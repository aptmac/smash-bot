# Smash Bot

## How to Use
Configure the IRC channel information at the top of the `smashbot.py` file to set the bot's name and specify which channel it should join. 

Run `python smashbot.py` to start the bot, and if configured correctly, it should join the channel specified.

## Commands
`!help`: whispers the user with a description of bot functionality

`!all <message>`: broadcasts a message and tags every member of the channel

`!bracket`: prints the URL of the current challonge bracket

`!hitbox <character> <move>`: prints the URL to view the move in the smash 4 move viewer app

## Contributing
This is a hacky bot, and isn't meant to be high quality. As a result, spaghetti code is encouraged! That means no tests, no segregation of code into other files (long live the monolith), regex is king, and it's a feature - not a bug. 

## Kudos
Based on the examples and instructions provided by https://linuxacademy.com/blog/geek/creating-an-irc-bot-with-python3/

