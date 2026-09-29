
import json
import tkinter as tk
import tkinter.ttk as ttk


def test(to, title, body, option):
    print(to)
    print(title)
    print(body)
    print(option)




def count_characters(text):
    count = 0
    for char in text:
        if ord(char) < 128:  # ASCII文字（半角）の場合
            count += 1
        else:  # ASCII文字以外（全角）の場合
            count += 2
    return count



def main():

    # JSONファイルのパス
    file_path = 'tkinter_trial.json'

    # JSONファイルを読み込んでデータをロード
    with open(file_path, 'r', encoding="utf-8") as file:
        conf_dict = json.load(file)

    # ウィンドウの作成と、Tkinterオブジェクトの取得
    window = tk.Tk()

    # ウィンドウのサイズと位置を設定
    width   = 500   # 横幅
    height  = 400   # 高さ
    xPos    = 500   # X座標
    yPos    = 300   # Y座標
    window.geometry(f"{width}x{height}+{xPos}+{yPos}")
    
    # ウィンドウにタイトルを設定
    window.title("Tkinterを使ってみましょう！！")
    grid_size_x=20
    grid_size_y=30
    message_width = 10 * grid_size_x

    
    # frame
    frame_for_start = tk.Frame(window,height=100, width=400, pady=10, padx=10)


    x_offset = 100
    text="勤務場所"
    label = tk.Label(window, text=text)
    label.place(x=x_offset, y=grid_size_y*0)
    x_offset = message_width #count_characters(text) * grid_size_x
    pass
    # ラジオボタン
    start_radio_button_list = ["出社", "在宅"]
    tk_start_radio_button_list = []
    start_var = tk.StringVar(value=start_radio_button_list[0])

    for i, radio_buttton in enumerate(start_radio_button_list):
        tk_start_radio_button = tk.Radiobutton(window, text=radio_buttton,variable=start_var, value=radio_buttton)
        tk_start_radio_button.place(x=x_offset, y=grid_size_y*0)
        tk_start_radio_button_list.append(tk_start_radio_button)
        width  = count_characters(radio_buttton) * grid_size_x
        x_offset += width

    x_offset = 100
    text="明日の予定"
    label = tk.Label(window, text=text)
    label.place(x=x_offset, y=grid_size_y*2)
    x_offset = message_width #count_characters(text) * grid_size_x
    pass
    # ラジオボタン
    radio_button_list = ["出社", "在宅"]
    tk_radio_button_list = []
    var = tk.StringVar(value=radio_button_list[0])

    for i, radio_buttton in enumerate(radio_button_list):
        tk_radio_button = tk.Radiobutton(window, text=radio_buttton,variable=var, value=radio_buttton)
        tk_radio_button.place(x=x_offset, y=grid_size_y*3)
        tk_radio_button_list.append(tk_radio_button)
        width  = count_characters(radio_buttton) * grid_size_x
        x_offset += width




    
    button_list = []
    for conf in conf_dict:
        hoge = tk.Button(window, text=conf["Name"], command=lambda conf=conf:test(
            to=conf["宛先"],
            title=conf["件名"],
            body=conf["本文"],
            option=var.get()
            ))
        pass
        button_list.append(hoge)
        pass
    
    for i, button in enumerate(button_list):
        button.place(x=10, y=grid_size_y*i)
        pass




    # ウィンドウのループ処理
    window.mainloop()
    pass



if __name__ == "__main__":
    main()
