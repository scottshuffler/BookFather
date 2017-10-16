import os
import telebot
import sqlite3

bot = telebot.TeleBot(os.environ['BOT_API_TOKEN'])


def connect():
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    return conn, c


def disconnect(conn, c):
    c.close()
    conn.close()


def startup():
    conn, c = connect()

    sql_books = 'create table if not exists books (id INTEGER PRIMARY KEY,author VARCHAR,title VARCHAR,date int,finished int)'
    sql_users = 'create table if not exists users (id INTEGER PRIMARY KEY,name VARCHAR)'
    sql_read = 'create table if not exists read_books (book int,user int)'
    c.execute(sql_books)
    c.execute(sql_users)
    c.execute(sql_read)

    # c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    # print(c.fetchall())
    conn.commit()
    disconnect(conn, c)


@bot.message_handler(commands=['join'])
def send_welcome(message):
    print message.from_user
    if message.from_user.username is None:
        bot.reply_to(message, u"Please set a username and try again!")
    else:
        conn, c = connect()
        sql = 'INSERT INTO users VALUES(?,?);'
        try:
            c.execute(sql, (message.from_user.id, str(message.from_user.username)))
            conn.commit()
            bot.reply_to(message, u"Welcome, " + message.from_user.username + "!")
        except Exception as e:
            bot.reply_to(message, u"You're already in the club!")
            print e
        disconnect(conn, c)


@bot.message_handler(commands=['finished'])
def send_finished(message):
    print message.from_user
    conn, c = connect()
    sql = 'SELECT count(*) from users where id=?;'
    user_id = unicode(message.from_user.id)
    print(user_id)
    c.execute(sql, (user_id,))
    if c.fetchone()[0] is 1:
        try:
            c.execute('SELECT id FROM books WHERE finished=0')
            book_id = c.fetchone()[0]
            c.execute('SELECT count(*) FROM read_books WHERE user=? AND book=?', (user_id, book_id))
            if c.fetchone()[0] is 0:
                c.execute('INSERT INTO read_books VALUES(?,?)', (book_id, user_id))
                conn.commit()
                bot.reply_to(message, u"Nice! I'll mark you as done!")
            else:
                bot.reply_to(message, u"You've already finished this book!")
        except Exception as e:
            bot.reply_to(message, u"There doesn't seem to be an active book")
            print e
    else:
        bot.reply_to(message, u"You must join the club first! Use: /join")
    disconnect(conn, c)


@bot.message_handler(commands=['begin'])
def send_begin(message):
    text = message.text.split(',')
    text[0] = text[0].split(' ', 1)[-1]
    conn, c = connect()
    if len(text) is 3:
        c.execute("SELECT count(*) FROM books WHERE finished=0")
        if c.fetchone()[0] is 0:
            sql = 'INSERT INTO books (author,title,date,finished) VALUES(?,?,?,?);'
            try:
                c.execute(sql, (text[0].strip(), text[1].strip(), text[2].strip(), 0))
                conn.commit()
                bot.reply_to(message, u"Added " + text[1] + " by " + text[0]
                             + " ending on " + text[2] + "! Enjoy!")
            except Exception as e:
                bot.reply_to(message, u"Failed to add book!")
                print e
        else:
            bot.reply_to(message, u"Sorry but it looks like a book is already being read")
    else:
        bot.reply_to(message, u"Too few arguments")
    disconnect(conn, c)


@bot.message_handler(commands=['end'])
def send_end(message):
    conn, c = connect()
    text = message.text.split(' ', 1)[-1].strip()
    print text
    if len(text) > 0:
        c.execute("UPDATE books SET finished=1 WHERE title=?", (text,))
        conn.commit()
        bot.reply_to(message, u"Book ended! Discuss!")
    disconnect(conn, c)


@bot.message_handler(commands=['current'])
def send_current(message):
    conn, c = connect()
    # conn = sqlite3.connect('books.db')
    # c = conn.cursor()
    c.execute("SELECT title from books WHERE finished=0")
    try:
        title = c.fetchone()[0]
        bot.reply_to(message, u"Current book is " + title)
    except Exception as e:
        bot.reply_to(message, u"There is no current book")
        print e
    disconnect(conn, c)


startup()
bot.polling()
