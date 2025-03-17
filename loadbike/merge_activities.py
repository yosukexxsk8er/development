import json
import pandas as pd



def merge_activities(files,dir="./", save_name=None):
    dfs = []
    #col_from = "Activity Type"
    #col_to   = "Distance"
    #col_date = "日付"
    col_from = "アクティビティタイプ"
    col_to   = "距離"
    col_date = "日付"
    for file in files:
        print(f'Read {dir}{file}, and merging....')
        dfs.append(pd.read_csv(dir + file))
    df = pd.concat(dfs)
    df = df.loc[:,f"{col_from}":f"{col_to}"]
    df = df.drop_duplicates().sort_values(by=f"{col_date}",ascending=False)
    if(save_name):
        df.to_csv(save_name,index=False)
        print(f'{save_name} was saved since file name as save was not specified.')
    else:
        print(f'Merged Dataframe was not saved as csv.')
    return df


def main():
    json_file="maintenance_note.json"
    with open(json_file, "r", encoding="utf-8_sig") as f:
        json_dict = json.load(f)
    
    files = json_dict["Activities"]
    #files.append("Book1.csv")
    #files.append("Book2.csv")
    #files.append("Activities (12).csv")
    #files.append("Activities (13).csv")
    df = merge_activities(files,"AAA.csv")
    print(df)

    pass



if __name__ == "__main__":
    main()
