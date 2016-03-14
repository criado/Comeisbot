# -*- coding: utf-8 -*-

import praw
import time
import sched
import threading

#def notifyOp(text):
def notifyOp(bot, text):
    '''
    It iterates over the subscribers file and send a notification message to
    each chat
    '''
    f = open('private/subscribers', 'r')
    id = f.readline()
    #TODO mirar si hay que quitar el \n al string
    while id != '':
        #print 'leed op'
        #'''
        bot.sendMessage(id, text='¡Leed OP!'
                ' ¡Ha salido un nuevo capítulo!')
        bot.sendMessage(id, text=text)
        #'''
        id = f.read()

#def check_one_piece():
def check_one_piece(bot):
    '''
    The last reddit id post the bot has processed is in the file
    'private/op_last_post'. This method reads the last 10 posts and searches
    for a new One Piece chapter or for the last post processed. If it doesn't
    find any of those it repeats the search doubling the number of posts and so
    on.
    When it finds a new chapter or the last post processed it updates the file
    with the last post processed. If it had found a new chapter, it notifies it
    to all the subscriptors.
    '''
    f = open('private/op_last_post', 'r')
    last_post = f.read()
    f.close()

    r = praw.Reddit(user_agent='comeis_op')
    subreddit = r.get_subreddit('OnePiece')
    new_last_post = subreddit.get_new(limit=1).next().id
    #print 'new_last_post ', new_last_post
    if new_last_post == last_post:
        return

    #TODO Comprobar si algo sale mal para que no se quede en este bucle infinito
    limit = 10
    while True:
        for submission in subreddit.get_new(limit=limit):
            if submission.id == last_post:
                f = open('private/op_last_post', 'w')
                f.write(new_last_post)
                f.close()
                break
            op_text = submission.link_flair_text
            if op_text is None:
                continue
            if 'Current Chapter' in op_text:
                f = open('private/op_last_post', 'w')
                f.write(new_last_post)
                f.close()
                #notifyOp(submission.selftext)
                notifyOp(bot, submission.selftext)
                break
        else:
            limit *= 2
            continue
        break



#def subscribe_op():
def subscribe_op(bot, update):
    '''
    It opens a file and after having checked that the chat wasn't subscribed
    it subscribe the chat appending its id to the file. It also searches for the
    last chapter and sends it to the chat
    '''
    f = open('private/subscribers', 'r+')
   # id = 'asdf1234'
    id = update.message.chat_id
    line = f.readline()
    while line != '':
        if line == id + '\n':
            #print 'ya estabas suscrito'
            bot.sendMessage(update.message.chat_id, text='Ya estabas suscrito!')
            f.close()
            return
        line = f.readline()

    r = praw.Reddit(user_agent='comeis_op')
    subreddit = r.get_subreddit('OnePiece')

    limit = 300
    while True:
        asdf = False
        for submission in subreddit.get_new(limit=limit):
            op_text = submission.link_flair_text
            if op_text is None:
                continue
            if 'Current Chapter' in op_text:
                if asdf is False:
                    asdf = True
                    continue

                '''
                print 'te he suscrito'
                print submission.selftext
                #'''
                bot.sendMessage(id, text='Ya estás suscrito a las notificaciones de'
                       ' One Piece del Comeisbot. Usamos reddit para mandarte una'
                       ' notificación cuando sale el capítulo y con un enlace')
                bot.sendMessage(id, text='El último capítulo es este:')
                bot.sendMessage(id, text=submission.selftext)
                #'''
                f.write(id + '\n')
                f.close()
                return
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
    threading.Timer(360, run_op(bot)).start()

if __name__ == '__main__':
    run_op()
