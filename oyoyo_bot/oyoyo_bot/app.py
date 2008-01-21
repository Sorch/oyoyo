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

import sys
import inspect
import traceback
import new

import pkg_resources

from oyoyo.cmdhandler import CommandHandler, BotCommandHandler, DefaultBotCommandHandler
from oyoyo.cmdhandler import CommandError
from oyoyo.cmdhandler import protected

from oyoyo.client import IRCClient, IRCApp
from oyoyo import helpers

from configobj import ConfigObj

import logging
log = logging.getLogger(__name__)

app = None
config = None


def auth(func):
    """ decorator to add authentication to a command """
    func.auth = True
    return func


def extendCommandClassWithEP(klass, ep, client):
    log.info('adding %s as %s' % (ep.name, ep))
    try:
        obj = ep.load()
        if not inspect.isfunction(obj):
            setattr(klass, ep.name, obj(client))
        else:
            setattr(klass, ep.name, new.instancemethod(obj, klass))
    except Exception, e:
        log.error('failed to load %s %s' % (ep.name, e))
        log.error(traceback.format_exc())


def extendCommandClass(working_set, klass, key, client):
    """ extend a class with objects from entrypoints """
    for ep in working_set.iter_entry_points(key): 
        extendCommandClassWithEP(klass, ep, client)


def getPkgResourcesWorkingSet():
    if config['plugins'].as_bool('load_all'): 
        working_set = pkg_resources.working_set
    else:
        working_set = pkg_resources.WorkingSet([])

    if config['plugins']['load_from_dir']:
        log.info('loading from %s' % config['plugins']['load_from_dir'])
        distributions, errors = working_set.find_plugins(
            pkg_resources.Environment([config['plugins']['load_from_dir']])
        )
        log.info('distributions %s' % distributions)
        map(working_set.add, distributions)
        if errors: 
            log.info("Couldn't load %s" % errors)
    return working_set


class BotCommands(DefaultBotCommandHandler):
    def __init__(self, client):
        DefaultBotCommandHandler.__init__(self, client)

        working_set = getPkgResourcesWorkingSet()
        extendCommandClass(working_set, self, 'oyoyo_bot.commands', client)  

        for command, fnc in config['commands'].iteritems():
            ep = pkg_resources.EntryPoint.parse("%s = %s" % (command, fnc))
            if not ep.dist: 
                ep.dist = pkg_resources.get_distribution('oyoyo_bot')
            extendCommandClassWithEP(self, ep, client)

    @protected
    def getVisibleCommands(self, obj=None):
        obj = obj or self
        cmds = DefaultBotCommandHandler.getVisibleCommands(self, obj)
        if config['help'].as_bool('hide_auth_commands'):
            return [c for c in cmds if not hasattr(getattr(obj, c), 'auth')]
        else:
            return ["@%s"%c if hasattr(getattr(obj, c), 'auth') else c
                    for c in cmds]

    @protected
    def run(self, command, sender, dest, *arg):
        log.info("running command sender=%s, dest=%s, command=%s, arg=%s",
            sender, dest, command, arg)
        try:
            f = self.get(command)
        except CommandError, e:
            helpers.msg(self.client, dest, str(e))
            return

        if (hasattr(f, 'auth') and 
            not self.client.command_handler.auth(sender, dest, command, *arg)):
            helpers.msg(self.client, dest, 
                "sorry, you dont have permission to do that")
            return

        try:
            f(sender, dest, *arg)
        except Exception, e:
            log.error('command %s raised %s' % (command, e))
            log.error(traceback.format_exc())
            helpers.msg(self.client, dest, "sorry, there was an error")

    @auth
    def quit(self, sender, dest):
        log.info('told to quit by %s' % sender)
        app.stop()

    @auth 
    def join(self, sender, dest, arg):
        log.info('told to join %s by %s' % (arg, sender))
        helpers.join(self.client, arg.strip())

    @auth
    def part(self, sender, dest, arg):
        log.info('told to join %s by %s' % (arg, sender))
        helpers.part(self.client, arg.strip())


def loadAuthPlugin(plugin, args):
    log.info('loadAuthPlugin %s %s' % (plugin, args))
    ep = pkg_resources.EntryPoint.parse("auth = %s" % plugin)
    if not ep.dist:
        # weird...
        log.warning('no distribution set loading auth plugin')
        log.warning('setting to oyoyo')
        ep.dist = pkg_resources.get_distribution('oyoyo_bot')
    f = ep.load()
    log.info('loaded auth %s' % f)
    return f(*args)


def loadListenerPlugins(working_set, key, client):
    listeners = []
    for ep in working_set.iter_entry_points(key): 
        listeners.append(ep.load()(client))
    return listeners


class OyoyoBotCommandHandler(BotCommandHandler):
        
    def __init__(self, client, command_handler, auth):
        BotCommandHandler.__init__(self, client, command_handler)
        self.auth = auth 
        working_set = getPkgResourcesWorkingSet()
        self.listeners = loadListenerPlugins(working_set, 
            'oyoyo_bot.listeners', client)

    @protected
    def unhandled(self, command, *args):
        found = False
        for listener in self.listeners:
            try:
                listener.run(command, *args)
            except Exception, e:
                log.error('listener raised %s' % e)
                log.error(traceback.format_exc())
            else:
                found = True
        if not found:
            log.debug('unhandled command %s(%s)' % (command, args))

    def privmsg(self, prefix, dest, msg):
        BotCommandHandler.privmsg(self, prefix, dest, msg)
        self.unhandled('privmsg', prefix, dest, msg)


def make_config():
    from StringIO import StringIO

    defaults = StringIO("""
# oyoyo bot config

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
# should be 'a' or 'w'
filemode = a

[auth]
# plugin ( entry point syntax )
plugin = oyoyo_bot.authplugins:OwnerAuth
# args are split by whitespace and passed to plugin
args = d1223m!n=dunk@unaffiliated/d1223m

[plugins]
# load all plugins found on sys.path
load_all = True
# load eggs from directory
load_from_dir = plugins/

# extra commands to load ( entry point syntax )
[commands]
hello = oyoyo_bot.oneliners:hello
botsnack = oyoyo_bot.oneliners:botsnack

[help]
# hide functions that need authentication
hide_auth_commands = False

# defaults for all servers
[server default]
port = 6667
nick = oyoyo
realname = oyoyo

# specific server connections
#[server irc.freenode.net]
#rooms = test bots 
#identify = oyoyo_nick_serv_pass

""")

    config = ConfigObj(defaults)
    for conf in sys.argv[1:]:
        if conf.startswith('-'):
            continue
        c = ConfigObj(conf)
        config.merge(c)
    return config


def extendConfig(key):
    working_set = getPkgResourcesWorkingSet()
    for ep in working_set.iter_entry_points(key): 
        log.info('extending defaults with %s' % ep)
        obj = ep.load()
        plugin_defaults = ConfigObj(obj)
        config.merge(plugin_defaults)
        

def make_app():
    """ main entry point """

    print "make_app()"
    import logging
    import sys
    from oyoyo_bot import db
        
    global app
    global config

    config = make_config()

    logging.basicConfig(level=getattr(logging, config['logging']['level']),
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=config['logging']['filename'],
                    filemode=config['logging']['filemode'])

    db.engine = db.create_engine(config['database']['uri'],
                    echo=config['database'].as_bool('echo'))
    db.Session.configure(bind=db.engine)
    db.session = db.Session()

    app = IRCApp()

    def serverOrDefault(server, key):
        try:
            return config[server][key]
        except KeyError:
            return config['server default'][key]

    args = [a for a in config['auth']['args'].strip().split(' ') if a]
    auth = loadAuthPlugin(config['auth']['plugin'], args)

    for key in config.iterkeys():
        if not key.startswith('server ') or key == 'server default':
            continue
        server = key.split(' ', 1)[1]

        rooms = serverOrDefault(key, 'rooms').split(' ')
        identify = serverOrDefault(key, 'identify')

        def connect_cb(c):
            if identify: 
                helpers.ns(c, "IDENTIFY", identify)
            for room in rooms:
                helpers.join(c, "#"+room)

        cli = IRCClient( 
            nick=serverOrDefault(key, 'nick'),
            realname=serverOrDefault(key, 'realname'),
            host=server,
            port=int(serverOrDefault(key, 'port')),
            connect_cb=connect_cb)
        cli.command_handler = OyoyoBotCommandHandler(
            cli, BotCommands(cli), auth)

        app.addClient(cli, autoreconnect=True)

    db.meta.create_all(db.engine)
    extendConfig('oyoyo_bot.config')
    config.filename = 'lastrun.ini'
    config.write()

    # to just write a config
    if '-c' in sys.argv:
        return

    app.run()
    print "done."


    



















