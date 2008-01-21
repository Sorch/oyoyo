# Copyright (c) 2008 Duncan Fordyce
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import random
from StringIO import StringIO

from sqlalchemy import Table, Column, Integer, String
from sqlalchemy.orm import mapper

from oyoyo import helpers
from oyoyo_bot.app import auth, config
from oyoyo_bot import db
from oyoyo.util import parse_name
from oyoyo.cmdhandler import CommandHandler

import logging
log = logging.getLogger(__name__)


TellMessagesTable = Table("tell_messages", db.meta,
    Column('id', Integer, primary_key=True),
    Column('from_user', String(100)),
    Column('to_user', String(100)),
    Column('room', String(100)),
    Column('msg', String(255)),
)

class TellMessage(object):
    def __init__(self, from_user, to_user, room, msg):
        self.from_user = from_user
        self.to_user = to_user
        self.room = room
        self.msg = msg

    @classmethod 
    def get(klass, id):
        log.debug('get %s' % id)
        return db.session.query(klass).get(int(id))

    @classmethod
    def getAll(klass):
        return db.session.query(klass).all()

    @classmethod
    def getForUser(klass, name, room=None):
        q = db.session.query(klass).filter_by(to_user=name)
        if room:
            q.filter_by(room=room)
        return q.all()

    @classmethod
    def getCountForUser(klass, name):
        return db.session.query(klass).filter_by(to_user=name).count()

    
mapper(TellMessage, TellMessagesTable)

defaults = StringIO("""
[tell]
max_msgs = 3   
""")


class Commands(CommandHandler):
    """ tell someone something the next time they join """
    def __call__(self, sender, dest, arg):
        t = arg.split(' ', 1)
        target, message = t[0], t[1]
        sender = parse_name(sender)[0]

        if TellMessage.getCountForUser(target) >= int(config['tell']['max_msgs']):
            helpers.msg(self.client, dest, "%s has too many messages already" % target)
            return
    
        msg = TellMessage(sender, target, dest, message)
        db.session.save(msg)
        db.session.commit()
        helpers.msgOK(self.client, dest, sender)

    # TODO, list, remove etc..


class Listener(CommandHandler):
    def join(self, prefix, arg):
        log.info('join %s %s' % (prefix, arg))
        name = parse_name(prefix)[0]
        msgs = TellMessage.getForUser(name, arg)
        for msg in msgs:
            helpers.msg(self.client, arg, "%s: %s said to tell you %s" %
                (msg.to_user, msg.from_user, msg.msg))
            db.session.delete(msg)
        db.session.commit()
           











