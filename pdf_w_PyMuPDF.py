# １：ライブラリ設定
import fitz # pymupdfライブラリ
import openpyxl as px 
from openpyxl.styles import Alignment
import json
import re
from tqdm import tqdm




class Attr:
    def __init__(self,size="*", font="*", color="*", indent="*"):
        self.size = size
        self.font = font
        self.color = color
        self.indent = indent

    def __eq__(self, other):
        flag = True
        if(other.size != "*" and self.size != other.size):
            flag = False
        if(other.font != "*" and self.font != other.font):
            flag = False
        if(other.color != "*" and self.color != other.color):
            flag = False
        if(other.indent != "*" and self.indent != other.indent):
            flag = False
        return flag
    
#ParegraphクラスがクラスLineを配列のとして格納する
# Lineには、 spanを解析することで分類された属性と文からなる。
class Line():
    def __init__(self, span:object, rule:dict):
        self.attr = Attr(
            size=span.get("size"),
            font=span.get("font"),
            color=span.get("color"),
            indent=span.get("origin")[0]
            )
        self.span = span
        self.type = None
        self.text = span.get("text")
        for type, formats in rule.items():
            for format in formats:
                other_attr = Attr(format["size"], format["font"], format["color"], format["indent"])
                if(self.attr == other_attr):
                    self.type = type
                    break
            else:
                continue
            break

        pass

    def __eq__(self,other):
        if(self.type == other.type):
            return True
        else:
            return False

    def add(self, other_line:object):
        self.text += other_line.text


#パラグラフは 章の名前と、本文に分類する。本文には 通常文書、リスト、図表名を区別する。
#通常文書、リスト、図表名 が切り替わっタイミングで、切り替わり前のを1つの文字列する
# またその１つの文字列が何なのかを示す属性(ID)を付加する。


class Paragraph:
    def __init__(self,span, dict):
        size = span.get("size")
        self.title = ""
        self.body  = ""
        self.has_body = False
        text = span.get("text")
        if( self.is_title(span, dict)):
            self.title += text
        if( self.is_body(span, dict)):
            self.has_body = True
            self.body += text
    @classmethod
    def is_title(self,span, dict):
        self_attr = Attr(size=span.get("size"), font=span.get("font"), color=span.get("color"), indent=span.get("origin")[0])
        for title in dict.get("Titles"):
            other_attr = Attr(size=title.get("size"), font=title.get("font"), color=title.get("color"), indent=title.get("indent"))
            if(self_attr == other_attr):
                return True
        return False

    @classmethod
    def is_body (self,span, dict):
        self_attr = Attr(size=span.get("size"), font=span.get("font"), color=span.get("color"), indent=span.get("origin")[0])
        for body in dict.get("Bodies"):
            other_attr = Attr(size=body.get("size"), font=body.get("font"), color=body.get("color"), indent=body.get("origin")[0])
            if(self_attr == other_attr):
                return True
        return False

    def add_body(self,span):
        self.body += " " + span.get("text")
        self.has_body = True
        pass

    def add_title(self,span):
        self.title += " " + span.get("text")
        pass

def main():
    # ２：PDFテキストを格納するリスト作成
    txt_list = []

    # ３：PDFファイルを読み込む
    filename = r"C:\Users\phantasm\Downloads\NCB-PCI_Express_Base_5.0r1.0-2019-05-22.pdf"
    doc = fitz.open(filename)

    # ４：１ページずつテキストデータを取得

    # 番号なしリストの1行目は、　lines の要素が2個 (同リストの事業は別line)
    # block はページに相当する。

    #設定ファイルを読み込む
    config_file = "pdf_w_PyMuPDF_setting.json"
    with open(config_file) as f:
        setting_dict = json.load(f)


    analyzed_lines = []
    dump_file = "pdf_w_PyMuPDF_dump.json"
    page_start = 88
    page_range = 40
    with open (dump_file, "w") as f:
        for page in tqdm(range(page_start, page_start+page_range)):
            
            # 解析用に json file formatで取得した内容(Page毎)をファイルに書き出す()
                #print(doc[page].get_text("json"))
            f.write(doc[page].get_text("json"))
            images = doc[page].get_images()
            if(len(images)):
                try:
                    f.write(doc[page].get_images("json"))
                except TypeError:
                    f.write(f"!!! ERRROR  in page{page}!!!!")


            # PDF情報(Page毎)を Json format で出力した内容を辞書に変換し変数に格納する
            json_load = json.loads(doc[page].get_text("json"))
            pass

            # 現ページの情報をBlockという単位で取り出す
            for block in json_load.get("blocks"):
                #type of the block is "list"
                #print(f'key={key}, value={value}')
                #print(f'block={block}')
                #現Blockの情報を1行ずつ取り出す。
                for line in block.get("lines"):
                    #print(f'line={line}')
                    # 章の名前と、内容に分離したあと、両方を オブジェクト Paragraph に格納する
                    # ここでBody部分に該当する行はすべて連結する。
                    for span in line.get("spans"):
                        text = span.get("text")
                        size = span.get("size")
                        analyzed_lines.append(Line(span, setting_dict))



    debug_file = "pdf_w_PyMuPDF_debug.log"
    with open (debug_file, "w", encoding='utf-8') as f:
        for line in analyzed_lines:
            f.write(f'type:{line.type:15s},indent:{line.span.get("origin")[0]}, \t{line.text}\n')


    pass

    for line in analyzed_lines:
        pass
        while(False):
            m = re.search(r"(?P<match>.*?\.) " , str)
            if(m):
                str = re.sub(r"^.*?\. ", "", str)
                match = m.group("match")
                # 両端にある " " を削除
                match = match.strip(" ")
                print("\t" + match)
            else:
                # 両端にある " " を削除
                str = str.strip(" ")
                print("\t" + str)
                break
    exit()
    # ５：新しいExcelファイルを作成
    wb = px.Workbook()
    ws = wb.active

    # ６：Excelの書式設定
    my_alignment=Alignment(vertical='top', wrap_text=True)
    ws.column_dimensions['B'].width = 100

    # ７：Excelのヘッダーを出力
    headers = ['ページ', '内容']
    for i, header in enumerate(headers):
        ws.cell(row=1, column=1+i, value=headers[i])

    # ８：ExcelにPDFのテキストを出力
    for y, row in enumerate(txt_list):
        for x, cell in enumerate(row):
            ws.cell(row= y+2, column= x+1, value=cell)
            ws.cell(row= y+2, column= x+1).alignment = my_alignment

    # ９：Excelファイルの保存
    xlname = filename.split('.')[0] + '_excel.xlsx'
    wb.save(xlname)




if __name__ == "__main__":
    main()
