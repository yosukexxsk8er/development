import PySimpleGUI as sg
import json
import os
#Pythonでカレントディレクトリをスクリプトのディレクトリに固定
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def main():
    # Read json
    json_file = "./config.json"
    template = Template_from_json(json_file)

    # ウィンドウのテーマ
    sg.theme('BlueMono')
    # ウィンドウオブジェクトの作成
    window = sg.Window('title', template.layout, size=(300, 150))
    
    # イベントのループ
    while True:
        # イベントの読み込み
        event, values = window.read()
        if (event == sg.WIN_CLOSED):
            break
        # ウィンドウの×ボタンクリックで終了
        try:
            print(template.get_content(event))
        except KeyError:
            print(f'The event "{event}" is not defined in {json_file}')
            
    
    # ウィンドウ終了処理
    window.close()



class Template_from_json:
    def __init__(self,json_file):
        self.json_file = json_file
        with open(self.json_file, 'r', encoding='utf-8') as fp:
            self.js_dict = json.load(fp)
        self.layout = []
        self.contents = {}
        for key1, dict1 in self.js_dict.items():
            self.contents[key1] = "\n".join(self.js_dict[key1].get("content"))
            self.layout.append([sg.Button(key1,key=key1, size=(30,1), tooltip=self.contents[key1])])
        
    def get_content(self,event)->str:
        return self.contents[event]

if __name__ == "__main__":
    main()
