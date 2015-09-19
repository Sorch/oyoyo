# Introduction #

This tutorial will show you how to use the Oyoyo IRC library. To begin, first install the library.

## Handlers and Starting a Connection ##
To connect to a single server you need to use oyoyo.client.IRCClient. The
IRCClient class handles all communication with a **single** server. When creating an IRCClient you also need to define a handler class,
which connects messages sent from the server to ideas.

The following is an example of creating an IRCClient and a command handler:

```
#!/usr/bin/python
from oyoyo.client import IRCClient
from oyoyo.cmdhandler import DefaultCommandHandler

class MyHandler(DefaultCommandHandler):
    # Handle messages (the PRIVMSG command, note lower case)
    def privmsg(self, nick, chan, msg):
        print "%s in %s said: %s" % (nick, chan, msg)

cli = IRCClient(MyHandler, host="irc.freenode.net", port=6667, nick="myname")
```

The above code shows a simple handler to that outputs all PRIVMSG commands.

In general, in order to behave on types of commands sent by the server, your handler class should override the methods whose names and parameters associate with the command. To see what kind of commands the server sends, you can override the method `__unhandled__`, and print its \**args. Alternatively, you may consult the IRC specification.**

## Connect callback and joining channels ##
It's very likely that you will want to issue some commands "on connect", for example
joining rooms, sending identify messages etc... This is achieved with an on connect
callback.

The following example builds on the previous example and adds an on connect
callback to automatically identify and join the room '#test'. Notice the use of
oyoyo.helpers which contains commonly used IRC commands.

```
#!/usr/bin/python
from oyoyo.client import IRCClient
from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo import helpers

def connect_callback(cli):
    # Identify to nickserv
    helpers.msg(cli, "NickServ", "IDENTIFY", "my_password")

    # Join the channel '#test'
    helpers.join(cli, "#test")

class MyHandler(DefaultCommandHandler):
    # Handle messages (the PRIVMSG command, note lower case)
    def privmsg(self, nick, chan, msg):
        print "%s in %s said: %s" % (nick, chan, msg)

cli = IRCClient(MyHandler, host="irc.freenode.net", port=6667, nick="myname",
                connect_cb=connect_callback)

....
```

## Single-client looping and Multi-client looping ##
All the previous code will not actually do anything, we still need to connect
( and stay connected )...

```
conn = cli.connect()
while True:
    conn.next()
```

Whats actually happening is connect calls yield, halting execution at a specific
point in the loop, waiting to be called again. This means you can easily create
more than one instance of IRCClient and call them all in a loop. For example:

```
cli_1 = IRCClient(SomeHandler, ...)
cli_2 = IRCClient(SomeHandler, ...)

conn_1 = cli_1.connect()
conn_2 = cli_2.connect()

while 1:
    conn_1.next()
    conn_2.next()
```

Luckily we don't have to deal with multiple connections like this.
oyoyo.client.IRCApp is designed to maintain several IRCClient connections but at the
cost of blocking. It is useful in certain situations and also serves as an example
implementation of an application.

Using IRCApp we can write the last example as:

```
app = IRCApp()
app.addClient( IRCClient(SomeHandler, ...) )
app.addClient( IRCClient(SomeHandler, ...) )
app.run()
```