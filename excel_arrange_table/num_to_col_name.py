
def num_to_col_name(num):
    """数値をExcelの列名（アルファベット）に変換する関数"""
    col_name = ''
    num = num -1
    while num >= 0:
        col_name = chr(num % 26 + 65) + col_name
        num = num // 26 - 1
    return col_name

