# -*- coding: utf-8 -*-

import praw
import threading
import re

#TODO Capturar la excepción de error de SSL, en vez de hacer except:

def notifyOp(bot, text):
    '''
    It iterates over the subscribers file and send a notification message to
    each chat
    '''
    f = open('private/OnePiece/subscribers', 'r')
    id = f.readline()
    #TODO mirar si hay que quitar el \n al string
    while id != '':
        bot.sendMessage(id, text='¡Leed OP!'
                ' ¡Ha salido un nuevo capítulo!')
        bot.sendMessage(id, text=text)
        id = f.read()

def extract_chapter(text):
    return re.findall(r'\d+', text)[0]

def parse_post(text):
    urls =re.findall(',(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|'+
                     '[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\('+
                     '[^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|['+
                     '^\s`!()\[\]{};:\'".,<>?«»“”‘’]))', text);
    urls=[u for u in urls if u!="http://vizmanga.com/"]

    chapter=re.findall(r'\"(.+?)\"',text)[0]

    res=extract_chapter(text)+": "+chapter+":\n"
    for u in urls: res+=u+"\n"
    return res

def check_one_piece(bot):
    '''
    The last reddit id post the bot has processed is in the file
    'private/OnePiece/last_post'. This method reads the last 10 posts and searches
    for a new One Piece chapter or for the last post processed. If it doesn't
    find any of those it repeats the search doubling the number of posts and so
    on.
    When it finds a new chapter or the last post processed it updates the file
    with the last post processed. If it had found a new chapter, it notifies it
    to all the subscriptors.
    '''
    f = open('private/OnePiece/last_post', 'r')
    last_post = f.read()
    f.close()
    f = open('private/OnePiece/last_chapter', 'r')
    last_chapter = f.read()
    f.close()

    r = praw.Reddit(user_agent='comeis_op')
    subreddit = r.get_subreddit('OnePiece')
    try:
        new_last_post = subreddit.get_new(limit=1).next().id
    except:
        return

    if new_last_post == last_post:
        return

    #TODO Comprobar si algo sale mal para que no se quede en este bucle infinito
    limit = 10
    while True:
        try:
            for submission in subreddit.get_new(limit=limit):
                if submission.id == last_post:
                    f = open('private/OnePiece/last_post', 'w')
                    f.write(new_last_post)
                    f.close()
                    break
                op_text = submission.link_flair_text
                if op_text is None:
                    continue
                if 'Current Chapter' in op_text:
                    new_last_chapter = extract_chapter(submission.selftext)
                    if last_chapter == new_last_chapter:
                        break
                    f = open('private/OnePiece/last_post', 'w')
                    f.write(new_last_post)
                    f.close()
                    f = open('private/OnePiece/last_chapter', 'w')
                    f.write(new_last_chapter)
                    f.close()
                    notifyOp(bot, parse_post(submission.selftext))
                    break
            else:
                limit *= 2
                continue
            break
        except:
            return

#def subscribe_op():
def subscribe_op(bot, update):
    '''
    It opens a file and after having checked that the chat wasn't subscribed
    it subscribes the chat appending its id to the file. It also searches for
    the last chapter and sends it to the chat
    '''
    f = open('private/OnePiece/subscribers', 'r+')
    id = update.message.chat_id
    line = f.readline()
    while line != '':
        if line == str(id) + '\n':
            bot.sendMessage(update.message.chat_id, text='Ya estabas suscrito!')
            f.close()
            return
        line = f.readline()

    r = praw.Reddit(user_agent='comeis_op')
    subreddit = r.get_subreddit('OnePiece')

    limit = 300
    while True:
        #try:
            for submission in subreddit.get_new(limit=limit):
                op_text = submission.link_flair_text
                if op_text is None:
                    continue
                if 'Current Chapter' in op_text:
                    bot.sendMessage(id, text='Acabas de suscribirte a las notificaciones de'
                           ' One Piece del Comeisbot. Usamos reddit para mandarte una'
                           ' notificación cuando sale el capítulo y con un enlace')
                    bot.sendMessage(id, text='El último capítulo es este:')
                    asdf = parse_post(submission.selftext)
                    bot.sendMessage(id, text=asdf)
                    f.write(str(id) + '\n')
                    f.close()
                    return
     #   except:
      #      print 'Excepcion de suscripcion'
       #     return
            limit  *= 2

def unsubscribe_op(bot, update):
    '''
        TODO
        Para hacerlo hay que cambiar la manera de suscribirse, que ahora solo es un
        archivo donde se guardan cosas
    '''
    pass

def run_op(bot):
    check_one_piece(bot)
    threading.Timer(600, run_op, [bot]).start()
