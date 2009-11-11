# This is sonicIRC's config file.  You should be able to figure it out if you
# know any Python.  The only things you might not know about would be the following:
# 1) bpass is your nickserv/server password
# Remember to put all strings in quotes.
# 2) If debug is set to True, it will print out raw IRC in the console,
# otherwise it print it parsed.
# 3) You need to list each host in the order that you would like sonicbot to connect
# 4) Channels is a dict in which you specify the host against the channels
# (in a list) Example: channels = {"irc.freenode.net" : ["#sonicIRC", "#test"]}


hosts = [""]
ports = [6667]
ident = ""
nick = ""
channels = {"":[]}
realname = nick
bpass = ""
debug = True



