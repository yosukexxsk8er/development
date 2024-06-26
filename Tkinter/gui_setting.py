import json
import customtkinter as ctk
from tkinter import filedialog, messagebox

class DropdownGUI:
    def __init__(self, root):
        self.root = root
        self.dropdown_data = None
        self.dropdowns = {}
        self.file_entry = None

        # JSONファイルを読み込む
        file_path = 'gui_objects.json'
        data = self.load_json(file_path)

        if data is None:
            return

        self.dropdown_data = data

        # CustomTkinter ウィンドウの設定
        ctk.set_appearance_mode("dark")  # 外観モードをダークに設定
        ctk.set_default_color_theme("dark-blue")  # カラーテーマをダークブルーに設定

        self.root.title("Dropdown GUI")
        self.create_widgets()  # ウィジェットを作成

    def load_json(self, file_path):
        """
        指定されたパスからJSONファイルを読み込み、その内容を返す。
        読み込みに失敗した場合、エラーメッセージを表示し、Noneを返す。
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load JSON file: {e}")
            return None

    def create_dropdowns(self):
        """
        JSONデータに基づいてドロップダウンリストを作成し、ウィンドウに配置する。
        作成したドロップダウンリストをself.dropdownsに保存する。
        """
        for index, (key, values) in enumerate(self.dropdown_data['dropdown'].items()):
            label = ctk.CTkLabel(self.root, text=key)
            label.grid(row=index, column=0, padx=10, pady=5)

            dropdown = ctk.CTkComboBox(self.root, values=values, width=200)
            dropdown.grid(row=index, column=1, padx=10, pady=5)
            self.dropdowns[key] = dropdown

    def create_buttons(self, start_row):
        """
        JSONデータに基づいてボタンを作成し、ウィンドウに配置する。
        ボタンは指定された行から順に配置される。
        """
        for index, (key, func_name) in enumerate(self.dropdown_data['button'].items()):
            button = ctk.CTkButton(self.root, text=key, command=getattr(self, func_name))
            button.grid(row=start_row + index, column=0, columnspan=2, padx=10, pady=5)

    def browse_file(self):
        """
        ファイルダイアログを開いてJSONファイルを選択し、
        選択されたファイルパスをファイル入力欄に表示する。
        """
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            self.file_entry.delete(0, ctk.END)
            self.file_entry.insert(0, file_path)

    def load_settings(self):
        """
        ファイル入力欄に指定されたパスからJSONファイルを読み込み、
        読み込んだデータに基づいてドロップダウンリストの値を更新する。
        """
        file_path = self.file_entry.get()
        if not file_path:
            messagebox.showwarning("Warning", "Please select a file first.")
            return

        settings = self.load_json(file_path)
        if settings:
            for key, value in settings.items():
                if key in self.dropdowns:
                    self.dropdowns[key].set(value)

    def hoge(self):
        """
        サンプルのメッセージボックスを表示する関数。
        """
        messagebox.showinfo("実行", "hoge 関数が実行されました")

    def create_widgets(self):
        """
        ウィジェットを作成し、ウィンドウに配置するメイン関数。
        ドロップダウンリスト、ラベル、ファイル入力欄、ボタンを配置する。
        """
        self.create_dropdowns()

        log_label = ctk.CTkLabel(self.root, text="過去ログ")
        log_label.grid(row=len(self.dropdown_data['dropdown']), column=0, padx=10, pady=10)

        self.file_entry = ctk.CTkEntry(self.root, width=250)
        self.file_entry.grid(row=len(self.dropdown_data['dropdown']), column=1, padx=10, pady=10)

        browse_button = ctk.CTkButton(self.root, text="参照", command=self.browse_file, width=75)
        browse_button.grid(row=len(self.dropdown_data['dropdown']), column=2, padx=5, pady=10)

        load_button = ctk.CTkButton(self.root, text="ロード", command=self.load_settings, width=75)
        load_button.grid(row=len(self.dropdown_data['dropdown']), column=3, padx=5, pady=10)

        self.create_buttons(len(self.dropdown_data['dropdown']) + 1)

        # ウィンドウのサイズを設定
        total_rows = len(self.dropdown_data['dropdown']) + 1 + len(self.dropdown_data['button'])
        window_height = total_rows * 45  # 1行あたりの高さを45pxと仮定
        window_width = 600  # 横幅は固定
        self.root.geometry(f"{window_width}x{window_height}")

def main():
    """
    アプリケーションを起動するメイン関数。
    """
    root = ctk.CTk()
    app = DropdownGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
