#!/usr/bin/python

# Modified from: https://linuxacademy.com/blog/geek/creating-an-irc-bot-with-python3/

# Import some necessary libraries.
import socket, re, subprocess, os, time, threading, sys, math, challonge
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

# send help message to users
def help(name,topic=''):
  # set default help message to blank.
  message = ''
  # if no help topic is specified, send general help message about the bot.
  if topic == '':
    message = 'Current valid functions include:'\
    ' | !all <message> to send a message to everyone in the channel'\
    ' | !bracket to get the current challonge url'\
    ' | !hitbox <character> <move> to get a url to see move animation'\
    ' | !matches to see the current open matches'\
    ' | !results to see results of complete matches (of current tournament)'
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
  sendmsg(get_bracket_url())

# get the bracket url
def get_bracket_url():
  base_url = 'https://challonge.com/'
  return (base_url + get_bracket_id())

def get_bracket_id():
  month = date.today().strftime("%B")[:3].lower()
  week = str(int((math.ceil(date.today().day // 7 + 1) / 2)))
  year = str(date.today().year)
  return ('rht_' + month + '_' + week + '_' + year)

# library to map character argument to appropriate move viewer name
def format_character(character):
  character = character.lower()
  switcher = {
    'bayo': 'bayonetta',
    'bayonetta': 'bayonetta',
    'bowser': 'koopa',
    'koopa': 'koopa',
    'captainfalcon': 'captain',
    'charizard': 'lizardon',
    'lizardon': 'lizardon',
    'cloud': 'cloud',
    'diddykong': 'diddy',
    'diddy': 'diddy',
    'donkeykong': 'donkey',
    'donkey': 'donkey',
    'dr.mario': 'mariod',
    'drmario': 'mariod',
    'falco': 'falco',
    'fox': 'fox',
    '20XX': 'fox',
    'ganondorf': 'ganon',
    'ganon': 'ganon',
    'greninja': 'gekkouga',
    'gekkouga': 'gekkouga',
    'ike': 'ike',
    'link': 'link',
    'littlemac': 'littlemac',
    'lucario': 'lucario',
    'luigi': 'luigi',
    'mario': 'mario',
    'marth': 'marth',
    'metaknight': 'metaknight',
    'mewtwo': 'mewtwo',
    'palutena': 'palutena',
    'peach': 'peach',
    'leo': 'peach',
    'robin': 'reflet',
    'rosalina': 'rosetta',
    'luma': 'tico',
    'roy': 'roy',
    'ryu': 'ryu',
    'sheik': 'sheik',
    'shulk': 'shulk',
    'sonic': 'sonic',
    'gottagofast': 'sonic',
    'toonlink': 'toonlink',
    'tink': 'toonlink',
    'yoshi': 'yoshi',
    'zerosuitsamus': 'szerosuit',
    'zss': 'szerosuit'
  }
  return switcher.get(character, 'error')

# library to map move argument to appropriate move viewer name
def format_move(move):
  move = move.lower()
  switcher = {
    # Grounded
    'jab1': 'Attack11',
    'jab2': 'Attack12',
    'utilt': 'AttackHi3',
    'dtilt': 'AttackLw3',
    'ftilt': 'AttackS3S',
    'dash': 'AttackDash',
    'dashattack': 'AttackDash',
    # Aerials
    'nair': 'AttackAirN',
    'dair': 'AttackAirLw',
    'uair': 'AttackAirHi',
    'fair': 'AttackAirF',
    'bair': 'AttackAirB',
    # Smashes
    'fsmash': 'AttackS4S',
    'dsmash': 'AttackLw4',
    'usmash': 'AttackHi4',
    # Specials
    'special': 'SpecialN',
    'b': 'SpecialN',
    'sidespecial': 'SpecialS',
    'sideb': 'SpecialS',
    'uspecial': 'SpecialHi',
    'dspecial': 'SpecialLw',
    # Throws
    'grab': 'Catch',
    'dashgrab': 'CatchDash',
    'fthrow': 'ThrowF',
    'uthrow': 'ThrowHi',
    'dthrow': 'ThrowLw',
    'bthrow': 'ThrowB'
  }
  return switcher.get(move, 'error')

def hitbox(message):
  baseURL = 'https://struz.github.io/smash-move-viewer/#/v1'
  try:
    message = message.split()
    character = format_character(message[0])
    move = format_move(message[1])
    if character != 'error' and move != 'error':
      sendmsg(baseURL + '/' + character + '/' + move + '/1?speed=0.25')
    else: 
      if character == 'error':
        sendmsg('Error: invalid character name has been entered.')
        sendmsg('Valid characters are: '\
        'bayonetta, bowser, captainfalcon, charizard, cloud, diddykong, donkeykong, '\
        'dr.mario, falco, fox, ganondorf, greninja, ike, link, littlemac, lucario, '\
        'luigi, mario, marth, metaknight, mewtwo, palutena, peach, robin, rosalina, '\
        'luma, roy, ryu, sheik, shulk, sonic, toonlink, yoshi, zerosuitsamus')
      if move == 'error':
        sendmsg('Error: invalid move name has been entered.')
        sendmsg('Valid moves are: '\
          'jab1, jab2, ftilt, utilt, dtilt, dashattack, '\
          'nair, fair, dair, uair, bair, '\
          'fsmash, dsmash, usmash, '\
          'special, sidespecial, uspecial, dspecial, '\
          'grab, dashgrab, fthrow, uthrow, dthrow, bthrow')
  except IndexError:
    sendmsg('Error: invalid command.'\
    ' | Usage: !hitbox <character> <move>'\
    ' | example: !hitbox cloud uair')

# print the results of completed matches
def finished_matches(flag):
  bracket_url = get_bracket_url()
  file = open('api-key.txt', 'r')
  apikey = file.read()
  file.close()
  # setup pychallonge
  try:
    challonge.set_credentials("aptmac", apikey)
    tournament = challonge.tournaments.show(get_bracket_id())
    # get response with all participant info
    participants = challonge.participants.index(tournament["id"])
    players = {}
    for participant in participants:
      players[participant["id"]] = participant["display-name"]
    # get the matches with state complete
    matches = challonge.matches.index(tournament["id"])
    sendmsg("\(`O`)/: Completed matches this tournament are:")
    for match in matches:
      if match["state"] == 'complete':
        score = match["score-csv"]
        sendmsg(players[match["player1-id"]].split()[0][::-1] + ' ' + score + ' ' + players[match["player2-id"]].split()[0][::-1])
        time.sleep(1)
  except:
    sendmsg('Error: something went wrong with challonge :/')

# print the currently pending matches
def pending_matches():
  bracket_url = get_bracket_url()
  file = open('api-key.txt', 'r') 
  apikey = file.read()
  file.close()
  # setup pychallonge
  try:
    challonge.set_credentials("aptmac", apikey)
    tournament = challonge.tournaments.show(get_bracket_id())
    # get response with all participant info
    participants = challonge.participants.index(tournament["id"])
    players = {}
    for participant in participants:
      players[participant["id"]] = participant["display-name"]
    # get the matches with state complete
    matches = challonge.matches.index(tournament["id"])
    sendmsg("\(`O`)/: Current open matches to be played are:")
    for match in matches:
      if match["state"] == 'open':
        sendmsg(players[match["player1-id"]].split()[0] + ' vs. ' + players[match["player2-id"]].split()[0])
  except:
    sendmsg('Error: something went wrong with challonge :/')

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
      elif message[:7] == '!hitbox':
        hitbox(message[8:])
      elif message[:8] == '!matches':
        pending_matches()
      elif message[:8] == '!results':
        finished_matches(message[8:])
      else:
      # if no command found, get 
        if len(name) < 17:
          # logger(name, message)
          # if the final message is from me and says 'gtfo [bot]' stop the bot and exit. Needs adjustment so it works for main user account and not hardcoded username.
          if name.lower() == "almac" and message[:5+len(botnick)] == "gtfo %s" % botnick:
            sendmsg("Oh...okay... :'(")
            ircsock.send("PART " + channel + "\r\n")
            sys.exit()

#start main function
main()
