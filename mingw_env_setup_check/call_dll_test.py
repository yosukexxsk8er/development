import ctypes

# DLLをロード
mydll = ctypes.CDLL('./dll_test.dll')  # DLLのパスを指定

# 関数の引数と戻り値の型を指定
mydll.add.argtypes = (ctypes.c_int, ctypes.c_int)  # 引数: 整数型2つ
mydll.add.restype = ctypes.c_int                  # 戻り値: 整数型

# 足し算関数を呼び出し
result = mydll.add(15, 25)
print(f"Result of add: {result}")

# メッセージ出力関数を呼び出し
mydll.print_message.argtypes = (ctypes.c_char_p,)  # 引数: 文字列
mydll.print_message.restype = None                # 戻り値: なし

message = b"Hello from Python using MinGW DLL!"  # バイト列に変換
mydll.print_message(message)
