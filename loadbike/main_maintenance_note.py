from html_style import StyleProperty
from html_style import Table
import loadbike.maintenance_note as maintenance_note
from loadbike.merge_activities import merge_activities
import json

def main():
    file_prefix = "maintenance_note"
    json_file = "./" + file_prefix + ".json"
    csv_filename = "./Activities_Merged.csv"

    with open(json_file, "r", encoding="utf-8_sig") as f:
        json_dict = json.load(f)
    files = json_dict["Activities"]
    merge_activities(files,dir="./", save_name=csv_filename)
    activities = maintenance_note.Activities(csv_filename)
    #distance  =activities.distance(date(2022,1,1), date(2022,12,31))
    #print(f'Distance:{distance:.2f}[km]')

    parts = maintenance_note.Parts(json_file,activities)
    parts_str_list = parts.dump_list()

    table_html = Table(border="solid 1px")
    table_style = StyleProperty(font_size="small", background_color="white", border="solid 1px")
    html =  ""
    html += table_html.add_table(parts_str_list, table_style=table_style, cell_style=table_style)

    with open (f"{file_prefix}.html", "w", encoding="utf-8") as f:
        f.write(html)
    pass



if __name__ == "__main__":
    main()
