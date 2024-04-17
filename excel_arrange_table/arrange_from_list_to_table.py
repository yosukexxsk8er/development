import openpyxl
import pandas as pd

def get_sample_table():
    workbook=r"C:\Work\GitLocals\development\conbination\excel_file.xlsx"
    worksheet="Sheet"
    wb = openpyxl.load_workbook(workbook)
    ws = wb[worksheet]

    expanded_table_list = []
    #ワークシートを1列ずつ読み込み
    key_list = []
    dict_list = []
    df_list = []
    for i_col, cols in enumerate(ws.iter_cols()):
        params = []
        dict = {}
        for i_row, cell in enumerate(cols):
            if(i_col==0):
                params.append(cell.value)
            else:
                dict[key_list[i_row]] = cell.value
        if(i_col==0):
            key_list = params
        else:
            dict_list.append(dict)

    for i, dict in enumerate(dict_list):
        dict_list[i]["ImgNameA"] = f'AAAA_{dict["No."]:04d}_{dict["Pattern"]}_{dict["preset"]}'
        dict_list[i]["ImgNameB"] = f'BBBB_{dict["No."]:04d}_{dict["Pattern"]}_{dict["preset"]}'
        dict_list[i]["ImgNameC"] = f'CCCC_{dict["No."]:04d}_{dict["Pattern"]}_{dict["preset"]}'
    df = pd.DataFrame(dict_list)

    return df
            
        
    pass


def main():
    df = get_sample_table()
    header_list = ["ImgNameA", "ImgNameB", "ImgNameC"]
    index  = "preset"
    table = []
    # 横方向はパターンを並べる
    # Vamp にバリエーションがあるなら、Vampを下方向に並べる
    # 上記がNoで、 PresetにバリエーションがあるならPresetを下方向に並べる


    #df_temp = df.query('Vamp!=9999')
    #df_temp = df.query('Pattern == "PRBS9" & Vamp==200')
    df_temp = df.query('Vamp==200')

    if(df_temp["Vamp"].nunique()!=1):
        header_to_sort = "Vamp"
    elif(df_temp["preset"].nunique()!=1):
        header_to_sort = "preset"
    else:
        header_to_sort = "Pattern"
    
    pattern_list = list(df_temp["Pattern"].unique())
    preset_list  = list(df_temp["preset"].unique())
    vamp_list    = list(df_temp["Vamp"].unique())

    header_list = ["ImgNameA", "ImgNameB", "ImgNameC"]

    for pattern in pattern_list:
        if(len(vamp_list)==1):
            #Preset を下方向に並べる
            print(f"Sheet:{pattern}-Each Preset({vamp_list[0]}mV)")
            value_table = []
            for index, s in df_temp.query('Pattern == @pattern').sort_values("preset").iterrows():
                value_list = []
                for header in header_list:
                    value_list.append(s[header])
                value_table.append(value_list)
            for value_list in value_table:
                print(", ".join(value_list))
            pass
        else:
            #Vamp を下方向に並べる, Preset事にシートを作る
            for preset in preset_list:
                print(f"Sheet:{pattern}-{preset}(Each Vdiff)")
                value_table = []
                for index, s in df_temp.query('Pattern == @pattern & preset == @preset').sort_values("Vamp").iterrows():
                    value_list = []
                    for header in header_list:
                        value_list.append(s[header])
                    value_table.append(value_list)
                for value_list in value_table:
                    print(", ".join(value_list))


    pass
        



if __name__ == "__main__":
    main()
