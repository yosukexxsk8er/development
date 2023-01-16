from dataclasses import dataclass

def main():
    #print(html)
    headline_table = Table(border="solid 1px")

    table = [["xxxx", "yyyy"], ["zzzz", "vvvv"]]

    html =  ""
    html += StyleProperty(border="solid 0px").header("td")
    html += StyleProperty(border="solid 2px").header("th")

    table_style = StyleProperty(font_size="large", background_color="yellow")

    html += headline_table.start(style=StyleProperty(background_color="gray", width="100px", text_align="center"))
    html += headline_table.add_row(["aaaaa"])
    html += headline_table.start()
    html += headline_table.start_row(style=StyleProperty(background="lightblue"))
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
    background_color:str=None      # 背景色	全ての要素	しない
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

    def has_valid(self):
        for value in vars(self).values():
            if(value is not None):
                return True
        return False

    def add(self):
        if(self.has_valid()):
            style = ' style="'
            for key, value in vars(self).items():
                if(value is not None):
                    style+= f'{key.replace("_", "-")}:{value};'

            style+= '"'
            return style
        else:
            return ""

    def header(self, tag, indent="    "):
        style = []
        style.append(f'<style>')
        style.append(f'{indent * 1}{tag} {{')
        for key, value in vars(self).items():
            if(value is not None):
                style.append(f'{indent * 2}{key.replace("_", "-")}:{value};')
        #style.append(f'{indent * 2}border: {border};')
        style.append(f'{indent * 1}}}')
        style.append(f'</style>')
        return "\n".join(style) + "\n"



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
