import win32com.client as win32
import os
import json
import sys
from datetime import date

def read_body_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        body = file.read()
    return body

def read_config():
    config_file_path = os.path.join(os.getcwd(), "config.json")
    with open(config_file_path, "r", encoding="utf-8") as file:
        config = json.load(file)
    return config

def create_outlook_email(recipients, subject, body):
    outlook = win32.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)
    mail.Subject = subject
    mail.Body = body
    mail.To = ";".join(recipients)
    mail.Display()

def main():
    config = read_config()
    recipients = config["recipients"]
    start_file = config["start_file"]
    end_file = config["end_file"]
    body_file = config["body_file"]

    today = date.today()
    formatted_date = today.strftime("%m/%d")

    if len(sys.argv) > 1:
        if sys.argv[1] == "Start":
            body = read_body_file(start_file) + read_body_file(body_file)
            subject = f"{config['subject_for_start']} {formatted_date}"
        elif sys.argv[1] == "End":
            body = read_body_file(end_file) + read_body_file(body_file)
            subject = f"{config['subject_for_end']} {formatted_date}"
        else:
            print("Invalid argument. Use 'Start' or 'End'.")
            return
    else:
        body = read_body_file(start_file) + read_body_file(body_file)
        subject = f"{config['subject']} {formatted_date}"

    create_outlook_email(recipients, subject, body)

if __name__ == "__main__":
    main()
