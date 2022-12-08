# １：ライブラリ設定
import fitz # pymupdfライブラリ
import openpyxl as px 
from openpyxl.styles import Alignment
import json
import re

# ２：PDFテキストを格納するリスト作成
txt_list = []

# ３：PDFファイルを読み込む
filename = r"C:\Users\phantasm\Downloads\NCB-PCI_Express_Base_5.0r1.0-2019-05-22.pdf"
doc = fitz.open(filename)

# ４：１ページずつテキストデータを取得


class Paragraph:
    def __init__(self,span):
        size = span.get("size")
        self.title = ""
        self.body  = ""
        self.has_body = False
        text = span.get("text")
        if( self.is_title(span)):
            self.title += text
        if( self.is_body(span)):
            self.has_body = True
            self.body += text
    @classmethod
    def is_title(self,span):
        size = span.get("size")
        if(size==72 or size == 18 or size == 16 or size == 14 or size == 13):
            return True
        else:
            return False

    @classmethod
    def is_body (self,span):
        size  = span.get("size")
        color = span.get("color")
        if(size==10 and color==0):
            return True
        else:
            return False

    def add_body(self,span):
        self.body += " " + span.get("text")
        self.has_body = True
        pass

    def add_title(self,span):
        self.title += " " + span.get("text")
        pass


# 番号なしリストの1行目は、　lines の要素が2個 (同リストの事業は別line)
# block はページに相当する。
page_start = 88
page_range = 10
paragraphs  = []
size_of_title_max = 25
size_of_title_min = 14
size_of_body_max  = 14
with open ("hoge.json", "w") as f:
    pass

paragraphs = []
for i, page in enumerate(range(len(doc))):
    if(i<page_start):
        continue
    if((page_start+page_range)<i):
        break
    page_text = doc[page].get_text()
    with open ("hoge.json", "a") as f:
        #print(doc[page].get_text("json"))
        f.write(doc[page].get_text("json"))
        images = doc[page].get_images()
        if(len(images)):
            f.write(doc[page].get_images("json"))


    json_load = json.loads(doc[page].get_text("json"))
    pass

    for block in json_load.get("blocks"):
        #type of the block is "list"
        #print(f'key={key}, value={value}')
        #print(f'block={block}')
        for line in block.get("lines"):
            #print(f'line={line}')
            for span in line.get("spans"):
                text = span.get("text")
                size = span.get("size")
                if(Paragraph.is_title(span)):
                    if 'paragraph' in locals():
                        if(paragraph.has_body):
                            paragraphs.append(paragraph)
                            paragraph = Paragraph(span)
                        else:
                            paragraph.add_title(span)
                    else:
                        paragraph = Paragraph(span)
                elif(Paragraph.is_body(span)):
                    if 'paragraph' in locals():
                        paragraph.add_body(span)
                    else:
                        print(f'Skipping it (size {size}) due to a paragraph object is not defined. "{text}"')
                else:
                    print(f'Skipping it (size {size}) since unexpected font. "{text}"')
                pass


pass

for paragraph in paragraphs:
    print(f'{paragraph.title}')
    str = paragraph.body
    while(True):
        m = re.search(r"(?P<match>.*?\.) " , str)
        if(m):
            str = re.sub(r"^.*?\. ", "", str)
            match = m.group("match")
            match = match.strip(" ")
            print("\t" + match)
        else:
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