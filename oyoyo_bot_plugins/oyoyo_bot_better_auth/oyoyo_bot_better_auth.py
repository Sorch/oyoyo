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


from StringIO import StringIO

from sqlalchemy import Table, Column, Integer, String
from sqlalchemy.orm import mapper

from oyoyo import helpers
from oyoyo.util import parse_name
from oyoyo.cmdhandler import CommandHandler

from oyoyo_bot import db
from oyoyo_bot.app import auth, config
from oyoyo_bot.authplugins import OwnerAuth

import logging
log = logging.getLogger(__name__)


AuthTable = Table("better_auth", db.meta,
    Column('id', Integer, primary_key=True),
    Column('user', String(100)),
    Column('command', String(100)),
)

class AuthEntry(object):
    def __init__(self, user, command):
        self.user = user
        self.command = command

    @classmethod 
    def get(klass, id):
        return db.session.query(klass).get(int(id))

    @classmethod
    def getAll(klass):
        return db.session.query(klass).all()

    @classmethod
    def getForUser(klass, name, command=None):
        q = db.session.query(klass).filter_by(user=name)
        if command:
            q.filter_by(command=command)
        return q.all()

mapper(AuthEntry, AuthTable)


class Commands(CommandHandler):
    """ tell someone something the next time they join """
    def __call__(self, sender, dest, arg):
        t = arg.split(' ', 1)
        target, function = t[0], t[1]
        sender = parse_name(sender)[0]

        entry = AuthEntry(target, function)
        db.session.save(entry)
        db.session.commit()
        helpers.msgOK(self.client, dest, sender)
auth(Commands)


class Auth(OwnerAuth):
    def __call__(self, sender, dest, command, arg=None):
        return (OwnerAuth.__call__(self, sender, dest, command, arg) or 
                len(AuthEntry.getForUser(sender, command)))
        



