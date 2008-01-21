import sys
import socket
import traceback
import time

from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo.client import parse_raw_irc_command

from oyoyo_ircd import helpers

import logging 
log = logging.getLogger(__name__)

config = None


class ServerCommandHandler(DefaultCommandHandler):

    def nick(self, prefix, args):
        self.client.nick = args[0]
        server = self.client.server
        try:
            existing = server.nicks[args[0]]
        except KeyError:
            server.nicks[args[0]] = self.client
        else:
            self.client.sendClient( helpers.nicknameinuse() )

    def user(self, prefix, args):
        self.client.username = args[0]
        self.client.hostname = args[1]
        self.client.servername = args[2]
        self.client.realname = args[3]

        self.client.calcPrefix()

        log.info('user username=%s hostname=%s servername=%s realname=%s'
             % (args[0], args[1], args[2], args[3]))

        self.client.sendWelcome()

    def join(self, prefix, args):
        self.client.server.join(self.client, args[0])

    def privmsg(self, prefix, args):
        log.debug('privmsg prefix=%s args=%s' % (prefix, str(args)))
        dest, message = args
        message = ":" + message
        if dest.startswith('#'):
            log.debug('room message')
            try:
                room = self.client.server.rooms[dest]
            except KeyError:
                log.info('no such room %s' % dest)
            else:
                room.send([self.client.prefix, 'PRIVMSG', dest, message], 
                    fromclient=self.client)
        else:
            log.debug('user message')
            try:
                cli = self.client.server.nicks[dest]
            except KeyError:
                log.info('no suck user %s' % dest)
            else:
                cli.send(self.client.prefix, 'PRIVMSG', dest, message)


class Connection(object):
    bufsize = 1024

    def __init__(self, server, connection, address):
        self.server = server
        self.connection = connection
        self.address = address
        self.host, self.port = address
        self.handler = ServerCommandHandler(self)

        self.nick = None
        self.username = None
        self.realname = None
        self.prefix = None

        self.rooms = []

    def __str__(self):
        return "<Connection %s>" % str(self.address)

    def calcPrefix(self):
        self.prefix = ":%s!n=%s@%s" % (self.nick, self.username, self.host)

    def connect(self):
        buffer = ""
        while 1:
            try:
                buffer += self.connection.recv(self.bufsize)
            except socket.error, e:
                if e[0] != 11:
                    raise e
            
            data = buffer.split('\n')
            if len(buffer) > 1:
                buffer = data[-1]
                data = data[:-1]
            else: 
                buffer = ""
            if data:
                for thing in data:
                    log.debug('recv %s' % thing)
                    if not thing: 
                        continue
                    try:
                        prefix, cmd, args = parse_raw_irc_command(thing)   
                    except Exception, e:
                        log.error('parse raw command failed on "%s"')
                        log.error(traceback.format_exc())
                        continue

                    log.debug('%s %s %s %s' % (self, prefix, cmd, args))
                    self.processCommand(prefix, cmd, args)
            yield True

    def processCommand(self, prefix, cmd, args):
        try:
            f = getattr(self.handler, cmd)
        except AttributeError:
            self.handler._unhandled(cmd, prefix, args)
        else:
            f(prefix, args)

    def send(self, *args):
        log.debug('%s --> %s' % (self, args))
        self.connection.send("%s\n" % " ".join([str(a) for a in args]))

    def sendServer(self, args):
        dest = ":%s" % self.server.host
        self.send(dest, *args)

    def sendClient(self, args):
        self.send(self.prefix, *args)   

    def sendWelcome(self):
        cli = self
        nick = self.nick

        cli.sendServer( helpers.welcome(nick, ':Welcome') )
        cli.sendServer( helpers.yourhost(nick, ':your host is me!') )
        cli.send(      *helpers.notice(nick, ':your host is me!') )
        cli.sendServer( helpers.luserclient(nick, ':there are %s connected users' %
            len(self.server.connections)) )
        cli.sendServer( helpers.luserop(nick, ':there are 0 ops') )
        cli.sendServer( helpers.luserchannels(nick, ':there are %s rooms' % 
            len(self.server.rooms)) )

        cli.sendServer( helpers.motdstart(nick, ':oyoyo motd') )
        cli.sendServer( helpers.motd(nick, ':motd!') )
        cli.sendServer( helpers.endofmotd(nick, ':end of motd') )


class Room(object):
    def __init__(self, server, name):
        self.server = server
        self.name = name
        self.members = []
        self.topic = "Welcome to %s" % self.name
        self.topic_user = "oyoyo_ircd"
        self.topic_time = int(time.time())

    def addMember(self, client):
        self.members.append(client)

        client.sendClient( helpers.join(self.name) )

        client.sendServer( helpers.currenttopic(client.nick, self.name, 
            ":"+self.topic) )
        client.sendServer( helpers.topicinfo(client.nick, self.name, 
            self.topic_user, self.topic_time) )
        client.sendServer( helpers.namreply(client.nick, "=", self.name, 
            " ".join(map(lambda c: c.nick, self.members))) )
        client.sendServer( helpers.endofnames(client.nick, self.name, 
            ":End of /NAMES list") )

        self.send([client.prefix, 'JOIN', self.name], fromclient=client)

    def sendClient(self, args, fromclient=None):
        for client in self.members:
            if client == fromclient: continue
            client.sendClient(args)

    def send(self, args, fromclient=None):
        for client in self.members:
            if client == fromclient: continue
            client.send(*args)


class IRCD(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.running = False
        self.buf = 1024
        self.socket = None

        self.connections = {}
        self.nicks = {}

        self.rooms = {}

    def run(self):
        self.running = True
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            log.info('listening on %s:%s' % (self.host, self.port))
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            log.info('waiting for bind...')
            while True:
                try:
                    self.socket.bind((self.host, self.port))
                except socket.error, e:
                    if e[0] == 98:
                        continue
                    raise e
                else:
                    break
            log.info('bound')
                
            self.socket.setblocking(0)
            self.socket.listen(5)

            self.loop()

            #while self.running:
            #    data, addr = s.recvfrom(self.buf)
            #    log.debug("%s %s" % (addr, data))
        except Exception, e:
            log.error('callback raised %s' % e)
            log.error(traceback.format_exc())

        finally: 
            log.info('closing socket')
            self.socket.close()

    def loop(self):
        s = self.socket
        while self.running:
            try:
                connection, address = s.accept()
            except socket.error, e:
                if e[0] != 11:
                    raise e
            else:
                log.info('connection %s %s' % (connection, address))
                connection.setblocking(0)
                con = Connection(self, connection, address)
                self.connections[con] = con.connect()

            for con, con_obj in self.connections.iteritems():
                try:
                    con_obj.next()
                except StopIteration:
                    log.info('removing client %s' % con)
                    del self.connections[con]

            time.sleep(0.5)

    def join(self, client, room_name):
        room_name = room_name.lower().strip()
        try:
            room = self.rooms[room_name]
        except KeyError:
            room = self.rooms[room_name] = Room(self, room_name)
        room.addMember(client)


def make_config():
    from StringIO import StringIO

    defaults = StringIO("""
# oyoyo ircd config

# several options use entry point syntax to link to external
# modules/functions/classes
# entrypoint syntax is
#       some.module:some.attr [extra1,extra2]

[database]
# connection uri - see sqlachemy docs for full spec
uri = sqlite:///mydb.db
#uri = sqlite:///:memory:
#uri = mysql://user:password@localhost/oyoyo
# echo's database commands to log
echo = False

[logging]
# one of DEBUG, INFO, WARN, ERROR
level = DEBUG
# filename to log to, set to an empty string to log to stdout
filename =
#filename = oyoyo.log
#filename = oyoyo.log
# should be 'a' or 'w'
filemode = a

[server]
hostname = localhost
port = 6667
"""

    config = ConfigObj(defaults)
    for conf in sys.argv[1:]:
        if conf.startswith('-'):
            continue
        c = ConfigObj(conf)
        config.merge(c)
    return config


def make_app():
    global config 
    config = make_config()

    logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s',
        filename=config['logging']['filename'],
        filemode=config['logging']['filemode'],
    )

    ircd = IRCD(config['server']['hostname'], 
        int(config['server']['port']))

    config.filename = 'lastrun.ini'
    config.write()

    if '-c' in sys.argv:
        return 

    ircd.run()









