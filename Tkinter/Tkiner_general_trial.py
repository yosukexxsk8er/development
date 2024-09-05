import json
import tkinter as tk
import tkinter.ttk as ttk



class LogWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Log Window")
        self.log_frame = tk.Frame(self.master)
        self.log_frame.pack()
        self.text = tk.Text(self.log_frame)
        self.text.pack()
        self.master = master
        self.master.title("Log Window")
        self.text = tk.Text(self.master)
        self.log_frame.config(height=10)  # 高さを 10 行に設定
        self.text.pack()

    def log_message(self, message):
        self.text.insert(tk.END, message + "\n")
        self.text.see(tk.END)

        
class InputForm:
    def __init__(self, master,wraplength,width):
        self.master = master
        self.master.title("Input Form")

        
        # 任意の文字列を表示するラベルを作成（テキストボックスの直前）
        self.label = tk.Label(self.master, text="\n任意の文字列をここに表示します")
        self.label.pack()


        # テキスト入力フィールドの作成
        self.text_box = tk.Text(master, height=5, width=100)  # 5行の入力フォーム
        self.text_box.pack()

        # 送信ボタンの作成
        self.button = tk.Button(self.master, text="Submit", command=self.submit)
        self.button.pack()

    def submit(self):
        # 入力テキストフォームの内容を取得
        name = self.text_box.get("1.0", tk.END)  
        print("Name:", name)



class AppBase:
    def __init__(self,name,log_window,input_form):
        self.name = name
        self.log_window = log_window
        self.input_form = input_form
        pass

    def gen_button(self,window):
        self.button = tk.Button(window, text=self.name, command=self.common_func)

    def common_func(self):
        print(f"{self.name} was pushed!")
        match self.name:
            case "開始":
                print("開始します。")
                self.log_window.log_message("開始します。")
            case "終了":
                print("終了します。")
                self.log_window.log_message("終了します。")

        return

    def place(self,x,y):
        self.button.place(x=x, y=y)
        return


def main():

    # JSONファイルのパス
    file_path = 'tkinter_trial.json'

    # JSONファイルを読み込んでデータをロード
    with open(file_path, 'r', encoding="utf-8") as file:
        conf_dict = json.load(file)

    # ウィンドウの作成と、Tkinterオブジェクトの取得
    window = tk.Tk()
    log_window = LogWindow(window)
    input_form = InputForm(window,wraplength=5,width=30)


    # ウィンドウのサイズと位置を設定
    width   = 500   # 横幅
    height  = 900   # 高さ
    xPos    = 500   # X座標
    yPos    = 300   # Y座標
    window.geometry(f"{width}x{height}+{xPos}+{yPos}")
    
    # ウィンドウにタイトルを設定
    window.title("Tkinterを使ってみましょう！！")
    grid_size_x=20
    grid_size_y=30
    message_width = 10 * grid_size_x

    

    app_list = []
    for conf in conf_dict:
        app = AppBase(conf["Name"],log_window,input_form)
        app.gen_button(window)
        app_list.append(app)
        pass
    

    for i, app in enumerate(app_list):
        app.place(x=10, y=grid_size_y*i)
        pass


    # ウィンドウのループ処理
    window.mainloop()
    pass



if __name__ == "__main__":
    main()
