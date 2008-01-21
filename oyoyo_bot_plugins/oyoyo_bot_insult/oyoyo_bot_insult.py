import random

from sqlalchemy import Table, Column, Integer, String
from sqlalchemy.orm import mapper

from oyoyo import helpers
from oyoyo_bot.app import auth
from oyoyo_bot import db
from oyoyo.util import parse_name
from oyoyo.cmdhandler import CommandHandler

import logging
log = logging.getLogger(__name__)

InsultsTable = Table("insults", db.meta,
    Column('id', Integer, primary_key=True),
    Column('insult', String(100)),
)

class Insult(object):
    def __init__(self, insult):
        self.insult = insult

    def __str__(self):
        return self.insult

    @classmethod 
    def get(klass, id):
        log.debug('get %s' % id)
        return db.session.query(klass).get(int(id))

    @classmethod
    def getRandom(klass):
        total = db.session.query(klass).count()
        log.debug('total %s' % total)
        return klass.get(random.randint(1, total))

    @classmethod
    def getAll(klass):
        return db.session.query(klass).all()

    
mapper(Insult, InsultsTable)


class OyoyoInsult(CommandHandler):
    """ insult someone """
    def __call__(self, sender, dest, arg=None):
        t = (arg or parse_name(sender)[0]).split(' ', 1)
        target, id = t[0], t[1:]
        
        helpers.msg(self.client, dest, "%s %s" % (target, 
            Insult.get(id[0]) if id else Insult.getRandom()) )

    @auth
    def add(self, sender, dest, arg):
        """ add an insult to the datbase """
        insult = Insult(arg)
        db.session.save(insult)
        db.session.commit()
        helpers.msgOK(self.client, dest, parse_name(sender)[0])

    @auth
    def list(self, sender, dest):
        """ list all insults """
        sender = parse_name(sender)[0]
        for insult in Insult.getAll():
            helpers.msg(self.client, sender, "%s: %s" % (insult.id, insult.insult))

    @auth
    def delete(self, sender, dest, arg):
        """ delete an insult, arg is insult id """
        insult = Insult.get(int(arg))   
        db.session.delete(insult)
        db.session.commit()
        helpers.msgOK(self.client, dest, parse_name(sender)[0])
        
        
        

