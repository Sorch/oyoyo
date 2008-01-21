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

from oyoyo.cmdhandler import DefaultCommandHandler, BotMixin
from oyoyo.client import IRCClient, IRCApp
from oyoyo import helpers


class LogBot(BotMixin):
    def processBotCommand(self, cmd, sender):
        if sender == 'd1223m!n=dunk@unaffiliated/d1223m' and cmd == 'quit':
            self.client.quit()


class LoggingHandler(DefaultCommandHandler, LogBot):
    def privmsg(self, prefix, args):
        print "[%s %s] %s" % (args[0], prefix, args[1])
        self.tryBotCommand(prefix, args)


def make_app():
    import logging
    import sys

    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s')

    def connect_cb(c):
        for room in sys.argv[2:]:
            helpers.join(c, '#%s' % room)

    app = IRCApp()

    cli = IRCClient(LoggingHandler, 
        nick="oyoyo",
        host=sys.argv[1],
        port=6667,
        connect_cb=connect_cb)
    app.addClient(cli)

    def msg_dunk():
        helpers.msg(cli, "#test", "hello!")

    app.addTimer(15, msg_dunk)

    app.run()



