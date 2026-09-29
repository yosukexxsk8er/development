
import tkinter as tk

def main():

    root = tk.Tk()
    root.title("ボタン配置")

    left_frame = tk.Frame(root, bg="lightblue", padx=10, pady=10)
    right_frame = tk.Frame(root, bg="lightgreen", padx=10, pady=10)
    bottom_frame = tk.Frame(root, bg="lightyellow", padx=10, pady=10)

    left_frame.pack(side="left", fill="y", expand=True)
    right_frame.pack(side="left", fill="y", expand=True)
    bottom_frame.pack(fill="x", expand=True)




    button_left_list = []
    for i in range(10):
        button_left_list.append(tk.Button(left_frame, text=f"ボタン{i+1}"))

    button_right_list = []
    for i in range(10):
        button_right_list.append(tk.Button(right_frame, text=f"ボタン{i+1}"))

    button_bottom_list = []
    for i in range(10):
        button_bottom_list.append(tk.Button(bottom_frame, text=f"ボタン{i+1}"))

    button_left_list[2].pack(anchor="nw")
    button_left_list[3].pack(anchor="nw")
    button_left_list[4].pack(anchor="nw")
    button_left_list[5].pack(anchor="nw")
    button_left_list[6].pack(fill="both", anchor="nw", side="right")

    button_right_list[2].pack(anchor="nw")
    button_right_list[3].pack(anchor="nw")
    button_right_list[4].pack(anchor="nw")
    button_right_list[5].pack(anchor="nw")
    button_right_list[6].pack(fill="both", anchor="nw", side="right")

    button_bottom_list[2].pack(anchor="nw")
    button_bottom_list[3].pack(anchor="nw")
    button_bottom_list[4].pack(anchor="nw")
    button_bottom_list[5].pack(anchor="nw")
    button_bottom_list[6].pack(fill="both", anchor="nw", side="right")

    root.mainloop()




if __name__ == "__main__":
    main()
