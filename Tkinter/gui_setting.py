import json
import customtkinter as ctk
from tkinter import filedialog, messagebox

# サンプル関数の定義
def hoge():
    messagebox.showinfo("実行", "hoge 関数が実行されました")

# JSONファイルを読み込む関数
def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load JSON file: {e}")
        return None

# ドロップダウンリストを作成する関数
def create_dropdowns(root, data):
    dropdowns = {}
    for index, (key, values) in enumerate(data['dropdown'].items()):
        label = ctk.CTkLabel(root, text=key)
        label.grid(row=index, column=0, padx=10, pady=5)

        dropdown = ctk.CTkComboBox(root, values=values, width=200)  # 幅を2倍に設定
        dropdown.grid(row=index, column=1, padx=10, pady=5)
        dropdowns[key] = dropdown
    return dropdowns

# ボタンを作成する関数
def create_buttons(root, data, start_row):
    buttons = {}
    for index, (key, func_name) in enumerate(data['button'].items()):
        button = ctk.CTkButton(root, text=key, command=globals()[func_name])
        button.grid(row=start_row + index, column=0, columnspan=2, padx=10, pady=5)
        buttons[key] = button
    return buttons

# ファイルを選択する関数
def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        file_entry.delete(0, ctk.END)
        file_entry.insert(0, file_path)

# ドロップダウンリストの値を更新する関数
def load_settings():
    file_path = file_entry.get()
    if not file_path:
        messagebox.showwarning("Warning", "Please select a file first.")
        return
    
    settings = load_json(file_path)
    if settings:
        for key, value in settings.items():
            if key in dropdowns:
                dropdowns[key].set(value)

def main():
    # JSONファイルを読み込む
    file_path = 'gui_objects.json'
    data = load_json(file_path)

    if data is None:
        return

    # CustomTkinter ウィンドウの設定
    ctk.set_appearance_mode("dark")  # Appearance mode
    ctk.set_default_color_theme("dark-blue")  # Color theme

    root = ctk.CTk()  # Create window
    root.title("Dropdown GUI")

    global dropdowns
    dropdowns = create_dropdowns(root, data)

    # 「過去ログ」ラベルの作成と配置
    log_label = ctk.CTkLabel(root, text="過去ログ")
    log_label.grid(row=len(data['dropdown']), column=0, padx=10, pady=10)

    global file_entry
    file_entry = ctk.CTkEntry(root, width=250)
    file_entry.grid(row=len(data['dropdown']), column=1, padx=10, pady=10)

    browse_button = ctk.CTkButton(root, text="参照", command=browse_file, width=75)  # 横幅を半分に設定
    browse_button.grid(row=len(data['dropdown']), column=2, padx=5, pady=10)

    load_button = ctk.CTkButton(root, text="ロード", command=load_settings, width=75)  # 横幅を半分に設定
    load_button.grid(row=len(data['dropdown']), column=3, padx=5, pady=10)

    # ロードボタンの直下にボタンを配置
    create_buttons(root, data, len(data['dropdown']) + 1)

    # ウィンドウサイズを設定
    total_rows = len(data['dropdown']) + 1 + len(data['button'])
    window_height = total_rows * 45  # 1行あたりの高さを45pxと仮定
    window_width = 600  # 横幅は固定
    root.geometry(f"{window_width}x{window_height}")

    root.mainloop()

if __name__ == "__main__":
    main()
