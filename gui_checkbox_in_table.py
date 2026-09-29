import PySimpleGUI as sg
import random
import string
import datetime

"""
    Basic use of the Table Element
"""

sg.theme('Dark Blue')

# ------ Some functions to help generate data for the table ------
def word():
    return ''.join(random.choice(string.ascii_lowercase) for i in range(10))
def number(max_val=1000):
    return random.randint(0, max_val)

def make_table(num_rows, num_cols):
    data = [[j for j in range(num_cols)] for i in range(num_rows)]
    data[0] = [word() for __ in range(num_cols)]
    for i in range(1, num_rows):
        data[i] = [word(), *[number() for i in range(num_cols - 1)]]
    return data

# ------ Make the Table Data ------
data = make_table(num_rows=15, num_cols=6)
headings = [str(data[0][x])+'     ..' for x in range(len(data[0]))]

# ------ Window Layout ------
layout = [[sg.Table(values=data[1:][:], headings=headings, max_col_width=25,
                    # background_color='light blue',
                    auto_size_columns=True,
                    display_row_numbers=True,
                    justification='right',
                    num_rows=15,
                    alternating_row_color='#000020',
                    select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                    enable_events=True,
                    key='-TABLE-',
                    row_height=35,
                    tooltip='This is a table')],
          [sg.Button('Read'), sg.Button('Double'), sg.Button('Change Colors')],
          [sg.Text('Read = read which rows are selected')],
          [sg.Text('Double = double the amount of data in the table')],
          [sg.Text('Change Colors = Changes the colors of rows 8 and 9')]]

# ------ Create Window ------
window = sg.Window('The Table Element', layout, finalize=True,
                   # font='Helvetica 25',
                   )
table = window['-TABLE-']
# ------ Event Loop ------

user_click = True
selected = []
double_click_dt_s = None
double_click_dt_e = None
double_click_dt_diff =  datetime.timedelta(seconds=1)


while True:
    event, values = window.read()
    print(event, values)
    if event == sg.WIN_CLOSED:
        break
    if event == 'Double':
        for i in range(len(data)):
            data.append(data[i])
        window['-TABLE-'].update(values=data)
    elif event == 'Change Colors':
        window['-TABLE-'].update(row_colors=((8, 'white', 'red'), (9, 'green')))
    elif event == '-TABLE-':
        if user_click:
            double_click_dt_e = datetime.datetime.now()
            if(double_click_dt_s is not None):
                dt_diff = double_click_dt_e - double_click_dt_s
                print(f'start={double_click_dt_s}')
                print(f'end  ={double_click_dt_e}')
                print(f'diff={dt_diff}')
                print(f'{type(dt_diff)}, {type(double_click_dt_diff)}')
                if(dt_diff < double_click_dt_diff):
                    if len(values['-TABLE-']) == 1:
                        select = values['-TABLE-'][0]
                        if select in selected:
                            selected.remove(select)
                        else:
                            selected.append(select)
                        table.update(select_rows=selected)
                        user_click = False
            double_click_dt_s = double_click_dt_e
        else:
            user_click = True

window.close()
