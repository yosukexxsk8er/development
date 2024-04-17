from openpyxl import Workbook
from openpyxl.drawing.image import Image
from openpyxl.styles import PatternFill, Font
import math

import numpy as np
import os

from  excel_arrange_table.num_to_col_name import num_to_col_name

def arrange_img(img_path_table, worksheet):
    """ table[n] の右方向に並べ、 table[n+1]は次の行に並べる
    画像の大きさに合わせてセルの大きさを変更し、
    1つのセルに1つの画像が収まるよう
    
    Args:
        img_path_table (_type_): 画像へのパスを格納した2次元配列
        worksheet (_type_): ワークシート
    """
    ws = worksheet
    i_col = 1
    i_row = 1
    col_padding_num = 1 #とある画像(の左上座標)と右隣の画像(の左上座標)の間隔
    row_padding_num = 2 #とある画像(の左上座標)と下の画像(の左上座標)の間隔
    margin = 1.01
    width_ratio_fom_img_to_cell  = ( 57 / 400) * margin # 過去の調整の結果から比率を算出
    height_ratio_fom_img_to_cell = (170 / 200) * margin # 過去の調整の結果から比率を算出
    cell_width  = math.ceil(Image(img_path_table[0][0]).width  *  width_ratio_fom_img_to_cell)  #400 -> 57
    cell_height = math.ceil(Image(img_path_table[0][0]).height *  height_ratio_fom_img_to_cell) #200 -> 170
    title_format = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
    title_font = Font(name="Meiryo", bold=True)

    for img_path_list in img_path_table:
        for img_path in img_path_list:
            # 画像を読み込む
            img = Image(img_path)
            cell_name = f"{num_to_col_name(i_col)}{i_row}"
            #ws.cell(row=4, column=1).value = '=HYPERLINK("https://www.amazon.co.jp/", "Amazon")'

            ws[cell_name] = f'=HYPERLINK("{img_path}","{os.path.basename(img_path)}")'
            ws[cell_name].fill = title_format
            ws[cell_name].font = title_font 

            cell_name = f"{num_to_col_name(i_col)}{i_row+1}"
            ws.column_dimensions[f'{num_to_col_name(i_col)}'].width = cell_width
            ws.row_dimensions[i_row+1].height = cell_height
            ws.add_image(img, cell_name)
            i_col += col_padding_num
            pass
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
