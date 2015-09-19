# Introduction #

This tutorial describes how to write plugins for Oyoyo Bot

# Writing a new commands #
Commands in Oyoyo Bot can either be classes or functions. Using a class
will allow for "dotted commands" ( ie. insult.add, insult.delete ... ).

## A single command ##
To create a single command you need to create a function as follows:
```
def MyCommand(h, sender, dest, arg=None):
    helpers.msg(h.client, dest, "hello")
```

## A command class ##
To create a command class you need to create a class as follows:
```
class MyCommand(CommandHandler):
    # MyCommand command 
    def __call__(self, sender, dest, arg=None):
        helpers.msg(self.client, dest, "hello")
        # do something 

    # MyCommand.delete command
    def delete(self, sender, dest, arg=None):
        # delete something 
```

# Adding a new command #
Oyoyo Bot relies heavily on entry points. To make either of the previous examples
usefull you will need a setup.py similar to:

```
setup(
    ...
    entry_points="""
    [oyoyo_bot.commands]
    MyCommand = mymodule:MyCommand
    """,
)
```

The resulting module can either be installed system-wide or the egg can be copied
to the plugins folder.

# Adding a listener #
If you need your plugin to listen for certain events, you simply create
a new CommandHandler class (like when dealing with IRCClient):

```
class MyListener(CommandHandler):
    def join(self, prefix, arg):
        # do something 
```

Again you need to use entry points to make Oyoyo Bot aware of the listener.
This means a setup.py with:

```
setup(
    ...
    entry_points="""
    [oyoyo_bot.listeners]
    MyListener = mymodule:MyListener
    """,
)
```

# Plugin configuration #
It is possible ( and advised ) that plugins use the configuration system
used by Oyoyo Bot. To use the config well, a set of defaults needs to be supplied.
A plugin can define defaults in any format that ConfigObj will accept.

```
defaults = StringIO("""
[tell]
max_msgs = 3
""")
```

It should be of little suprise that you need to create an entry point for this...
```
setup(
    ...
    entry_points="""
    [oyoyo_bot.config]
    tell = oyoyo_bot_tell:defaults
    """,
)
```

# A Complete Example #

For complete examples look in http://oyoyo.googlecode.com/svn/trunk/oyoyo_bot_plugins/