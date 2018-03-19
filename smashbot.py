#!/usr/bin/python

# Modified from: https://linuxacademy.com/blog/geek/creating-an-irc-bot-with-python3/

# Import some necessary libraries.
import socket, re, subprocess, os, time, threading, sys, math
from datetime import date

# Some basic variables used to configure the bot        
server = "chat.freenode.net" # Server
channel = "#SmashTO" # Channel
botnick = "SM4SHBOT" # Your bots nick
password = "smashbotpassword"
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock.connect((server, 6667)) # Here we connect to the server using the port 6667
ircsock.send("USER "+ botnick +" "+ botnick +" "+ botnick + " " + botnick + "\n") # user authentication
ircsock.send("NICK "+ botnick +"\n") # assign the nick to the bot
ircsock.send("nickserv identify " + password + "\r\n")

def ping(): # respond to server Pings.
  ircsock.send("PONG :pingis\n")  

def sendmsg(msg): # sends messages to the channel.
  ircsock.send("PRIVMSG "+ channel +" :"+ msg +"\n") 

def joinchan(chan): # join channel(s).
  ircsock.send("JOIN "+ chan + "\n")

def whisper(msg, user): # whisper a user 
  ircsock.send("PRIVMSG " + user + ' :' + msg.strip('\n\r') + '\n')

def get_names(): # get list of users in a channel
  ircsock.send("NAMES " + channel + "\n")
  resp = ircsock.recv(2048)
  return re.search(".*" + channel + " :(.*)", resp, re.IGNORECASE).group(1)

# log chat messages
def logger(name, msg):
  # loop through the content of the chat log and reduce to 100 lines, starting with oldest. --Definitely a better way to do this, needs improvement.
  irclog = open("ircchat.log", 'r')
  content = irclog.readlines()
  irclog.close()
  # loop through the content of the chat log and reduce to 100 lines, starting with oldest. --Definitely a better way to do this, needs improvement.
  irclog = open("ircchat.log", "w")
  while len(content) > 100:
    content.remove(content[0])
  if len(content) > 0:
    for i in content:
      irclog.write(i.strip('\n\r') + '\n')
  # write newest messge to log.
  irclog.write(name + ':' + msg.strip('\n\r'))
  irclog.close()

# send help message to users
def help(name,topic=''):
  # set default help message to blank.
  message = ''
  # if no help topic is specified, send general help message about the bot.
  if topic == '':
    message = "Current valid functions include:\n!all <message> to send a message to everyone in the channel\n!bracket to get the current challonge url" 
  # if a help message is specified, let the user know it's not coded yet.
  else:
    message = "Feature not yet implemented, sorry. Please see the main help (message me with \'.help\')"
  print(topic)
  # send help message in whisper to user.
  whisper(message, name)

# send a message to all members
def all(message):
  sendmsg("\(`O`)/: " + message + " @ " + get_names())

# print the link to the current bracket
def bracket():
  baseURL = 'https://challonge.com/rht'
  month = date.today().strftime("%B")[:3]
  week = str(int(math.ceil(date.today().day // 7 + 1 / 2)))
  year = str(date.today().year)
  sendmsg(baseURL + "_" + month + "_" + week + "_" + year)

# main functions of the bot
def main():
  # start by joining the channel.
  joinchan(channel)
  # start infinite loop to continually check for and receive new info from server
  while 1: 
    # clear ircmsg value every time
    ircmsg = ""
    # set ircmsg to new data received from server
    ircmsg = ircsock.recv(2048)
    # remove any line breaks
    ircmsg = ircmsg.strip('\n\r') 
    # print received message to stdout (mostly for debugging).
    print(ircmsg) 
    # repsond to pings so server doesn't think we've disconnected
    if ircmsg.find("PING :") != -1: 
      ping()
    # look for PRIVMSG lines as these are messages in the channel or sent to the bot
    if ircmsg.find("PRIVMSG") != -1:
      # save user name into name variable
      name = ircmsg.split('!',1)[0][1:]
      print('name: ' + name)
      # get the message to look for commands
      message = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1]
      print(message)
      # look for commands and send to appropriate function.
      if message[:5] == '!help':
        help(name, message[5:])
      elif message[:4] == '!all':
        all(message[5:])
      elif message[:8] == '!bracket':
        bracket()
      else:
      # if no command found, get 
        if len(name) < 17:
          logger(name, message)
          # if the final message is from me and says 'gtfo [bot]' stop the bot and exit. Needs adjustment so it works for main user account and not hardcoded username.
          if name.lower() == "almac" and message[:5+len(botnick)] == "gtfo %s" % botnick:
            sendmsg("Oh...okay... :'(")
            ircsock.send("PART " + channel + "\r\n")
            sys.exit()

#start main function
main()
