import os
import tkinter as tk
from tkinter import ttk


class Tinker_Top:
    def __init__(self, title="No Title Name"):
        self.window = tk.Tk()
        self.window.title(title)
        self.dropdown_dict = {}
        self.button_dict = {}
        pass

    def add_dropdown(self, name, choice_list:list):
        self.dropdown_dict[name] = {}
        self.dropdown_dict[name]["choice_list"] = choice_list
        self.dropdown_dict[name] = ttk.Combobox(
            self.window,
            textvariable=tk.StringVar(),
            values=self.dropdown_dict[name]["choice_list"],
            state="readonly")

    def add_button(self, name="更新", func):
        # 更新ボタンを作成してドロップダウンリストを更新する
        update_button = tk.Button(
            self.window,
            text=name,
            command=func)
        update_button.pack(padx=10, pady=5)



class MyDropdown:
    def __init__(self, dir_path_to_dropdown_list):
        self.dir_path_to_dropdown_list = dir_path_to_dropdown_list
        self.dropdown = None
        self.text_area = None
        pass

    def add_dropdown(self, dropdown):
        self.dropdown = dropdown

    def add_text_area(self, text_area):
        self.text_area = text_area

    def add_log_area(self, log_area):
        self.log_area = log_area

    def update_dropdown(self):
        """ドロップダウンリストを更新する関数"""
        files = self.get_files_in_folder(self.dir_path_to_dropdown_list, update=True)
        self.dropdown["values"] = files

    def get_files_in_folder(self, update=True):
        if(update is True or self.dir_path_to_dropdown_list is None):
            """指定されたフォルダ内のファイル一覧を取得する関数"""
            self.files = []
            for f in os.listdir(self.dir_path_to_dropdown_list):
                full_path = os.path.join(self.dir_path_to_dropdown_list, f)
                if os.path.isfile(full_path):
                    self.files.append(f)
        return self.files

        return self.files
    
    def get_selected_value(self):
        selected_value = self.dropdown.get()
        print(f'selected_value is {selected_value}')

    def display_file(self):
        selected_value = self.dropdown.get()
        self.log_area.insert(tk.END, f'"{selected_value}" を開きます。\n')
        with open(f'{self.dir_path_to_dropdown_list}/{selected_value}', "r") as file:
            content = file.read()
            self.text_area.delete("1.0", tk.END)  # テキストエリアをクリア
            self.text_area.insert(tk.END, content)  # テキストエリアにファイル内容を挿入
    
    def on_scroll(self,*args):
        self.text_area.yview(*args)
        self.log_area.yview(*args)


def on_scroll(text_area1, text_area2, *args):
    text_area1.yview(*args)
    text_area2.yview(*args)


def main():
    # Tkinterウィンドウの作成
    window = tk.Tk()
    window.title("ファイル選択")

    # フォルダ内のファイル一覧を取得して初期選択肢とする
    folder_path = r"C:\Work\FT232H\pyftdi-0.54.0\pyftdi\bin"  # 対象のフォルダパスを指定してください
    myDropdown = MyDropdown(folder_path)

    # ドロップダウンリスト（コンボボックス）の作成
    selected_file = tk.StringVar()
    dropdown = ttk.Combobox(window, textvariable=selected_file, values=myDropdown.get_files_in_folder(), state="readonly")
    myDropdown.add_dropdown(dropdown)
    dropdown.pack(padx=10, pady=10)

    # 更新ボタンを作成してドロップダウンリストを更新する
    update_button = tk.Button(window, text="更新", command=myDropdown.update_dropdown)
    update_button.pack(padx=10, pady=5)

    
    # 選択された値を表示するボタンを作成
    show_value_button = tk.Button(window, text="選択された値を表示", command=myDropdown.get_selected_value)
    show_value_button.pack(padx=10, pady=5)


    # ボタンを作成してファイルを開く
    open_button = tk.Button(window, text="ファイルを開く", command=myDropdown.display_file)
    open_button.pack(padx=10, pady=10)

    
    # スクロールバーを作成
    scrollbar = tk.Scrollbar(window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


    # テキストエリアを作成してファイル内容を表示する
    text_area = tk.Text(window, wrap="word", height=20, width=50, yscrollcommand=scrollbar.set)
    text_area.pack(padx=10, pady=10)
    myDropdown.add_text_area(text_area)

    # ログ表示のためのテキストエリアを作成
    log_area = tk.Text(window, wrap="word", height=10, width=50, yscrollcommand=scrollbar.set)
    log_area.pack(padx=10, pady=10)
    myDropdown.add_log_area(log_area)







    # ウィンドウの表示
    window.mainloop()
    pass


if __name__ == "__main__":
    main()


