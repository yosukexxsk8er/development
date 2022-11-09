import win32com.client
import datetime

outlook = win32com.client.Dispatch("outlook.Application")

print(type(outlook))


APPOINTMENT_ITEM = 1
item = outlook.CreateItem(APPOINTMENT_ITEM)
a = datetime.datetime(2022, 11, 13, 13,15)
b =datetime.datetime.today()
print(type(a))
print(type(b))
item.Start = a
item.Duration = 30
item.Subject = '定例ミーティング'
item.Body = 'いつものミーティング'
item.ReminderMinutesBeforeStart = 0
item.ReminderSet = True
item.BusyStatus = 0
item.Save()


dt_now = datetime.datetime.now()
print(dt_now)

print(item)