import openpyxl
import re
import numpy as np
import itertools
import pandas as pd


def expand_to_list(str_or_other):
    """ 文字列をルールに従って展開(可能なら)し、リストで返す

    Args:
        str_or_other (_type_): _description_

    Returns:
        _type_: _description_
    """
    
    if(str_or_other=="None"):
        return [""]
    # 100 to 200 by 50 の形式であれば展開する。前提としてそれぞれが整数
    m = re.search(r"([\d]+) to ([\d]+) by ([\d]+)", str_or_other)
    if(m):
        start  = int(m.group(1))
        end    = int(m.group(2))
        delta  = int(m.group(3))
        return list(range(start, end+delta, delta))
    else:
        return str_or_other.split(",")

def df_swapped_to_excel(df):
    """ df の行と列を入れ替え、エクセルに保存

    Args:
        df (_type_): データフレーム
    """
    matrix = df.to_numpy()
    # 行列を入れ替える
    transposed_matrix = np.transpose(matrix)
    # Excelファイルを作成して行列を書き込む
    wb = openpyxl.Workbook()
    ws = wb.active
    # 行列をExcelに書き込む
    for row in transposed_matrix:
        ws.append(row.tolist())
    # Excelファイルを保存
    wb.save('excel_file.xlsx')

def main():
    workbook="conditions.xlsx"
    worksheet="Sheet1"
    wb = openpyxl.load_workbook(workbook)
    ws = wb[worksheet]

    expanded_table_list = []
    #ワークシートを1列ずつ読み込み
    for i_col, cols in enumerate(ws.iter_cols()):
        if(i_col==0):
            continue
        expanded_table = []
        for i_row, cell in enumerate(cols):
            if(i_row==0):
                continue
            #行頭、行末の空白削除、連続する空白を1つに置換
            value = re.sub(r'\s+', ' ', str(cell.value).lstrip().rstrip() )
            # 値を展開した結果(配列)を別の配列に格納
            values = expand_to_list(value)
            expanded_table.append(values)
        expanded_table_list.append(expanded_table)
        
    df_list = []
    test_no = 1
    for expanded_table in expanded_table_list:
        # 1列分のデータから全組み合わせを生成し、組み合わせを1つずつデータフレームを格納
        for params in list(itertools.product(*expanded_table)):
            params = list(params) #tuple をリストに変更
            params[0] = test_no # No は新規に振り直し
            #テスト条件1つを１つのデータフレームとして保存
            df_sub = pd.DataFrame([params], columns=["no", "vamp", "hoge", "preset"])
            #そのデータフレームをリストに格納
            df_list.append(df_sub)
            test_no += 1

    #リストに格納したデータフレームを結合
    df = pd.concat(df_list)
    df_swapped_to_excel(df)

    #生成したテストの本数や所要時間(概算)を表示
    total_test_number = len(df)
    run_time_per_a_test = 4
    tat_hour = (run_time_per_a_test * total_test_number)//60
    tat_min  = (run_time_per_a_test * total_test_number)%60
    print(f'生成された組合せ数は {total_test_number} でした。')
    print(f'{tat_hour}時間{tat_min}分かかる見込みです。({run_time_per_a_test}分/本で計算)')
    pass
    



if __name__ == "__main__":
    main()



