import markdown
from bs4 import BeautifulSoup
from dataclasses import dataclass


def main():
    with open ("sendmail.md", "r", encoding="utf-8") as f:
        md_text = f.read()
        html = markdown.markdown(md_text)

    #print(html)
    style = Style("td")
    headline = Table()

    table = [["xxxx", "yyyy"], ["zzzz", "vvvv"]]

    html =  ""
    html += style.dump()
    html += headline.start()
    html += headline.start_row()
    html += headline.add_cell("aaaa", )
    html += headline.add_cell("bbbb", )
    html += headline.end_row()
    html += headline.start_row()
    html += headline.add_cell("cccc", )
    html += headline.add_cell("dddd", )
    html += headline.end_row()
    html += headline.end()

    html += headline.add_table(table)

    with open ("test2.html", "w", encoding="utf-8") as f:
        f.write(html)




@dataclass
class Style:
    tag:str
    border  :str="solid 1px"
    bg      :str="#cdefff"
    def dump(self):
        indent = "    "
        lines = []
        lines.append(f'<style>')
        lines.append(f'{indent * 1}{self.tag} {{')
        lines.append(f'{indent * 2}border: {self.border};')
        lines.append(f'{indent * 1}}}')
        lines.append(f'</style>')
        return "\n".join(lines) + "\n"



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
    
    def start(self, offset=0):
        str  = f'{self.indent * self.offset}<table'
        str += f' width="{self.width}"'
        str += f' style="'
        str += f' border: {self.border};'
        str += f' background-color: {self.bg};'
        str += f' "'
        str += f'>'
        self.offset += 1
        return str + "\n"

    def start_row(self):
        str  = f'{self.indent * self.offset}<tr>'
        self.offset += 1
        return str + "\n"

    def end_row(self):
        self.offset -= 1
        str  = f'{self.indent * self.offset}<tr>'
        return str + "\n"

    def add_cell(self, body="None"):
        str  = f'{self.indent * self.offset}<td>{body}</td>'
        return str + "\n"

    def end(self):
        self.offset -= 1
        str  = f'{self.indent * self.offset}</table>'
        return str + "\n"

    






    
if __name__ == "__main__":
    main()
