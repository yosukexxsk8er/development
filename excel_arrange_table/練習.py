from openpyxl import Workbook
from openpyxl.drawing.image import Image
from openpyxl.styles import PatternFill, Font

import numpy as np
import os

from  excel_arrange_table.num_to_col_name import num_to_col_name

def arrange_img(img_path_table, worksheet):
    ws = worksheet
    i_col = 1
    i_row = 1
    col_padding_num = 1
    row_padding_num = 2
    cell_width  = 57
    cell_height = 170
    title_format = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
    title_font = Font(name="Meiryo", bold=True)

    for img_path_list in img_path_table:
        for img_path in img_path_list:
            # 画像を読み込む
            img = Image(img_path)
            cell_name = f"{num_to_col_name(i_col)}{i_row}"
            ws[cell_name] = f'{os.path.basename(img_path)}'
            ws[cell_name].fill = title_format
            ws[cell_name].font = title_font 

            cell_name = f"{num_to_col_name(i_col)}{i_row+1}"
            ws.column_dimensions[f'{num_to_col_name(i_col)}'].width = cell_width
            ws.row_dimensions[i_row+1].height = cell_height
            ws.add_image(img, cell_name)
            i_col += col_padding_num
        i_row += row_padding_num
        i_col = 1


def main():
    wb = Workbook()
    ws = wb.active

    pattern_list = ["CLK", "PRBS9", "MCP-IR"]
    Preset_list = list(np.char.add("P", np.arange(10).astype(str)))
    dir = "outputs"
    
    # 2次元配列で画像ファイルパスの一覧を作成
    img_path_table = []
    for preset in Preset_list:
        img_path_list = []
        for pattern in pattern_list:
            img_path_list.append(f'{dir}/{pattern}_{preset}.png')
        img_path_table.append(img_path_list)
            

    arrange_img(img_path_table=img_path_table, worksheet=ws)
    pass

    pass
    output_file = "output.xlsx"
    wb.save(output_file)



if __name__ == "__main__":
    main()
