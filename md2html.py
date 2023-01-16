import markdown
from bs4 import BeautifulSoup
from html_style import StyleProperty
from html_style import Table

def main():
    with open ("sendmail.md", "r", encoding="utf-8") as f:
        md_text = f.read()
        html = markdown.markdown(md_text)

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




    
if __name__ == "__main__":
    main()
