# -*- coding: utf-8 -*-

import praw
import time

def notifyOp(bot, text):
    '''
    It iterates over the subscribers file and send a notification message to
    each chat
    '''
    f = open('private/subscribers', 'r')
    id = f.read()
    while id is not '':
        bot.sendMessage(id, text='¡Leed OP!'
                ' ¡Ha salido un nuevo capítulo!')
        bot.sendMessage(id, text=text)
        id = f.read()

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
    new_last_post = subreddit.get_new(limit=1).id
    if new_last_post == last_post:
        return

    #TODO Comprobar si algo sale mal para que no se quede en este bucle infinito
    while True:
        limit = 10
        for submission in subreddit.get_new(limit=limit):
            if submission.id is last_post:
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
                notifyOp(bot, submission.selftext)
                break
        limit *= 2



def subscribe_op(bot, update):
    '''
    It opens a file and after having checked that the chat wasn't subscribed
    it subscribe the chat appending its id to the file. It also searches for the
    last chapter and sends it to the chat
    '''
    f = open('private/subscribers', 'r+')
    id = update.message.chat_id
    line = f.readline()
    while line != '':
        if line == id + '\n':
            bot.sendMessage(update.message.chat_id, text='Ya estabas suscrito!')
            f.close()
            return

    r = praw.Reddit(user_agent='comeis_op')
    subreddit = r.get_subreddit('OnePiece')
    while True:
        limit = 500
        for submission in subreddit.get_new(limit=limit):
            op_text = submission.link_flair_text
            if op_text is None:
                continue
            if 'Current Chapter' in op_text:
                bot.sendMessage(id, text='Ya estás suscrito a las notificaciones de'
                       ' One Piece del Comeisbot. Usamos reddit para mandarte una'
                       ' notificación cuando sale el capítulo y con un enlace')
                bot.sendMessage(id, text='El último capítulo es este:')
                bot.sendMessage(id, text=submission.selftext)
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


