import json
import tkinter as tk

class LogWindow:
    def __init__(self, master):
        # ログ表示用のウィンドウを作成
        self.master = master

        # ログフレームとスクロールバー付きテキストウィジェットを作成
        self.log_frame = tk.Frame(self.master)

        self.text = tk.Text(self.log_frame, height=10)

        self.scrollbar = tk.Scrollbar(self.log_frame, command=self.text.yview)
        self.text.config(yscrollcommand=self.scrollbar.set)

    def pack(self):
        self.log_frame.pack(fill=tk.BOTH, expand=True)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def log_message(self, message):
        """ログメッセージを追加し、最新メッセージに自動スクロール"""
        self.text.insert(tk.END, message + "\n")
        self.text.see(tk.END)


class InputForm:
    def __init__(self, master):
        # 入力フォームのウィンドウを作成
        self.master = master

        # 任意のラベル（1行）とテキスト入力フィールドを作成
        self.label = tk.Label(self.master, text="任意の文字列をここに表示します")

        # テキスト入力フィールド
        self.text_box = tk.Text(self.master, height=5, width=50)  # 幅を50に設定

        # 送信ボタン
        self.button = tk.Button(self.master, text="Submit", command=self.submit)

    def pack(self):
        self.label.pack(pady=5)
        self.text_box.pack(pady=5)
        self.button.pack(pady=5)

    def submit(self):
        """テキストボックスの内容を取得して表示"""
        name = self.text_box.get("1.0", tk.END).strip()
        print("Name:", name)


class AppBase:
    def __init__(self, name, log_window, input_form):
        self.name = name
        self.log_window = log_window
        self.input_form = input_form

    def gen_button(self, window):
        """ウィンドウにボタンを生成"""
        self.button = tk.Button(window, text=self.name, command=self.common_func)

    def common_func(self):
        """ボタンが押されたときの共通処理"""
        print(f"{self.name} was pushed!")
        if self.name == "開始":
            print("開始します。")
            self.log_window.log_message("開始します。")
        elif self.name == "終了":
            print("終了します。")
            self.log_window.log_message("終了します。")

    def pack(self):
        """ボタンを順番にパック"""
        self.button.pack(pady=5)


def main():
    # JSONファイルのパス
    file_path = 'tkinter_trial.json'

    # JSONファイルを読み込み
    with open(file_path, 'r', encoding="utf-8") as file:
        conf_dict = json.load(file)

    # メインウィンドウの作成
    window = tk.Tk()
    window.geometry("400x600")  # 幅と高さを設定
    window.title("Tkinterを使ってみましょう！！")

    # ログウィンドウの作成
    log_window = LogWindow(window)

    # 入力フォームの作成
    input_form = InputForm(window)

    # ボタン生成および配置
    app_list = []
    for conf in conf_dict:
        app = AppBase(conf["Name"], log_window, input_form)
        app.gen_button(window)
        app.pack()
        app_list.append(app)

    input_form.pack()
    log_window.pack()

    # メインループ
    window.mainloop()


if __name__ == "__main__":
    main()
