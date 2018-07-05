# ==================
# Bonus BLT bot, for translating
# your favorite text from Latko,
# without leaving your IRC client!
# ==================
# Based in Lonedude.
import time
import logging
import traceback
import json
import re
import math
import sys
import atexit
import json
import blt
import textwrap

from irc.bot import ServerSpec, SingleServerIRCBot
from threading import Thread
from os.path import isfile

logging.basicConfig(filename="bot.log", level=logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.terminator = ""

logging.getLogger('').addHandler(console)

prefix = "^"

class BLTBot(SingleServerIRCBot):
    def __init__(self, server, port, channels):
        super().__init__([ServerSpec(server, port)], "BLTBot", "A simple BLT bot by Gustavo6046.")
        self.joinchans = channels
        
    def on_pubmsg(self, connection, event):
        full_cmd = event.arguments[0].split(' ')
        cmd_name = full_cmd[0]
        cmd_args = full_cmd[1:]
        
        if not cmd_name.startswith(prefix):
            return
            
        cmd_name = cmd_name[len(prefix):]
        
        if cmd_name == "translate":
            if len(cmd_args) < 2:
                connection.privmsg(event.target, "[Not enough arguments!]")
                return
        
            language = cmd_args[0]
            text = ' '.join(cmd_args[1:])
            
            try:
                language = blt.loadlang(language)
                
            except BaseException as e:
                connection.privmsg(event.target, "[Error loading language 'lang_{}.bat': {}!]".format(language, type(e).__name__))
                traceback.print_exc()
                
            else:
                try:
                    res = language.translate(text)[0]
                    
                except BaseException as e:
                    connection.privmsg(event.target, "[Error translating {} from English to {}: {}!]".format(repr(text), language, type(e).__name__))
                    traceback.print_exc()
                
                else:
                    for s in textwrap.wrap("{}: {}".format(event.source.nick, res), 350):
                        connection.privmsg(event.target, s)
                        
        elif cmd_name == "addradical":
            if len(cmd_args) < 3:
                connection.privmsg(event.target, "[Not enough arguments!]")
                return
                
            [langname, english, value] = cmd_args[:3]
            
            try:
                language = blt.loadlang(langname)
            
            except BaseException as e:
                connection.privmsg(event.target, "[Error loading language 'lang_{}.bat': {}!]".format(langname, type(e).__name__))
                return
                
            if language.supports(english):
                connection.privmsg(event.target, "['{}' already defined in {}!]".format(english, langname))
                return
                
            language.add_radical(english, value)
            open('lang_{}.bat'.format(langname), 'w').write(language.dumps())
            
            connection.privmsg(event.target, "[Succesfully added radical.]")
                     
        elif cmd_name == "addcomposite":            
            if len(cmd_args) < 3:
                connection.privmsg(event.target, "[Not enough arguments!]")
                return
                
            [langname, english] = cmd_args[:2]
            rads = cmd_args[2:]
        
            try:
                language = blt.loadlang(langname)
            
            except BaseException as e:
                connection.privmsg(event.target, "[Error loading language 'lang_{}.bat': {}!]".format(langname, type(e).__name__))
                return
            
            if language.supports(english):
                connection.privmsg(event.target, "['{}' already defined in {}!]".format(english, langname))
                return
                
            language.add_composite(english, *rads)
            open('lang_{}.bat'.format(langname), 'w').write(language.dumps())

            connection.privmsg(event.target, "[Succesfully added composite word.]")
        
    def on_endofmotd(self, connection, event):
        logging.debug("Joining channels: " + ' + '.join(self.joinchans))
        
        for c in self.joinchans:
            self.connection.join(c)

if __name__ == "__main__":
    conns = {}
    
    try:
        for s in json.load(open("irc.json")):
            conns[s[1]] = BLTBot(s[0], 6667, s[2:])
            
            def safestart():
                try:
                    conns[s[1]].start()
                    
                except BaseException:
                    return
            
            Thread(target=safestart, name="Bot: {}".format(s[0])).start()
            
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Exiting {}...".format(', '.join(conns.keys())))
        
        dead = 0
        
        def kill(conn):
            def __inner__():
                conn.die("BLTBot is a Sentient Team service. Check out BLT @ https://github.com/Gustavo6046/BatchLanguageToolkit")
                dead += 1
            
            return __inner__
        
        for c in conns.values():
            Thread(target=kill(c)).start()
        
        while dead < len(conns): time.sleep(0.5)
        print("Exited.")
        sys.exit(0)