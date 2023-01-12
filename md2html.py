import markdown
from bs4 import BeautifulSoup
from dataclasses import dataclass


def main():
    with open ("sendmail.md", "r", encoding="utf-8") as f:
        md_text = f.read()
        html = markdown.markdown(md_text)

    #print(html)
    headline = Table()

    table = [["xxxx", "yyyy"], ["zzzz", "vvvv"]]

    html =  ""
    html += style("td", border="solid 0px")
    html += style("th", border="solid 0px")

    html += headline.add_row(["aaaaa"])
    html += headline.start()
    html += headline.start_row()
    html += headline.add_cell("aaaa", width="100px", header=True )
    html += headline.add_cell("bbbb", width="auto")
    html += headline.end_row()
    html += headline.start_row()
    html += headline.add_cell("cccc" , header=True)
    html += headline.add_cell("dddd" )
    html += headline.end_row()
    html += headline.end()

    html += headline.add_table(table)

    with open ("test2.html", "w", encoding="utf-8") as f:
        f.write(html)




def style(tag, border="sold 1px", bg="#cdefff", indent="    "):
    htmls = []
    htmls.append(f'<style>')
    htmls.append(f'{indent * 1}{tag} {{')
    htmls.append(f'{indent * 2}border: {border};')
    htmls.append(f'{indent * 1}}}')
    htmls.append(f'</style>')
    return "\n".join(htmls) + "\n"

class Table:
    def __init__(self, width="100%", border="sold 1px", bg="#cdefff"):
        self.width  = width
        self.border  = border
        self.bg     = bg
        self.indent = "    "
        self.offset = 0

    def add_table(self,table):
        html = self.start()
        for row in table:
            html += self.start_row()
            for cell in row:
                html += self.add_cell(cell)
            html += self.end_row()
        html += self.end()
        return html

    def add_row(self,row):
        html = self.start()
        html += self.start_row()
        for cell in row:
            html += self.add_cell(cell)
        html += self.end_row()
        html += self.end()
        return html
    
    def start(self, offset=0):
        html  = f'{self.indent * self.offset}<table'
        html += f' width="{self.width}"'
        html += f' style="'
        html += f' border: {self.border};'
        html += f' background-color: {self.bg};'
        html += f' "'
        html += f'>'
        self.offset += 1
        return html + "\n"

    def start_row(self):
        html  = f'{self.indent * self.offset}<tr>'
        self.offset += 1
        return html + "\n"

    def end_row(self):
        self.offset -= 1
        html  = f'{self.indent * self.offset}<tr>'
        return html + "\n"

    def add_cell(self, body="None", width="auto", header=False):
        if(header):
            tag = "th"
        else:
            tag = "td"
        html  = f'{self.indent * self.offset}<{tag} width="{width}">{body}</{tag}>'
        return html + "\n"

    def end(self):
        self.offset -= 1
        html  = f'{self.indent * self.offset}</table>'
        return html + "\n"

    






    
if __name__ == "__main__":
    main()
