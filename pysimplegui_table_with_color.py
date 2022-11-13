import PySimpleGUI as sg

fix_table_color = """
ttk::style map Treeview \
    -foreground {disabled SystemGrayText \
                 selected SystemHighlightText} \
    -background {disabled SystemButtonFace \
                 selected SystemHighlight}
"""


data = [
    ["AAA", 1, 1],
    ["BBB", 2, 1],
    ["CCC", 3, 1],
    ["DDD", 4, 0],
    ["EEE", 5, 0],
]

layout = [
        [sg.Table(
            key='-TABLE-',
            values=data,
            headings=["key", "value1", "value2"],
            row_colors=[(0, "red", "white"), (4, "white", "#aaaaff")],
            justification='left',
            max_col_width=50,
            auto_size_columns=False,
            background_color='#aaaaaa',
            alternating_row_color='#888888',
            )],
        [sg.Button("Exit", key="-EXIT-")],
    ]