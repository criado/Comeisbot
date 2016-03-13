# -*- coding: utf-8 -*-

import praw
import time

def notifyOp(bot, text):
    '''
    Recorre el archivo de chat_id suscritos y les notifica con el nuevo capítulo
    de One Piece
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
    En el archivo private/op_last_post está el id del último post procesado.
    Se leen los 10 ultimos posts y se busca un nuevo capítulo de One Piece en
    reddit o el ultimo post procesado. Si no encuentra ninguno de los dos,
    repite la busqueda con el doble de posts y así sucesivamente.
    Cuando encuentra alguna de las dos cosas actualiza el ultimo post procesado.
    En el caso de encontrar nuevo capitulo notifica a todos los suscriptores
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
    Abre un archivo y después de comprobar que el chat no estaba suscrito
    anteriormente (si lo estaba lo notifica y sale) lo suscribe añadiendo el
    chat_id al archivo. También busca el último capítulo y lo manda al chat
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


