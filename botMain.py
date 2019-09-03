import sqlite3
import telebot
from telebot import types
from telebot.types import Message
from datetime import datetime
import schedule
import time
import threading

# create DataBases Methods

# conn = sqlite3.connect("dataUser.db")
# cur = conn.cursor()
# cur.execute("CREATE TABLE IF NOT EXISTS users (chatId INTEGER, autoSend BOOLEAN)")
# conn.commit()
# conn.close()


# conn = sqlite3.connect("dataJobs.db")
# cur = conn.cursor()
# cur.execute("CREATE TABLE IF NOT EXISTS jobs (job TEXT, status TEXT, city TEXT, timeOfJob TEXT, hours TEXT, salary TEXT, contact TEXT)")
# conn.commit()
# conn.close()

bot = telebot.TeleBot("token")

# Outlets and Variables

job = ''
status = ''
city = ''
timeOfJob = ''
hours = ''
salary = ''
contact = ''


# ViewsMethods
def viewSpecialJobs(status_job):
    # added
    delete()
    conn = sqlite3.connect("dataJobs.db")
    cur = conn.cursor()
    cur.execute("SELECT job,status,city,timeOfJob,hours,salary,contact FROM jobs WHERE status = ? " , (status_job,))
    rows = cur.fetchall()
    conn.close()
    return rows


# search for All Jobs
def viewAllJobs():
    conn = sqlite3.connect("dataJobs.db")
    cur = conn.cursor()
    cur.execute("SELECT job,status,city,timeOfJob,hours,salary,contact FROM jobs")
    rows = cur.fetchall()
    conn.close()
    return rows



# searchUsers
def viewUsers():
    conn = sqlite3.connect("dataUser.db")
    cur = conn.cursor()
    cur.execute("SELECT chatId, autoSend FROM users")
    rows = cur.fetchall()
    conn.close()
    return rows
#cleanDataBaseMethod


def delete():
    date = datetime.today().strftime('%d.%m.%Y')
    nowdate = datetime.today().strptime(date,'%d.%m.%Y')
    conn = sqlite3.connect("dataJobs.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM jobs")
    rows = cur.fetchall()
    for i in rows:
        jobdate = datetime.strptime(i[3], '%d.%m.%Y')
        if jobdate < nowdate:
            conn = sqlite3.connect("dataJobs.db")
            cur = conn.cursor()
            cur.execute("DELETE FROM jobs WHERE timeOfJob=?", (i[3],))
            conn.commit()
            conn.close()

# job TEXT, status TEXT, city TEXT, timeOfJob TEXT, hours TEXT, salary TEXT, contact TEXT
def insertToDB(job,status,city,timeOfJob,hours,salary,contact):
    now = datetime.today()
    timeOfJob = timeOfJob + '.' + str(now.year)
    print(timeOfJob)
    conn = sqlite3.connect("dataJobs.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO jobs VALUES (?,?,?,?,?,?,?)",(job,status,city,timeOfJob,hours,salary,contact))
    conn.commit()
    conn.close()

def insertChatId(chatId, autoSend, status):
    conn = sqlite3.connect("dataUser.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO users VALUES(?,?,?)",(chatId,autoSend,status))
    print("Inserting is good")
    conn.commit()
    conn.close()

# DoubleCheck of UserId

def doubleCheckId(numId):
    conn = sqlite3.connect("dataUser.db")
    cur = conn.cursor()
    cur.execute("SELECT chatId FROM users")
    rows = cur.fetchall()
    checkExistedId = False
    for i in rows:
        for var in i:
            print(var)
            if var == numId:
                print("Id already exists")
                checkExistedId = True
    return checkExistedId




#autoSending Functions
def func_send(userId,status):
    for i in viewSpecialJobs(status):
        jobString = ''
        for var in i:
            jobString = jobString + " " + var
        try:
            bot.send_message(userId, jobString)
        except:
            print("User blocked Bot")
    # bot.send_message(userId, "Привет авто!")
    print("Schedule")


def subscribing():
    while True:
        conn = sqlite3.connect("dataUser.db")
        cur = conn.cursor()
        cur.execute("SELECT chatId, status FROM users WHERE autoSend = ?", (True,))
        rows = cur.fetchall()
        for i in rows:
            schedule.every(5).minutes.do(func_send,i[0],i[1]).tag(i[0])
            # for var in i:
            #     # print(var)
            #     print(i[0])
            #     print(i[1])
            #     # schedule.every().day.at("20:00").do(func_send,i[0],i[1]).tag(var)
            #         # func_send(var)
        print(rows)
        conn.close()
        while True:
            print("While")
            schedule.run_pending()
            time.sleep(1)



@bot.message_handler(content_types=['text'])
@bot.message_handler(commands=['start','reg','endSubscribe'])
def inlineBtn(message: Message):
    chatNum = message.chat.id
    # Doublecheck and Inserting Id of User
    checkId = doubleCheckId(chatNum)

    if checkId == False:
        insertChatId(chatNum,False,'None')
        print("Id Inserted Succesfully")

    for i in viewUsers():
        for var in i:
            print(var)
    if message.text == '/start':
        delete()
        bot.send_message(message.chat.id,"Привет, Мы поможем найти тебе работу!")
        keyboard = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text="Работу", callback_data = "Full_time")
        btn2 = types.InlineKeyboardButton(text="Подработку", callback_data = "Part_time")
        keyboard.add(btn1, btn2)
        bot.send_message(message.chat.id, "Привет, Ищешь работу или Подработку?", reply_markup=keyboard)
    elif message.text == '/reg':
        bot.send_message(message.chat.id,"Привет, Глеб) Давай по порядку. Кто будет работать?")
        bot.register_next_step_handler(message, get_job)
    elif message.text == '/statistic':
        conn = sqlite3.connect("dataUser.db")
        cur = conn.cursor()
        cur.execute("SELECT chatId FROM users WHERE status = ?", ('Masa',))
        rowsMasa = len(cur.fetchall())
        cur.execute("SELECT chatId FROM users WHERE status = ?", ('Citizen(FullTime)',))
        rowsCitizenFullTime = len(cur.fetchall())
        cur.execute("SELECT chatId FROM users WHERE status = ?", ('Citizen(PartTime)',))
        rowsCitizenPartTime = len(cur.fetchall())
        cur.execute("SELECT chatId FROM users WHERE status = ?", ('Imigrant(FullTime)',))
        rowsImigrantFullTime = len(cur.fetchall())
        cur.execute("SELECT chatId FROM users WHERE status = ?", ('Imigrant(PartTime)',))
        rowsImigrantPartTime = len(cur.fetchall())
        bot.send_message(message.chat.id,"Граждане постоянная работа - %s; \nГраждане подработка - %s; \nБеженцы постоянная работа - %s; \nБеженцы подработка - %s; \nМасса - %s;"%(rowsCitizenFullTime,rowsCitizenPartTime,rowsImigrantFullTime,rowsImigrantPartTime,rowsMasa))

    elif message.text == '/endsubscribe':
        conn = sqlite3.connect("dataUser.db")
        cur = conn.cursor()
        cur.execute("UPDATE users SET autoSend = ? WHERE chatId = ? ", (False, message.chat.id))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, "Вы отписались от получения новых уведомлений!")
        schedule.clear(message.chat.id)
    elif message.text == '/subscribeMasa':
        conn = sqlite3.connect("dataUser.db")
        cur = conn.cursor()
        cur.execute("UPDATE users SET autoSend = ? WHERE chatId = ? ", (True, message.chat.id))
        cur.execute("UPDATE users SET status = ? WHERE chatId = ? AND autoSend = ? ", ('Masa', message.chat.id, True))
        conn.commit()
        conn.close()
        schedule.every(5).minutes.do(func_send,message.chat.id,'Masa').tag(message.chat.id)
        bot.send_message(message.chat.id, "Поздравляем вы подписались на ежедневную рассылку! Чтобы отписаться введите команду /endsubscribe")

    elif message.text == '/subscribeCitizenFullTime':
        conn = sqlite3.connect("dataUser.db")
        cur = conn.cursor()
        cur.execute("UPDATE users SET autoSend = ? WHERE chatId = ? ", (True, message.chat.id))
        cur.execute("UPDATE users SET status = ? WHERE chatId = ? AND autoSend = ? ", ('Citizen(FullTime)', message.chat.id, True))
        conn.commit()
        conn.close()
        schedule.every(5).minutes.do(func_send,message.chat.id,'Citizen(FullTime)').tag(message.chat.id)
        bot.send_message(message.chat.id, "Поздравляем вы подписались на ежедневную рассылку! Чтобы отписаться введите команду /endsubscribe")

    elif message.text == '/subscribeImmigrantFullTime':
        conn = sqlite3.connect("dataUser.db")
        cur = conn.cursor()
        cur.execute("UPDATE users SET autoSend = ? WHERE chatId = ? ", (True, message.chat.id))
        cur.execute("UPDATE users SET status = ? WHERE chatId = ? AND autoSend = ? ", ('Imigrant(FullTime)', message.chat.id, True))
        conn.commit()
        conn.close()
        schedule.every(5).minutes.do(func_send,message.chat.id,'Imigrant(FullTime)').tag(message.chat.id)
        bot.send_message(message.chat.id, "Поздравляем вы подписались на ежедневную рассылку! Чтобы отписаться введите команду /endsubscribe")

    elif message.text == '/subscribeCitizenPartTime':
        conn = sqlite3.connect("dataUser.db")
        cur = conn.cursor()
        cur.execute("UPDATE users SET autoSend = ? WHERE chatId = ? ", (True, message.chat.id))
        cur.execute("UPDATE users SET status = ? WHERE chatId = ? AND autoSend = ? ", ('Citizen(PartTime)', message.chat.id, True))
        conn.commit()
        conn.close()
        schedule.every(5).minutes.do(func_send,message.chat.id,'Citizen(PartTime)').tag(message.chat.id)
        bot.send_message(message.chat.id, "Поздравляем вы подписались на ежедневную рассылку! Чтобы отписаться введите команду /endsubscribe")

    elif message.text == '/subscribeImmigrantPartTime':
        conn = sqlite3.connect("dataUser.db")
        cur = conn.cursor()
        cur.execute("UPDATE users SET autoSend = ? WHERE chatId = ? ", (True, message.chat.id))
        cur.execute("UPDATE users SET status = ? WHERE chatId = ? AND autoSend = ? ", ('Imigrant(PartTime)', message.chat.id, True))
        conn.commit()
        conn.close()
        schedule.every(5).minutes.do(func_send,message.chat.id,'Imigrant(PartTime)').tag(message.chat.id)
        bot.send_message(message.chat.id, "Поздравляем вы подписались на ежедневную рассылку! Чтобы отписаться введите команду /endsubscribe")



# Registrate New Job
def get_job(message: Message):
    global job;
    job = message.text
    bot.send_message(message.chat.id,"Для кого работа?Cкопируй правильно:(\nMasa\nCitizen(FullTime)\nImigrant(FullTime)\nCitizen(PartTime)\nImigrant(PartTime)")
    bot.register_next_step_handler(message, get_status)

def get_status(message: Message):
    global status;
    status = message.text
    bot.send_message(message.chat.id,"Где будет работа?")
    bot.register_next_step_handler(message, get_city)

def get_city(message: Message):
    global city;
    city = message.text
    bot.send_message(message.chat.id,"Дата работы?")
    bot.register_next_step_handler(message, get_timeOfJob)

def get_timeOfJob(message: Message):
    global timeOfJob;
    timeOfJob = message.text
    bot.send_message(message.chat.id,"Сколько часов работать?")
    bot.register_next_step_handler(message, get_hours)

def get_hours(message: Message):
    global hours;
    hours = message.text
    bot.send_message(message.chat.id,"Сколько зарплата (не твоя конечно же)?")
    bot.register_next_step_handler(message, get_salary)

def get_salary(message: Message):
    global salary;
    salary = message.text
    bot.send_message(message.chat.id,"C кем связываться?")
    bot.register_next_step_handler(message, get_contact)

def get_contact(message: Message):
    global contact;
    contact = message.text
    bot.send_message(message.chat.id,job + " для " + status + " город: " + city + " дата: " + timeOfJob + " " + hours + " часов " + salary + " в час " + contact)
    bot.send_message(message.chat.id,"Убедись, что все верно? Если да, то напиши 'да', если нет, то 'нет' ")
    bot.register_next_step_handler(message, doubleCheck)

def doubleCheck(message: Message):
    if message.text == 'да' or message.text == 'Да':
        insertToDB(job,status,city,timeOfJob,hours,salary,contact)
        bot.send_message(message.chat.id,"Добавлено в базу")
    elif message.text == 'нет' or message.text == 'Нет':
        bot.send_message(message.chat.id,"Давай еще раз. Кто будет работать?")
        bot.register_next_step_handler(message, get_job)



@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "Full_time":
        keyboard = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text="Теудат Зеут", callback_data = "PassportFullTime")
        btn2 = types.InlineKeyboardButton(text="Беженец", callback_data = "ImmigrantFullTime")
        keyboard.add(btn1, btn2)
        bot.send_message(call.message.chat.id, "Выбери свое?", reply_markup=keyboard)

    elif call.data == "Part_time":
        keyboard = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text="Теудат Зеут", callback_data = "PassportPartTime")
        btn2 = types.InlineKeyboardButton(text="Беженец", callback_data = "ImmigrantPartTime")
        btn3 = types.InlineKeyboardButton(text="Масса", callback_data = "MassaPartTime")
        keyboard.add(btn1, btn2, btn3)
        bot.send_message(call.message.chat.id, "Выбери свое?", reply_markup=keyboard)

    elif call.data == "PassportFullTime":
        try:
            for i in viewSpecialJobs('Citizen(FullTime)'):
                jobString = ''
                for var in i:
                    jobString = jobString + " " + var
                bot.send_message(call.message.chat.id, jobString)
        except:
            bot.send_message(call.message.chat.id, "Пока что нет работы")
        bot.send_message(call.message.chat.id, "Хочешь получать рассылку - напиши - \n/subscribeCitizenFullTime")

    elif call.data == "ImmigrantFullTime":
        for i in viewSpecialJobs('Imigrant(FullTime)'):
            jobString = ''
            for var in i:
                jobString = jobString + " " + var
            bot.send_message(call.message.chat.id, jobString)
        bot.send_message(call.message.chat.id, "Хочешь получать рассылку - напиши - \n/subscribeImmigrantFullTime")

    elif call.data == "PassportPartTime":
        for i in viewSpecialJobs('Citizen(PartTime)'):
            jobString = ''
            for var in i:
                jobString = jobString + " " + var
            bot.send_message(call.message.chat.id, jobString)
        bot.send_message(call.message.chat.id, "Хочешь получать рассылку - напиши - \n/subscribeCitizenPartTime")


    elif call.data == "ImmigrantPartTime":
        for i in viewSpecialJobs('Imigrant(PartTime)'):
            jobString = ''
            for var in i:
                jobString = jobString + " " + var
            bot.send_message(call.message.chat.id, jobString)
        bot.send_message(call.message.chat.id, "Хочешь получать рассылку - напиши - \n/subscribeImmigrantPartTime")


    elif call.data == "MassaPartTime":
        for i in viewSpecialJobs('Masa'):
            jobString = ''
            for var in i:
                jobString = jobString + " " + var
            bot.send_message(call.message.chat.id, jobString)
        bot.send_message(call.message.chat.id, "Хочешь получать рассылку - напиши - \n/subscribeMasa")





if __name__ == "__main__":
    threading.Thread(target=subscribing).start()
    try:
        bot.polling(none_stop = True)
    except:
        print("Oooops")
