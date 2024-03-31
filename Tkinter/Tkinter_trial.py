
import json
import tkinter

def test(to, title, body):
    print(to)
    print(title)
    print(body)

def main():

    # JSONファイルのパス
    file_path = 'tkinter_trial.json'

    # JSONファイルを読み込んでデータをロード
    with open(file_path, 'r', encoding="utf-8") as file:
        conf_dict = json.load(file)

    # ウィンドウの作成と、Tkinterオブジェクトの取得
    window = tkinter.Tk()

    # ウィンドウのサイズと位置を設定
    width   = 500   # 横幅
    height  = 400   # 高さ
    xPos    = 500   # X座標
    yPos    = 300   # Y座標
    window.geometry(f"{width}x{height}+{xPos}+{yPos}")
    
    # ウィンドウにタイトルを設定
    window.title("Tkinterを使ってみましょう！！")

    
    button_list = []
    for conf in conf_dict:
        hoge = tkinter.Button(window, text=conf["Name"], command=lambda conf=conf:test(
            to=conf["宛先"],
            title=conf["件名"],
            body=conf["本文"],
            ))
        pass
        button_list.append(hoge)
        pass
    
    for button in button_list:
        button.pack(anchor='nw')
        pass

    options = ["オプション1", "オプション2", "オプション3"]
    vars_list = []
    for option in options:
        var = tkinter.IntVar()
        check_button = tkinter.Checkbutton(window, text=option, variable=var)
        check_button.pack(anchor='w')
        vars_list.append(var)




    # ウィンドウのループ処理
    window.mainloop()
    pass



if __name__ == "__main__":
    main()
