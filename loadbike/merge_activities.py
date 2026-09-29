import json
import pandas as pd



def merge_activities(files,dir="./", save_name=None):
    dfs = []
    col_from = "アクティビティタイプ"
    col_to   = "距離"
    col_date = "日付"
    col_title = "タイトル"
    col_dist = "距離"
    for file in files:
        print(f'Read {dir}{file}, and merging....')
        dfs.append(pd.read_csv(dir + file))
    df = pd.concat(dfs)
    df = df.loc[:,f"{col_from}":f"{col_to}"]
    df = df.drop_duplicates().sort_values(by=f"{col_date}",ascending=False)

    # 日付をdatetime型に変換
    df[col_date] = pd.to_datetime(df[col_date])

    # 2分以内かつタイトル・距離が同じものを重複とみなして削除
    df = df.sort_values(by=[col_title, col_dist, col_date])
    mask = [True]  # 最初の行は残す
    for i in range(1, len(df)):
        prev = df.iloc[i-1]
        curr = df.iloc[i]
        # タイトル・距離が同じ、かつ日付が2分以内なら重複
        if (curr[col_title] == prev[col_title]) and (curr[col_dist] == prev[col_dist]):
            diff = abs((curr[col_date] - prev[col_date]).total_seconds())
            if diff <= 120:
                mask.append(False)
                continue
        mask.append(True)
    df = df[mask]

    df = df.sort_values(by=f"{col_date}",ascending=False)
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
