import pyperclip


strings = pyperclip.paste()

body = ""
for i,string in enumerate(strings.splitlines()):
    string = string.replace('"', r'\"')
    string = f'{" ":12s}"{string}",\n'
    body += string

string = f'{" ":12s}""\n'
body += string

print(body)


