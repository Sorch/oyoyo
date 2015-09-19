# Introduction #

Below describes and shows examples for some more advanced usage of the Oyoyo IRC library.

This page is a work in progress.



# Conf-File based Bot Design Pattern #

Below outlines a design pattern you can use to create a bot that loads its information from a configuration file.

The principle of the design pattern is to define a class that inherits from `IRCClient` and whose `__init__` accepts a configuration file path. The init then parses the configuration file, stores the information in self.config, and then passes it on to `IRCClient.__init__`. Another note is that the `connect_cb` (connect callback) can then be a bound method on the instance.

In addition to this client class, you then define a command handler class, inheriting from `DefaultCommandHandler`, as you normally would. Such a class already has the client's config instance available through `self.client.config`, if it would ever need to act based on that.

The illustration below will use a yaml-based configuration file, although any format works in practice.

```
#!/usr/bin/python
from oyoyo import helpers
from oyoyo.client import IRCApp, IRCClient
from oyoyo.cmdhandler import DefaultCommandHandler
import yaml


class Config(object):
     def __init__(self, host, port, nick, channel):
          self.host = host
          self.port = port
          self.nick = nick
          self.channel = channel   


class BotClient(IRCClient):
    def __init__(self, conf_file):
        conf_yaml = yaml.load(open(conf_file))
        self.config = Config(conf_yaml['host'], conf_yaml['port'],
                             conf_yaml['nick'], conf_yaml['channel'])
        IRCClient.__init__(self, BotHandler, host=self.config.host,
                           port=self.config.port, nick=self.config.nick,
                           connect_cb=self.connect_cb)

    def connect_cb(self, unusued_cli):
        helpers.join(self, self.config.channel)


class BotHandler(DefaultCommandHandler):
    def privmsg(self, prefix, chan, msg):
        print prefix, chan, msg


if __name__ == '__main__':
     cli = BotClient('config.yaml')
     conn = cli.connect()
     while True:
         conn.next()

```



# Logging #

Oyoyo uses the python [logging](http://docs.python.org/library/logging.html) library by default to write information about what's going on with the connection and how it's being handled.

The logging module uses different logging "levels" to categorize different types of logging messages. The different levels follow a hierarchy, and you can set what you want to be printed on the screen by calling a function on the logging module.
```
import logging                            # defines DEBUG, INFO, WARNING, ERROR, CRITICAL constants
logging.basicConfig(level=logging.DEBUG)  # everything above DEBUG will now be printed 
```

Below is a brief synopsis of different types of messages sent to the logger.
| **Logging Level** | Information |
|:------------------|:------------|
|ERROR              |An exception occurred while calling a method in a command handler, includes formatted traceback|
|ERROR              |An error while reading the connection, includes formatted traceback|
|INFO               |Any message sent to IRC socket|
|INFO               |Beginning to connect IRC server|
|INFO               |Closing connection to IRC server|
|INFO               |Adding a new client to an IRCApp instance|
|INFO               |Adding a new timer callback to an IRCApp instance|
|INFO               |Stopping the IRCApp loop because no more clients left alive|
|INFO               |Calling a new timer callback|
|DEBUG              |Processing a command in the command handler, including the function repr|
|DEBUG              |A command was received that was not implemented by the command handler|