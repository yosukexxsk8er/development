import markdown
from bs4 import BeautifulSoup
from dataclasses import dataclass


def main():
    with open ("sendmail.md", "r", encoding="utf-8") as f:
        md_text = f.read()
        html = markdown.markdown(md_text)

    #print(html)
    headline_table = Table(border="solid 1px")

    table = [["xxxx", "yyyy"], ["zzzz", "vvvv"]]

    html =  ""
    html += style("td", border="solid 0px")
    html += style("th", border="solid 0px")


    table_style = StyleProperty(font_size="large", background_color="yellow")

    html += headline_table.start(style=StyleProperty(background_color="gray", width="100px", text_align="center"))
    html += headline_table.add_row(["aaaaa"])
    html += headline_table.start()
    html += headline_table.start_row(style=StyleProperty(background="blue"))
    html += headline_table.add_cell("aaaa", width="100px", header=True )
    html += headline_table.add_cell("bbbb", width="auto")
    html += headline_table.add_cell(["abc", "edf"], width="auto")
    html += headline_table.end_row()
    html += headline_table.start_row()
    html += headline_table.add_cell("cccc" , header=True)
    html += headline_table.add_cell("dddd", style=table_style )
    html += headline_table.end_row()
    html += headline_table.end()

    html += headline_table.add_table(table, table_style=table_style)

    with open ("test2.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(table_style.add())



@dataclass
class StyleProperty:
    #テキスト・フォント	適用対象	継承
    font:str=None            # フォント関連をまとめて指定	全ての要素	する
    font_size:str=None       # フォントのサイズ	全ての要素	する
    font_weight:str=None     # フォントの太さ	全ての要素	する
    font_style:str=None      # フォントのスタイル	全ての要素	する
    font_family:str=None     # フォントの種類	全ての要素	する
    font_variant:str=None    # スモールキャピタル	全ての要素	する
    text_align:str=None      # 水平方向の表示位置	ブロックレベル要素	する
    vertical_align:str=None  # 垂直方向の表示位置	インライン要素、th要素、td要素	しない
    line_height:str=None     # 行の高さ	全ての要素	する
    text_decoration:str=None # 文字の装飾	全ての要素	しない
    text_indent:str=None     # 1行目の字下げ	ブロックレベル要素	する
    text_transform:str=None  # 大文字と小文字の変換	全ての要素	する
    letter_spacing:str=None  # 文字の間隔	全ての要素	する
    word_spacing:str=None    # 単語の間隔	全ての要素	する
    white_space:str=None     # 改行・スペース・タブの扱い	全ての要素	する
    #色=None・背景	適用対象	継承
    color:str=None                 # 文字色	全ての要素	する
    background:str=None            # 背景関連をまとめて指定	全ての要素	しない
    background_color:str="transparent"      # 背景色	全ての要素	しない
    background_image:str=None      # 背景画像	全ての要素	しない
    background_repeat:str=None     # 背景画像の並び方	全ての要素	しない
    background_position:str=None   # 背景画像の表示位置	ブロックレベル要素、置換要素	しない
    background_attachment:str=None # 背景画像の固定表示	全ての要素	しない
    #幅=None・高さ	適用対象	継承
    width:str=None      # 内容領域の幅	全ての要素 （非置換インライン要素、tr要素、thead要素、tfoot要素、tbody要素を除く）	しない
    height:str=None     # 内容領域の高さ	全ての要素 （非置換インライン要素、colgroup要素、col要素を除く）	しない
    max_width:str=None  # 最大の幅	全ての要素 （非置換インライン要素、表関連要素を除く）	しない
    min_width:str=None  # 最小の幅	全ての要素 （非置換インライン要素、表関連要素を除く）	しない
    max_height:str=None # 最大の高さ	全ての要素 （非置換インライン要素、表関連要素を除く）	しない
    min_height:str=None # 最小の高さ	全ての要素 （非置換インライン要素、表関連要素を除く）	しない
    #マージン=None・パディング	適用対象	継承
    margin:str=None          # マージンをまとめて指定	全ての要素 （table要素、caption要素以外の表関連要素を除く）	しない
    m_argin_top:str=None     # _
    m_argin_right:str=None   # _
    m_argin_bottom:str=None  # _
    m_argin_left:str=None    # 上下左右のマージン	全ての要素 （table要素、caption要素以外の表関連要素を除く）	しない
    p_adding:str=None        # パディングをまとめて指定	全ての要素 （tr要素、thead要素、tfoot要素、tbody要素、col要素、colgroup要素を除く）	しない
    p_adding_top:str=None    # _
    p_adding_right:str=None  # _
    p_adding_bottom:str=None # _
    p_adding_left:str=None   # 上下左右のパディング	全ての要素 （tr要素、thead要素、tfoot要素、tbody要素、col要素、colgroup要素を除く）	しない
    #境界線=None	適用対象	継承
    border:str=None              # 境界線関連をまとめて指定	全ての要素	しない
    border_top:str=None          # _
    border_right:str=None        # _
    border_bottom:str=None       # _
    border_left:str=None         # 上下左右の境界線	全ての要素	しない
    border_width:str=None        # 境界線の太さをまとめて指定	全ての要素	しない
    border_top_width:str=None    # _
    border_right_width:str=None  # _
    border_bottom_width:str=None # _
    border_left_width:str=None   # 上下左右の境界線の太さ	全ての要素	しない
    border_color:str=None        # 境界線の色をまとめて指定	全ての要素	しない
    border_top_color:str=None    # _
    border_right_color:str=None  # _
    border_bottom_color:str=None # _
    border_left_color:str=None   # 上下左右の境界線の色	全ての要素	しない
    border_style:str=None        # 境界線のスタイルをまとめて指定	全ての要素	しない
    border_top_style:str=None    # _
    border_right_style:str=None  # _
    border_bottom_style:str=None # _
    border_left_style:str=None   # 上下左右の境界線のスタイル	全ての要素	しない
    #表示=None・配置	適用対象	継承
    overflow:str=None     # はみ出た部分の表示方法	ブロックレベル要素、置換要素	しない
    display:str=None      # 表示形式	全ての要素	しない
    visibility:str=None   # 表示と非表示	全ての要素	する
    clip:str=None         # 切り抜き	絶対位置決めされた要素	しない
    float:str=None        # フロート（浮動化）	全ての要素 （絶対位置決めされた要素、生成内容を除く）	しない
    clear:str=None        # 回り込みの解除	ブロックレベル要素	しない
    position:str=None     # 配置方法	全ての要素 （生成内容を除く）	しない
    top:str=None          # 上からの距離	位置決めされた要素	しない
    right:str=None        # 右からの距離	位置決めされた要素	しない
    bottom:str=None       # 下からの距離	位置決めされた要素	しない
    left:str=None         # 左からの距離	位置決めされた要素	しない
    z_index:str=None      # 重なりの順序	位置決めされた要素	しない
    direction:str=None    # 基本書字方向	全ての要素	する
    unicode_bidi:str=None # 書字方向の組み込みと上書き	全ての要素	しない
    #リスト=None	適用対象	継承
    list_style:str=None          # マーカー関連をまとめて指定	li要素、「display: list_item」が指定された要素	する
    list_style_type:str=None     # マーカーの種類	li要素、「display: list_item」が指定された要素	する
    list_style_position:str=None # マーカーの位置	li要素、「display: list_item」が指定された要素	する
    list_style_image:str=None    # マーカーの画像	li要素、「display: list_item」が指定された要素	する
    #テーブル=None	適用対象	継承
    table_layout:str=None    # 表のレイアウト方法	table要素	しない
    border_collapse:str=None # 境界線の表示方法	table要素	する
    border_spacing:str=None  # 境界線の間隔	table要素	する
    empty_cells:str=None     # 空セルの境界線	th要素、td要素	する
    caption_side:str=None    # 表タイトルの位置	caption要素	する

    def add(self):
        style  = ' style="'
        style += f'font:{self.font};'                                  if(self.font)                 else ""
        style += f'font-size:{self.font_size};'                        if(self.font_size)            else ""
        style += f'font-weight:{self.font_weight};'                    if(self.font_weight)          else ""
        style += f'font-style:{self.font_style};'                      if(self.font_style)           else ""
        style += f'font-family:{self.font_family};'                    if(self.font_family)          else ""
        style += f'font-variant:{self.font_variant};'                  if(self.font_variant)         else ""
        style += f'text-align:{self.text_align};'                      if(self.text_align)           else ""
        style += f'vertical-align:{self.vertical_align};'              if(self.vertical_align)       else ""
        style += f'line-height:{self.line_height};'                    if(self.line_height)          else ""
        style += f'text-decoration:{self.text_decoration};'            if(self.text_decoration)      else ""
        style += f'text-indent:{self.text_indent};'                    if(self.text_indent)          else ""
        style += f'text-transform:{self.text_transform};'              if(self.text_transform)       else ""
        style += f'letter-spacing:{self.letter_spacing};'              if(self.letter_spacing)       else ""
        style += f'word-spacing:{self.word_spacing};'                  if(self.word_spacing)         else ""
        style += f'white-space:{self.white_space};'                    if(self.white_space)          else ""
        style += f'color:{self.color};'                                if(self.color)                else ""
        style += f'background:{self.background};'                      if(self.background)           else ""
        style += f'background-color:{self.background_color};'          if(self.background_color)     else ""
        style += f'background-image:{self.background_image};'          if(self.background_image)     else ""
        style += f'background-repeat:{self.background_repeat};'        if(self.background_repeat)    else ""
        style += f'background-position:{self.background_position};'    if(self.background_position)  else ""
        style += f'background-attachment:{self.background_attachment};' if(self.background_attachment) else ""
        style += f'width:{self.width};'                                if(self.width)                else ""
        style += f'height:{self.height};'                              if(self.height)               else ""
        style += f'max-width:{self.max_width};'                        if(self.max_width)            else ""
        style += f'min-width:{self.min_width};'                        if(self.min_width)            else ""
        style += f'max-height:{self.max_height};'                      if(self.max_height)           else ""
        style += f'min-height:{self.min_height};'                      if(self.min_height)           else ""
        style += f'margin:{self.margin};'                              if(self.margin)               else ""
        style += f'm-argin-top:{self.m_argin_top};'                    if(self.m_argin_top)          else ""
        style += f'm-argin-right:{self.m_argin_right};'                if(self.m_argin_right)        else ""
        style += f'm-argin-bottom:{self.m_argin_bottom};'              if(self.m_argin_bottom)       else ""
        style += f'm-argin-left:{self.m_argin_left};'                  if(self.m_argin_left)         else ""
        style += f'p-adding:{self.p_adding};'                          if(self.p_adding)             else ""
        style += f'p-adding-top:{self.p_adding_top};'                  if(self.p_adding_top)         else ""
        style += f'p-adding-right:{self.p_adding_right};'              if(self.p_adding_right)       else ""
        style += f'p-adding-bottom:{self.p_adding_bottom};'            if(self.p_adding_bottom)      else ""
        style += f'p-adding-left:{self.p_adding_left};'                if(self.p_adding_left)        else ""
        style += f'border:{self.border};'                              if(self.border)               else ""
        style += f'border-top:{self.border_top};'                      if(self.border_top)           else ""
        style += f'border-right:{self.border_right};'                  if(self.border_right)         else ""
        style += f'border-bottom:{self.border_bottom};'                if(self.border_bottom)        else ""
        style += f'border-left:{self.border_left};'                    if(self.border_left)          else ""
        style += f'border-width:{self.border_width};'                  if(self.border_width)         else ""
        style += f'border-top-width:{self.border_top_width};'          if(self.border_top_width)     else ""
        style += f'border-right-width:{self.border_right_width};'      if(self.border_right_width)   else ""
        style += f'border-bottom-width:{self.border_bottom_width};'    if(self.border_bottom_width)  else ""
        style += f'border-left-width:{self.border_left_width};'        if(self.border_left_width)    else ""
        style += f'border-color:{self.border_color};'                  if(self.border_color)         else ""
        style += f'border-top-color:{self.border_top_color};'          if(self.border_top_color)     else ""
        style += f'border-right-color:{self.border_right_color};'      if(self.border_right_color)   else ""
        style += f'border-bottom-color:{self.border_bottom_color};'    if(self.border_bottom_color)  else ""
        style += f'border-left-color:{self.border_left_color};'        if(self.border_left_color)    else ""
        style += f'border-style:{self.border_style};'                  if(self.border_style)         else ""
        style += f'border-top-style:{self.border_top_style};'          if(self.border_top_style)     else ""
        style += f'border-right-style:{self.border_right_style};'      if(self.border_right_style)   else ""
        style += f'border-bottom-style:{self.border_bottom_style};'    if(self.border_bottom_style)  else ""
        style += f'border-left-style:{self.border_left_style};'        if(self.border_left_style)    else ""
        style += f'overflow:{self.overflow};'                          if(self.overflow)             else ""
        style += f'display:{self.display};'                            if(self.display)              else ""
        style += f'visibility:{self.visibility};'                      if(self.visibility)           else ""
        style += f'clip:{self.clip};'                                  if(self.clip)                 else ""
        style += f'float:{self.float};'                                if(self.float)                else ""
        style += f'clear:{self.clear};'                                if(self.clear)                else ""
        style += f'position:{self.position};'                          if(self.position)             else ""
        style += f'top:{self.top};'                                    if(self.top)                  else ""
        style += f'right:{self.right};'                                if(self.right)                else ""
        style += f'bottom:{self.bottom};'                              if(self.bottom)               else ""
        style += f'left:{self.left};'                                  if(self.left)                 else ""
        style += f'z-index:{self.z_index};'                            if(self.z_index)              else ""
        style += f'direction:{self.direction};'                        if(self.direction)            else ""
        style += f'unicode-bidi:{self.unicode_bidi};'                  if(self.unicode_bidi)         else ""
        style += f'list-style:{self.list_style};'                      if(self.list_style)           else ""
        style += f'list-style-type:{self.list_style_type};'            if(self.list_style_type)      else ""
        style += f'list-style-position:{self.list_style_position};'    if(self.list_style_position)  else ""
        style += f'list-style-image:{self.list_style_image};'          if(self.list_style_image)     else ""
        style += f'table-layout:{self.table_layout};'                  if(self.table_layout)         else ""
        style += f'border-collapse:{self.border_collapse};'            if(self.border_collapse)      else ""
        style += f'border-spacing:{self.border_spacing};'              if(self.border_spacing)       else ""
        style += f'empty-cells:{self.empty_cells};'                    if(self.empty_cells)          else ""
        style += f'caption-side:{self.caption_side};'                  if(self.caption_side)         else ""
        style += '"'
        return style


def style(tag, border="sold 1px", bg="#cdefff", indent="    "):
    htmls = []
    htmls.append(f'<style>')
    htmls.append(f'{indent * 1}{tag} {{')
    htmls.append(f'{indent * 2}border: {border};')
    htmls.append(f'{indent * 1}}}')
    htmls.append(f'</style>')
    return "\n".join(htmls) + "\n"

class Table:
    def __init__(self, width=None, border=None, bg=None):
        self.width  = width
        self.border  = border
        self.bg     = bg
        self.indent = "    "
        self.offset = 0

    def add_table(self,table, table_style=None, row_style=None, cell_style=None):
        html = self.start(style=table_style)
        for row in table:
            html += self.start_row(style=row_style)
            for cell in row:
                html += self.add_cell(cell,style=cell_style)
            html += self.end_row()
        html += self.end()
        return html

    def add_row(self,row, style=None):
        html  = self.start_row(style=style)
        for cell in row:
            html += self.add_cell(cell)
        html += self.end_row()
        return html
    
    def start(self, style=None,offset=0):
        html  = f'{self.indent * self.offset}<table'
        html += f' width="{self.width}"'            if self.width   else ""
        if(style):
            html += style.add()
        html += f'>'
        html = html.replace('style=" "', '')
        self.offset += 1
        return html + "\n"

    def start_row(self, style=None):
        html  = f'{self.indent * self.offset}<tr{style.add() if(style) else ""}>'
        self.offset += 1
        return html + "\n"

    def end_row(self):
        self.offset -= 1
        html  = f'{self.indent * self.offset}<tr>'
        return html + "\n"

    def add_cell(self, body="", width="auto", header=False, style=None):
        if(header):
            tag = "th"
        else:
            tag = "td"
        if(isinstance(body,str)):
            my_bodies = [body]
        else:
            my_bodies = body
        html = ""
        for my_body in my_bodies:
            html += f'{self.indent * self.offset}<{tag} {style.add() if(style) else ""}>{my_body}</{tag}>'
        return html + "\n"

    def end(self):
        self.offset -= 1
        html  = f'{self.indent * self.offset}</table>'
        return html + "\n"

    






    
if __name__ == "__main__":
    main()
