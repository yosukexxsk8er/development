import os
import tkinter as tk
from tkinter import ttk


class Tinker_sub:
    def __init__(self):
        self.window = tk.Tk()
        self.dropdown_dict = {}
        self.button_dict = {}
        self.log = {}
        #self.scrollbar = tk.Scrollbar(self.window)
        #self.scrollbar.grid()

    def add_dropdown(self, name, choice_list:list, padx, pady, row, column, columnspan=1):
        self.dropdown_dict[name] = ttk.Combobox(
            self.window,
            textvariable=tk.StringVar(),
            values=choice_list,
            state="readonly")
        self.dropdown_dict[name].grid(padx=padx, pady=pady, row=row, column=column, columnspan=columnspan)

    def add_button(self, func, name, padx, pady, row, column, columnspan=1):
        # 更新ボタンを作成してドロップダウンリストを更新する
        self.button_dict[name] = tk.Button(
            self.window,
            text=name,
            command=func)
        self.button_dict[name].grid(padx=padx, pady=pady, row=row, column=column,columnspan=columnspan)

    def add_log_area(self, height, width, padx, pady, row, column, columnspan=1):
        self.log_area = tk.Text(
            self.window,
            wrap="word",
            height=height,
            width=width)
            #yscrollcommand=self.scrollbar.set)
        self.log_area.grid(padx=padx, pady=pady, row=row, column=column, columnspan=columnspan)

class Tinker_Top(Tinker_sub):
    def __init__(self, title="No Title Name"):
        super().__init__()
        self.window.title(title)
        pass

    def mainloop(self):
        self.window.mainloop()

    def my_print(self):
        for key in self.dropdown_dict.keys():
            print(f'{key}:{self.dropdown_dict[key]["values"]}')



def main():
    tinker_top  = Tinker_Top()
    tinker_top.add_dropdown("hoge", choice_list=["A", "B"], padx=0, pady=0, row=0, column=0)
    tinker_top.add_button(name="hoge", func=tinker_top.my_print, padx=0, pady=5, row=0, column=1)
    tinker_top.add_log_area(height=10, width=50, padx=0, pady=10, row=1, column=0, columnspan=5)

    tinker_top.mainloop()




if __name__ == "__main__":
    main()
