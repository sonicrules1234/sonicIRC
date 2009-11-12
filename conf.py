# This is sonicIRC's config file.  You should be able to figure it out if you
# know any Python.  The only things you might not know about would be the following:
# 1) bpass is your nickserv/server password
# Remember to put all strings in quotes.
# 2) If debug is set to True, it will print out raw IRC in the console,
# otherwise it print it parsed.
# 3) Fill out the servers dict like:
# servers = {<hostname>:{"port":<port>, "channels":[<channels>]}}
# Example : servers = {"irc.freenode.net":{"port":6667, "channels":["#sonicIRC"]}}


servers = {"":{"port":6667, "channels":[""]}}
bpass = ""
debug = True
nick = ""
ident = nick
realname = nick


##DO NOT EDIT ANYTHING BELOW THIS LINE

hosts = servers.keys()
ports = [servers[host]["port"] for host in hosts]
channels = {}
for host in hosts :
    channels[host] = servers[host]["channels"]


