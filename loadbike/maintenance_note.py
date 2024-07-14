import datetime
import json
from bs4 import BeautifulSoup
import re
import csv
import os


def main():
    from merge_activities import merge_activities
    file_prefix = "maintenance_note"
    json_file = file_prefix + ".json"
    csv_filename = "./Activities_Merged.csv"

    with open(json_file, "r", encoding="utf-8_sig") as f:
        json_dict = json.load(f)
    files = json_dict["Activities"]
    merge_activities(files,save_name=csv_filename)
    activities = Activities(csv_filename)
    #distance  =activities.distance(date(2022,1,1), date(2022,12,31))
    #print(f'Distance:{distance:.2f}[km]')

    parts = Parts(json_file,activities)
    parts.dump_list()
    pass
    

#COL_DISTANCE = "Distance"
COL_DISTANCE = "距離"
COL_DATE     = "日付"
    
class Activities:
    def __init__(self,csv_file):
        self.activities = []
        with open(csv_file,newline="", encoding='utf-8') as csvf:
            data=csv.reader(csvf)
            for i,line in enumerate(data):
                if(i==0):
                    keys = line
                else:
                    self.activities.append(self._dec_garmin_line(keys,line))
    
    def distance(self, start_date, end_date):
        sum = 0
        for activity in self.activities:
            if(start_date<= activity[f"{COL_DATE}"] <=end_date):
                sum+= activity[f"{COL_DISTANCE}"]
        return sum

    def _dec_garmin_line(self,keys,line):
        dict = {}
        for j,cell in enumerate(line):
            key = keys[j]
            if(key==f"{COL_DATE}"):
                cell = datetime.datetime.strptime(cell, '%Y-%m-%d %H:%M:%S').date()
            try:
                cell = float(cell)
            except:
                pass
            exec(f'dict["{key}"] = cell')
        return dict



class Parts:
    def __init__(self,json_file,activities):
        self.list = []
        with open(json_file, "r", encoding="utf-8_sig") as f:
            json_dict = json.load(f)
        for part in json_dict["Parts"]:
            start_date = datetime.datetime.strptime(part["StartDate"], '%Y/%m/%d').date()
            all_date = part["ChangeDate"].copy()
            mark_list = ["" for i in range(len(all_date))]
            if(part["EndDate"] is not None):
                all_date.append(part["EndDate"])
                mark_list.append("")
            else:
                all_date.append(datetime.date.today().strftime("%Y/%m/%d"))
                mark_list.append("*")
            previous_date = start_date
            memo = ""
            try:
                memo = part["Memo"]
            except KeyError:
                pass
            for i, (change_date, mark) in enumerate(zip(all_date,mark_list)):
                change_date = datetime.datetime.strptime(change_date, '%Y/%m/%d').date()
                distance = activities.distance(previous_date, change_date)
                line = [part["Name"],previous_date,change_date,f'{distance:.2f}[km]',mark,memo]
                #print(line)
                self.list.append(line)
                previous_date = change_date
    
    def dump_list(self):
        list = []
        for line in self.list:
            str_line = []
            for cell in line:
                if(isinstance(cell,datetime.date)):
                    cell = cell.strftime('%Y/%m/%d')
                str_line.append(cell)
            #_ = ','.join(line)
            print("\t".join(str_line))
            list.append(str_line)
        return list




class Part:
    def __init__(self):
        pass



if __name__ == "__main__":
    main()
