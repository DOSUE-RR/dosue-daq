###########################################
# HIOKI Memory HiLogger LR8450 (LAN / USB) #
###########################################
# 使い方:
#   from DataLoggerLR8450 import DataLoggerLR8450
#   lr = DataLoggerLR8450('192.168.1.10', channels=['U1-1', 'U1-2', (2, 5)])  # LAN
#   lr = DataLoggerLR8450('/dev/ttyACM0', channels=['U1-1'])                  # USB (仮想COM)
#   values = lr.readValues()   # -> {'UNIT1_CH1': 23.4, 'UNIT1_CH2': ..., 'UNIT2_CH5': ...}
#
# ※ コマンド文字列 (CMD_*) は LR8450 の「通信コマンド取扱説明書」で要確認。
#    機器側の設定で LAN または USB の「通信コマンド」モードを有効にしておくこと。

import socket
import serial
from time import sleep


class DataLoggerLR8450Error(Exception):
  def __init__(self, message):
    self.msg = "DataLoggerLR8450Error: " + str(message)
    pass
  def __str__(self):
    return self.msg
  pass


class DataLoggerLR8450(object):

  TERM      = '\r\n'   # コマンド終端 / 応答終端
  TCP_PORT  = 8802     # HIOKI 機器の通信コマンド用ポート (既定値)
  BAUDRATE  = 9600     # USB は CDC (仮想COM) なのでボーレートは実質無視される

  # ---- 通信コマンド (マニュアルで要確認) ----
  CMD_IDN    = '*IDN?'
  CMD_HEADER = ':HEADer OFF'           # 応答にヘッダを付けない
  CMD_ERROR  = ':ERRor?'               # エラー番号の問い合わせ
  CMD_GETREAL = ':MEMory:GETReal;*OPC?'   # 取り込み完了まで待つ（応答 "1"）
  CMD_VALUE   = ':MEMory:VREAL? {ch}' # 指定チャンネルの現在値

  def __init__(self, devlocation, channels, verbose=0, timeout=2.0):
    self.devlocation = devlocation
    self.verbose     = verbose
    self.TIMEOUT     = timeout
    self.MAXREADLOOP = 100000  # max. loop in read()
    self.channels    = [self.chname(c) for c in channels]

    # LAN ('192.168.1.10' or '192.168.1.10:8802') か USB ('/dev/ttyACM0', 'COM3') かを判定
    self.isLAN = ('/' not in devlocation) and (not devlocation.upper().startswith('COM'))

    if self.isLAN:
      host, _, port = devlocation.partition(':')
      port = int(port) if port else self.TCP_PORT
      self.sock = socket.create_connection((host, port), timeout=self.TIMEOUT)
      self.ser  = None
    else:
      self.sock = None
      self.ser  = serial.Serial(self.devlocation,
              baudrate = self.BAUDRATE,
              timeout  = self.TIMEOUT,
              bytesize = serial.EIGHTBITS,
              parity   = serial.PARITY_NONE,
              stopbits = serial.STOPBITS_ONE,
              )
      self.ser.reset_input_buffer()
      self.ser.reset_output_buffer()
      pass

    if self.verbose > 0:
      print('devlocation = {}'.format(self.devlocation))
      print('interface   = {}'.format('LAN' if self.isLAN else 'USB'))
      print('channels    = {}'.format(self.channels))
      print('timeout     = {}'.format(self.TIMEOUT))
      pass

    self.write(self.CMD_HEADER)   # 応答からヘッダを外しておく
    pass

  def __del__(self):
    self.close()
    pass

  def close(self):
    if getattr(self, 'sock', None) is not None:
      self.sock.close(); self.sock = None
      pass
    if getattr(self, 'ser', None) is not None:
      self.ser.close(); self.ser = None
      pass
    pass

  # ---- チャンネル名の正規化 ----
  # 'U1-1', '1-1', 'UNIT1_CH1', (1, 1) などを全て 'UNIT1_CH1' 形式に揃える
  @staticmethod
  def chname(ch):
    if isinstance(ch, (tuple, list)) and len(ch) == 2:
      unit, num = ch
    else:
      s = str(ch).upper().replace('UNIT', '').replace('CH', '').replace('U', '')
      s = s.replace('_', '-')
      if '-' not in s:
        raise DataLoggerLR8450Error('Invalid channel specification: {}'.format(ch))
      unit, num = s.split('-')
      pass
    return 'CH{}_{}'.format(int(unit), int(num))

  # ---- 低レベル I/O ----
  def write(self, command):
    if self.verbose > 0: print('Write : {}'.format(repr(command)))
    data = (command + self.TERM).encode()
    if self.isLAN:
      self.sock.sendall(data)
    else:
      self.ser.write(data)
      pass
    return

  def read(self):
    # 終端 (\r\n) が来るまで読む
    buf = b''
    if self.verbose > 0: print('Read')
    for m in range(self.MAXREADLOOP):
      try:
        chunk = self.sock.recv(4096) if self.isLAN else self.ser.read(self.ser.in_waiting or 1)
      except socket.timeout:
        chunk = b''
        pass
      if len(chunk) == 0:
        break   # timeout
      buf += chunk
      if self.verbose > 1: print('read = {}'.format(repr(buf)))
      if buf.endswith(self.TERM.encode()):
        break
      pass
    return buf.decode(errors='replace').strip()

  def query(self, command):
    if not self.isLAN:
      self.ser.reset_input_buffer()
      self.ser.reset_output_buffer()
      pass
    self.write(command)
    ret = self.read()
    if ret == '':
      print('ERROR!! Could not read from LR8450! (Read failed)')
      print('        COMMAND = {}'.format(command))
      print('        Returning blank... ("")')
      pass
    return ret

  # ---- 高レベル ----
  def getIDN(self):
    return self.query(self.CMD_IDN)

  def getError(self):
    ret = self.query(self.CMD_ERROR)
    if ret == '':
      return 'ReadError '
    try:
      code = int(ret.split(',')[0])
    except ValueError:
      return 'ParseError({}) '.format(ret)
    return '' if code == 0 else 'Error{} '.format(code)

  def readValue(self, ch):
    ch  = self.chname(ch)
    ret = self.query(self.CMD_VALUE.format(ch=ch))
    if self.verbose > 0: print('return   = {}'.format(ret))
    try:
      value = float(ret.split(',')[-1])
    except ValueError:
      # 'OVER', '+OVER', '-OVER', 'BURNOUT' などは数値化できない
      print('WARNING!! Non-numeric value from LR8450 ({}): {}'.format(ch, ret))
      value = float('nan')
      pass
    if self.verbose > 0: print('{} = {}'.format(ch, value))
    return value

  def readValues(self, channels=None):
    chs = self.channels if channels is None else [self.chname(c) for c in channels]
    self.query(self.CMD_GETREAL)              # 一斉取り込み
    return {ch: self.readValue(ch) for ch in chs}


if __name__ == '__main__':
  import sys
  dev = sys.argv[1] if len(sys.argv) > 1 else '192.168.1.10'
  lr  = DataLoggerLR8450(dev, channels=['U1-1', 'U1-2'], verbose=1)
  print(lr.getIDN())
  while True:
    print(lr.readValues())
    sleep(1)
    pass
  pass
