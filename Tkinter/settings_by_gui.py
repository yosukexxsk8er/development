import json
import customtkinter as ctk
from tkinter import filedialog

def on_select(event, combo):
    selected_value = combo.get()
    print(f"選択された値: {selected_value}")

def load_json_file(file_path, combos, labels):
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)
        for i, (combo, label) in enumerate(zip(combos,labels)):
            options = data[i]["options"]
            combo.configure(values=options)
            combo.set(options[0])

def main():
    # メインウィンドウの作成
    root = ctk.CTk()
    root.title("ドロップダウンリストのウィンドウ")
    root.geometry("400x300")
    root.resizable(False, False)

    # プルダウンリストを格納するリスト
    combos = []
    labels = []

    # 「ロード」ボタンのクリックイベントの処理
    def on_load_click():
        file_path = filedialog.askopenfilename(filetypes=[("JSONファイル", "*.json")])
        if file_path:
            load_json_file(file_path, combos, labels)

    # ボタンを配置する
    load_button = ctk.CTkButton(root, text="ロード", command=on_load_click)
    load_button.grid(row=0, column=0, padx=10, pady=5)

    # JSONファイルからデータを読み込む
    with open("data.json", encoding="utf-8") as f:
        data = json.load(f)

    for i, item in enumerate(data):
        # テキストの表示
        label = ctk.CTkLabel(root, text=item["label"])
        label.grid(row=i+1, column=0, padx=10, pady=5)
        labels.append(label)

        # プルダウンリストの作成
        options = item["options"]
        combo = ctk.CTkComboBox(root, values=options)
        combo.grid(row=i+1, column=1, padx=10, pady=5)

        # プルダウンリストの初期値
        combo.set(options[0])

        # 選択時のイベントハンドラの設定
        combo.bind("<<ComboboxSelected>>", lambda event, combo=combo: on_select(event, combo))

        # プルダウンリストをリストに追加
        combos.append(combo)

    # 任意の文字列を表示するパーツ
    selected_text_label = ctk.CTkLabel(root, text="")
    selected_text_label.grid(row=len(data)+1, column=0, columnspan=2, padx=10, pady=5)

    # プルダウンリストの選択肢が変更されたときに、選択された値を表示する
    def update_selected_text():
        selected_values = [combo.get() for combo in combos]
        selected_text_label.config(text="\n".join(selected_values))

    for combo in combos:
        combo.bind("<<ComboboxSelected>>", update_selected_text)

    # ウィンドウの表示
    root.mainloop()

if __name__ == "__main__":
    main()