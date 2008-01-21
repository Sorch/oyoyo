
def notice(user, msg):
    return [user, ":"+msg]

def join(room):
    return ["JOIN", room]

def _addNumerics():
    import sys
    from oyoyo import ircevents
    listobj = list
    def numericcmd(cmd_num):
        def f(*args):
            #send(cmd_num, *args)
            print "cmd_num", cmd_num, args
            return [cmd_num] + listobj(args)
        return f
    m = sys.modules[__name__]
    for num, name in ircevents.numeric_events.iteritems():
        setattr(m, name, numericcmd(num))

_addNumerics()








