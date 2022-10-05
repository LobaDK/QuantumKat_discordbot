# QuantumKat-discordbot
A personal project for a Discord bot, purely for fun.

**This is a private bot**. It is not intended to be added by other people except for myself and close friends I trust. Furthermore, it is limited to a very small amount of servers I trust.

If you wish to use this bot and it's features yourself, in your own server(s), please git-clone or fork the project, and run it from there.

# Running it yourself
If you chose to run it yourself, please note the following:

#### Token
The Application/Bot token is read from a file named 'token' in a directory called 'files'. Feel free to rewrite this, but if you wanna use it as is, without changing anything, this is how it gets the token for the bot. Please note these are ignored in git for security, so you'll need to create both the directory and file manually.

#### Version
The bot recently got rewritten for Discord.py 2.0, which means only 2.0 and up will work correctly. If you for whatever reason want or need the 1.7 version, you'll need to use the version control/git history.

#### ar and pr commands
The ar and pr commands use a php script on https://aaaa.lobadk.com/botrandom.php and https://possum.lobadk.com/botrandom.php, respectively, to get a random relative filename (./example.png) from the server. This means all the randomness is handled server-side, for both performance, and easier intergration. Scrapping the index file is also a possibility, and was used before I wrote the php script, but can take a whole 1-2 seconds longer to return, and maybe even longer under non-ideal network conditions.
