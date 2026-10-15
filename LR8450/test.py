from DataLoggerLR8450 import DataLoggerLR8450

lr = DataLoggerLR8450('192.168.0.3', channels=['U1-1'], verbose=0)  # USB なら '/dev/ttyACM0'

def try_cmd(cmd, is_query=True):
    lr.query('*ESR?')                      # イベントレジスタを読んでクリア
    if is_query:
        ret = lr.query(cmd)
    else:
        lr.write(cmd); ret = '(no response)'
    esr = lr.query('*ESR?')                # bit5(32)=コマンドエラー, bit4(16)=実行エラー
    print('{:40s} -> {!r:30s} ESR={}'.format(cmd, ret, esr))

# 現在値の取り込み → 読み出し（LR8400 系ロガーで使われる形式の候補）
try_cmd(':MEMory:GETReal', is_query=False)
for ch in ['UNIT1_CH1', 'U1_1', 'CH1_1', 'U1-1', 'CH1']:
    try_cmd(':MEMory:VREAL? {}'.format(ch))

# 前回クラスに入れた候補
try_cmd(':MEMory:VDATa? UNIT1_CH1')

# エラー問い合わせコマンドの有無
try_cmd(':ERRor?')
