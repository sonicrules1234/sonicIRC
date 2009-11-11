#!/usr/bin/env python

# Copyright (c) 2009, Westly Ward
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the SonicIRC Team nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY Westly Ward ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Westly Ward BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import socket, thread, world
import time, glob, traceback, os, imp
from mainwindow import Ui_sonicIRC
from PyQt4.QtCore import *
from PyQt4.QtGui import *
conf = imp.load_source("conf", "conf.py")

class sonicIRCWindow(QMainWindow) :
    def __init__(self, parent=None) :
        QWidget.__init__(self, parent)
        self.ui = Ui_sonicIRC()
        self.ui.setupUi(self)
        self.ui.plainTextEdit.setReadOnly(True)
        QObject.connect(self.ui.lineEdit, SIGNAL("returnPressed()"), self.textappend)
        self.ui.lineEdit.tabPressed.connect(self.completeText)
        self.threads = []
        for x in range(len(conf.hosts)) :
            self.threads.append(sonicIRCConnection())
            self.connect(self.ui.listWidget, SIGNAL("currentTextChanged(const QString&)"), self.selectchannel)
            self.connect(self.threads[x], SIGNAL("newmessage"), self.textset)
            self.connect(self.threads[x], SIGNAL("/names"), self.ui.listWidget_2.addItem)
            self.connect(self.threads[x], SIGNAL("SelfJoin"), self.selfjoin)
            self.connect(self.threads[x], SIGNAL("SelfPart"), self.removeChannel)
            self.connect(self.threads[x], SIGNAL("NewJoin"), self.newjoin)
            self.connect(self.threads[x], SIGNAL("NewPart"), self.newpart)
            self.connect(self.threads[x], SIGNAL("SayHey"), self.sayhey)
            self.connect(self.threads[x], SIGNAL("NickChange"), self.nickchange)
    def newconnection(self, host, port, channels) :
        conf.hosts.append(host)
        conf.ports.append(int(port))
        conf.channels[host] = channels
        x = len(self.threads)
        self.threads.append(sonicIRCConnection())
        self.connect(self.ui.listWidget, SIGNAL("currentTextChanged(const QString&)"), self.selectchannel)
        self.connect(self.threads[x], SIGNAL("newmessage"), self.textset)
        self.connect(self.threads[x], SIGNAL("/names"), self.ui.listWidget_2.addItem)
        self.connect(self.threads[x], SIGNAL("SelfJoin"), self.selfjoin)
        self.connect(self.threads[x], SIGNAL("SelfPart"), self.removeChannel)
        self.connect(self.threads[x], SIGNAL("NewJoin"), self.newjoin)
        self.connect(self.threads[x], SIGNAL("NewPart"), self.newpart)
        self.connect(self.threads[x], SIGNAL("SayHey"), self.sayhey)
        self.connect(self.threads[x], SIGNAL("NickChange"), self.nickchange)

    def completeText(self) :
        text = str(self.ui.lineEdit.text())
        if text != "" :
            channel = self.ui.listWidget.item(self.ui.listWidget.currentRow())
            if channel :
                host = str(channel.text()).split("/", 1)[0]
                channel = str(channel.text()).split("/", 1)[1]
            word = text.split(" ")[-1]
            if word != "" :
                newword = word
                for nick in world.connections[host].channels[channel] :
                    if nick.lower().startswith(word.lower()):
                        newword = nick
                        break
                if len(text.split(" ")) == 1 :
                    self.ui.lineEdit.setText(newword + ": ")
                elif len(text.split(" ")) > 1 :
                    self.ui.lineEdit.setText("%s %s " % (" ".join(text.split(" ")[:-1]), newword))

    def nickchange(self, channel) :
        if channel == str(self.ui.listWidget.item(self.ui.listWidget.currentRow()).text()) :
            self.ui.listWidget_2.clear()
            self.ui.listWidget_2.addItems(world.connections[channel.split("/", 1)[0]].channels[channel.split("/", 1)[1]])

    def sayhey(self) :
        QSound.play("hey.wav")

    def selfjoin(self, channel) :
        total = [world.connections[a].channellist for a in [b for b in conf.hosts]]
        newtotal = []
        for network in total :
            for chnl in network :
                newtotal.append(chnl)

        self.ui.listWidget.clear()
        self.ui.listWidget.addItems(newtotal)
        self.selectchannel(channel)
        self.ui.listWidget.setCurrentItem(self.ui.listWidget.findItems(channel, Qt.MatchFixedString)[0])
        self.ui.listWidget.setItemSelected(self.ui.listWidget.item(self.ui.listWidget.currentRow()), True)

    def newjoin(self, channel, sender) :
        if channel == str(self.ui.listWidget.item(self.ui.listWidget.currentRow()).text()) :
            self.ui.listWidget_2.addItem(sender)
    def removeChannel(self, channel) :
        host = channel.split("/", 1)[0]
        channel = channel.split("/", 1)[1]
        total = [world.connections[a].channellist for a in [b for b in conf.hosts]]
        newtotal = []
        for network in total :
            for chnl in network :
                newtotal.append(chnl)
        self.ui.listWidget.clear()
        self.ui.listWidget.addItems(newtotal)
        self.selectchannel(world.connections[host].channellist[0])
        self.ui.listWidget.setCurrentItem(self.ui.listWidget.item(len(world.connections[host].channellist) - 1))
        self.ui.listWidget.setItemSelected(self.ui.listWidget.item(self.ui.listWidget.currentRow()), True)

    def newpart(self, host, channel, sender) :
        if channel == str(self.ui.listWidget.item(self.ui.listWidget.currentRow()).text()) :
            self.ui.listWidget_2.clear()
            self.ui.listWidget_2.addItems(world.connections[host].channels[channel])
    def selectchannel(self, text) :
        if str(text) != "" :
            channel = str(text).split("/", 1)[1]
            host = str(text).split("/", 1)[0]
            self.textset(str(text), world.connections[host].scrollback[channel])
            self.ui.listWidget_2.clear()
            self.ui.listWidget_2.addItems(world.connections[host].channels[channel])


    def textappend2(self, text) :
        self.ui.plainTextEdit.appendPlainText(text)
        self.ui.plainTextEdit.verticalScrollBar().setValue(self.ui.plainTextEdit.verticalScrollBar().maximum())
    def textset(self, channel, text) :
        channel2 = self.ui.listWidget.item(self.ui.listWidget.currentRow())
        if channel2 :
            channel2 = str(channel2.text())
            if channel == channel2 :
                self.ui.plainTextEdit.setPlainText(text)
                self.ui.plainTextEdit.verticalScrollBar().setValue(self.ui.plainTextEdit.verticalScrollBar().maximum())



    def textappend(self) :
        text = str(self.ui.lineEdit.text())
        channel = self.ui.listWidget.item(self.ui.listWidget.currentRow())
        if channel :
            host = str(channel.text()).split("/", 1)[0]
            channel = str(channel.text()).split("/", 1)[1]
        words = text.split(" ")
        if text.startswith("/") :
            if words[0] == "/me" :
                world.connections[host].ircsend(channel, "\x01ACTION %s\x01" % (" ".join(words[1:])))
            elif words[0] == "/quit" :
                world.connections[host].rawsend("QUIT :Leaving...\n")
                world.connections[host].sock.close()
            elif words[0] == "/eval" :
                self.textappend2(repr(eval(" ".join(words[1:]))) + "\n")
            elif words[0] == "/join" :
                world.connections[host].rawsend("JOIN %s\n" % (words[1]))
            elif words[0] == "/connect" :
                self.newconnection(words[1], words[2], words[3:])
            elif words[0] == "/part" :
                if len(words) == 1 and channel.startswith("#") :
                    world.connections[host].rawsend("PART %s\n" % (channel))
                elif len(words) == 1 and not channel.startswith("#") :
                    del world.connections[host].channels[channel]
                    world.connections[host].channellist.remove("%s/%s" % (host, channel))
                    self.removeChannel("%s/%s" % (host, channel))
                elif len(words) == 2 :
                    if words[1].startswith("#") :
                        world.connections[host].rawsend("PART %s\n" % (words[1]))
                    elif not words[1].startswith("#") :
                        del world.connections[host].channels[channel]
                        world.connections[host].channellist.remove("%s/%s" % (host, words[1]))
                        self.removeChannel("%s/%s" % (host, words[1]))
            elif words[0] == "/quote" :
                world.connections[host].rawsend("%s\n" % (" ".join(words[1:])))
            elif words[0] == "/ctcp" :
                world.connections[host].ircsend(words[1], "\x01%s\x01\n" % (words[2]))
        else :
            world.connections[host].ircsend(channel, text)
        self.ui.lineEdit.setText("")
        self.ui.plainTextEdit.verticalScrollBar().setValue(self.ui.plainTextEdit.verticalScrollBar().maximum())


class sonicIRCConnection(QThread) :
    def __init__(self, parent=None) :
        self.host = conf.hosts[world.hostcount]
        self.port = conf.ports[world.hostcount]
        world.hostcount += 1
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        QThread.__init__(self, parent)
        print "Working"
        self.start()
    def connect(self) :
        self.buffer = ""
        print "So far so good"
        self.logf = open("raw.txt", "a")
        self.channels = {}
        self.logs = {}
        self.logs[conf.nick] = open("logs/PMs.txt", "a")
        self.sock.connect((self.host, self.port))
        if conf.bpass != "" : self.rawsend("PASS %s\n" % (conf.bpass))
        self.rawsend("NICK %s \n" % (conf.nick))
        self.rawsend("USER %s * * :%s\n" % (conf.ident, conf.realname))
        self.channels = {}
        self.channellist = []
        self.logs = {}
        self.currentchannel = ""
        self.scrollback = {}
        self.logs[conf.nick] = open("logs/PMs.txt", "a")
        world.connections[self.host] = self
        self.startLoop()

    def run(self) :
        print "Stage 2"
        self.connect()

    def dataReceived(self, data):
        if conf.debug :
            print "[IN]" + data
        self.logf.write("[IN]%s" % (data))


        error = 0
        lines = data.replace("\r", "").split("\n")
        lines[0] = self.buffer + lines[0]
        self.buffer = lines[-1]
        for line in lines[:-1] :
            if line != "" :
                try: 
                    if line.split(" ")[0] == "PING" : self.rawsend("PONG %s\n" % (line.split(" ")[1]))
                    info = {}
                    info["raw"] = line
                    info["words"] = line[1:].split(" ")
                    if info["words"][1] == "001" :
                        self.rawsend("MODE %s +B\n" % (conf.nick))
                        self.ircsend("NickServ", "IDENTIFY %s" % (conf.bpass))
                        for i in conf.channels[self.host] :
                            self.rawsend("JOIN %s\n" % (i))
                    info["whois"] = info["words"][0]
                    info["sender"] = info["whois"].split("!")[0]
                except : traceback.print_exc()
                try : info["hostname"] = info["whois"].split("@")[1]
                except : info["hostname"] = "Unknown"
                try : info["mode"] = info["words"][1]
                except : info["mode"] = "Unknown"
                try :
                    if info["words"][2] == conf.nick :
                        info["channel"] = info["sender"]
                    else : info["channel"] = info["words"][2].replace(":", "").lower()
                except : info["channel"] = "Unknown"
                try : 
                    if info["mode"] == "PRIVMSG" or info["mode"] == "TOPIC" or info["mode"] == "NOTICE" :
                        if ":" in info["words"][3] : info["message"] = " ".join(info["words"][3:])[1:]
                        else : info["message"] = " ".join(info["words"][3:])
                    else : info["message"] = "Unknown"
                except : error = 1
                self.info = info
                if error != 1 : self.prettify(info)
    def rawsend(self, msg_out) :
        self.sock.send(msg_out)
        print "[OUT]%s" % (msg_out)
    def startLoop(self) :
        while True :
            data = self.sock.recv(4096)
            self.dataReceived(data)
        


    def on_ACTION(self, info, args) :
        self.logwrite(info["channel"], "[%s] *%s %s\n" % (time.strftime("%b %d %Y, %H:%M:%S %Z"), info["sender"], " ".join(args[1:]).replace("", "")))
        if not conf.debug : "[%s] *%s %s\n" % (time.strftime("%H:%M:%S"), info["sender"], " ".join(args[1:]).replace("", ""))


    def on_TIME(self, info) :
        pass


    def on_VERSION(self, info) :
        self.rawsend("NOTICE %s :VERSION sonicIRC v0.2\n" % (info["sender"]))

    def on_PRIVMSG(self, info) :
        if conf.nick in info["message"] : self.emit(SIGNAL("SayHey"))
        if info["channel"] in self.channels : self.logwrite(info["channel"], "[%s] <%s> %s\n" % (time.strftime("%b %d %Y, %H:%M:%S %Z"), info["sender"], info["message"]))
        elif info["channel"] == info["sender"] and info["channel"] not in self.channels.keys():
            self.channels[info["channel"]] = [info["sender"], conf.nick]
            self.channellist.append("%s/%s" % (self.host,info["channel"]))
            self.emit(SIGNAL("SelfJoin"), info["channel"])
            self.logwrite(info["channel"], "[%s] <%s> %s\n" % (time.strftime("%b %d %Y, %H:%M:%S %Z"), info["sender"], info["message"]))
            
        if not conf.debug : print "[%s] <%s> %s\n" % (time.strftime("%H:%M:%S"), info["sender"], info["message"])
        if not info["message"]: return




    def on_JOIN(self, info) :
        if not conf.debug : print "[%s] ***%s has joined %s\n" % (time.strftime("%H:%M:%S"), info["sender"], info["channel"])
        self.logwrite(info["channel"], "[%s] ***%s has joined %s\n" % (time.strftime("%b %d %Y, %H:%M:%S %Z"), info["sender"], info["channel"]))

        if conf.nick == info["sender"] :
            self.logs[info["channel"]] = open("logs/%s.txt" % (info["channel"]), "a")
            self.channels[info["channel"]] = []
            self.channellist.append("%s/%s" % (self.host, info["channel"]))
            self.emit(SIGNAL("SelfJoin"), "%s/%s" % (self.host, info["channel"]))
        else :

            self.emit(SIGNAL("NewJoin"), "%s/%s" % (self.host, info["channel"]), info["sender"])
            self.channels[info["channel"]].append(info["sender"])
        


    def on_PART(self, info) :
        self.logwrite(info["channel"], "[%s] ***%s has parted %s\n" % (time.strftime("%b %d %Y, %H:%M:%S %Z"), info["sender"], info["channel"]))
        if not conf.debug : print "[%s] ***%s has parted %s\n" % (time.strftime("%H:%M:%S"), info["sender"], info["channel"])
        if conf.nick == info["sender"] :
            self.logs[info["channel"]].close()
            del self.channels[info["channel"]]
            self.channellist.remove("%s/%s" %(self.host, info["channel"]))
            self.emit(SIGNAL("SelfPart"), "%s/%s" %(self.host, info["channel"]))
        else :
            self.channels[info["channel"]].remove(info["sender"])
            self.emit(SIGNAL("NewPart"), self.host, info["channel"], info["sender"])


    def on_QUIT(self, info) :
        quitmessage = " ".join(info["words"][2:])[1:]
        if not conf.debug : print "[%s] ***%s has quit (%s)\n" % (time.strftime("%b %d %Y, %H:%M:%S %Z"), info["sender"], quitmessage)
        for channel in self.channels :
            if info["sender"] in self.channels[channel] :
                self.channels[channel].remove(info["sender"])
                self.logwrite(channel, "[%s] ***%s has quit (%s)\n" % (time.strftime("%b %d %Y, %H:%M:%S %Z"), info["sender"], quitmessage))
                self.emit(SIGNAL("NewPart"), self.host, channel, info["sender"])
                if info["sender"] == conf.nick : self.logs[channel].close()


    def on_KICK(self, info) :
        recvr = info["words"][3]
        self.logwrite(info["channel"], "[%s] **%s has kicked %s from %s\n" % (time.strftime("%b %d %Y, %H:%M:%S %Z"), info["sender"], recvr, info["channel"]))
        if not conf.debug : print "[%s] **%s has kicked %s from %s" % (time.strftime("%H:%M:%S"), info["sender"], recvr, info["channel"])
        if conf.nick != recvr :
            self.channels[info["channel"]].remove(recvr)
            self.emit(SIGNAL("NewPart"), self.host, info["channel"], recvr)
        else :
            del self.channels[info["channel"]]
            self.channellist.remove("%s/%s" %(self.host, info["channel"]))
            self.emit(SIGNAL("SelfPart"), "%s/%s" %(self.host, info["channel"]))


    def on_TOPIC(self, info) :
        self.logwrite(info["channel"], '[%s] **%s has changed the topic in %s to "%s"\n' % (time.strftime("%b %d %Y, %H:%M:%S %Z"), info["sender"], info["channel"], info["message"]))
        if not conf.debug : print '[%s] **%s has changed the topic in %s to "%s"' % (time.strftime("%H:%M:%S"), info["sender"], info["channel"], info["message"])


    def on_MODE(self, info) :
        mode = info["words"][3]
        if len(info["words"]) > 4 :
            recvr = info["words"][4]
            self.logwrite(info["channel"], "[%s] **%s set mode %s on %s\n" % (time.strftime("%b %d %Y, %H:%M:%S %Z"), info["sender"], mode, recvr))
            if not conf.debug : print "[%s] **%s set mode %s on %s" % (time.strftime("%H:%M:%S"), info["sender"], mode, recvr)
        else :
            self.logwrite(conf.nick, "[%s] **%s set mode %s on %s\n" % (time.strftime("%b %d %Y, %H:%M:%S %Z"), info["sender"], mode, info["channel"]))
            if not conf.debug : print "[%s] **%s set mode %s on %s" % (time.strftime("%H:%M:%S"), info["sender"], mode, info["channel"])


    def on_NICK(self, info) :
        if info["words"][2].startswith(":") :
            newnick = info["words"][2][1:]
        else : newnick = info["words"][2]

        if not conf.debug : print "[%s]**%s is now known as %s" % (time.strftime("%b %d %Y, %H:%M:%S %Z"), info["sender"], newnick)
        for channel in self.channels :
            if info["sender"] in self.channels[channel] :
                self.channels[channel].remove(info["sender"])
                self.channels[channel].append(newnick)
                self.logwrite(channel, "[%s] **%s is now known as %s\n" % (time.strftime("%b %d %Y, %H:%M:%S %Z"), info["sender"], newnick))
                self.emit(SIGNAL("NickChange"), "%s/%s" %(self.host, channel))

        
    def on_INVITE(self, info):
        pass

            
    def on_353(self, info) :
        for nick in info["words"][5:] :
            if nick != "" :
                correctnick = nick.replace(":", "")
                if correctnick[0] in ["%", "@", "&", "~", "+"] :
                    correctnick = correctnick[1:]
                self.channels[info["words"][4].lower()].append(correctnick)
                self.emit(SIGNAL("/names"), correctnick)


    def on_NOTICE(self, info) :
        if not conf.debug : print "[%s] -%s- %s" % (time.strftime("%b %d %Y, %H:%M:%S %Z"), info["sender"], info["message"])
        if "." not in info["sender"] and not info["sender"].lower().endswith("serv") :
            if info["channel"] == info["sender"] and info["channel"] not in self.channels.keys() :
                self.channels[info["channel"]] = [info["sender"], conf.nick]
                self.channellist.append("%s/%s" % (self.host,info["channel"]))
                self.emit(SIGNAL("SelfJoin"), info["channel"])
            self.logwrite(info["channel"], "[%s] -%s- %s\n" % (time.strftime("%b %d %Y, %H:%M:%S %Z"), info["sender"], info["message"]))
        
    def prettify(self, info) :
        args = info["message"].split(" ")
        if info["mode"] == "PRIVMSG" :
            if args[0] == "ACTION" :
                self.on_ACTION(info, args)
            elif info["message"] == "VERSION" :
                self.on_VERSION(info)
            elif info["message"] == "TIME" :
                self.on_TIME(info)
            else : 
                self.on_PRIVMSG(info)
        elif info["mode"] == "JOIN" :
            self.on_JOIN(info)
        elif info["mode"] == "PART" :
            self.on_PART(info)
        elif info["mode"] == "QUIT":
            self.on_QUIT(info)
        elif info["mode"] == "KICK" : 
            recvr = info["words"][3]
            self.on_KICK(info)
        elif info["mode"] == "TOPIC" :
            self.on_TOPIC(info)
        elif info["mode"] == "MODE" :
            self.on_MODE(info)
        elif info["mode"] == "INVITE" :
            self.on_INVITE(info)
        elif info["mode"] == "NICK" :
            self.on_NICK(info)
        elif info["mode"] == "353" :
            self.on_353(info)
        elif info["mode"] == "NOTICE" :
            self.on_NOTICE(info)



    def ircsend(self, targ_channel, msg_out) :

        for line in msg_out.split("\n") :
            self.rawsend("PRIVMSG %s :%s\n" % (targ_channel, line))
            if not msg_out.startswith("\x01ACTION") : self.logwrite(targ_channel, "[%s] <%s> %s\n" % (time.strftime("%b %d %Y, %H:%M:%S %Z"), conf.nick, line))
            else : self.logwrite(targ_channel, "[%s] *%s %s\n" % (time.strftime("%b %d %Y, %H:%M:%S %Z"), conf.nick, " ".join(msg_out.split(" ")[1:]).replace("", "")))
        
    def logwrite(self, channel, log) :
        
        if not self.scrollback.has_key(channel) :
            print "Created", channel, self.host
            self.scrollback[channel] = ""
        self.scrollback[channel] += log
        self.emit(SIGNAL("newmessage"), "%s/%s" % (self.host, channel), self.scrollback[channel])
def main():
    if "logs" not in glob.glob("*") :
        os.mkdir("logs")
    app = QApplication([])
    
    window = sonicIRCWindow()

    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
