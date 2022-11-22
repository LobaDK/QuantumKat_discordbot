# QuantumKat-discordbot
A personal project for a Discord bot, purely for fun.

**This is a private bot**. It is not intended to be added by other people except for myself and close friends I trust. Furthermore, it is limited to a very small amount of servers I trust.

If you wish to use this bot and it's features yourself, in your own server(s), please git-clone or fork the project, and run it from there.

# Running it yourself
If you chose to run it yourself, please note the following:

#### Token
The Application/Bot token is read from a file named 'token' in a directory called 'files'. Feel free to rewrite this, but if you wanna use it as is, without changing anything, this is how it gets the token for the bot. Please note the file is ignored in Git, so you'll have to manually create the file in the directory.

#### Version
The bot recently got rewritten for Discord.py 2.0, which means only 2.0 and up will work correctly. If you for whatever reason want or need the 1.7 version, you'll need to use the version control/git history.

#### ar and pr commands
The ar and pr commands use a publicly available php script on https://aaaa.lobadk.com/botrandom.php and https://possum.lobadk.com/botrandom.php, respectively, to get a random relative filename (./example.png) from the server. This means all the randomness is handled server-side, for both performance, and easier intergration. Scrapping the index file is also a possibility, and was used before I wrote the php script, but can take a whole 1-2 seconds longer to return, and maybe even longer under non-ideal network conditions.

### Cogs/Extensions
The cogs are split up into different groups of purposes/accessibility. 'Field' is for standard commands that anyone should have access to, generally just to provide entertainment. 
'Entanglement' contains bot-owner only commands, for management of the bot's features. 
'Activity' is anything that requires or uses a loop, and also limited to the bot owner.
'Tunnel' is background code for handling exceptions, or listening to specific actions.
'Control' is anything used to control either the bot, or manage the users in the server.

# Features

## Standard commands
### Random meme/shitpost and opossums
No, the last part is not a joke. The bot features a command (?ar) which returns a random file from my shitpost subdomain https://aaaa.lobadk.com, as well as a command that returns random images and videos of opossums from https://possum.lobadk.com.

Also features the ?a, ?aaaasearch and ?aaaarandomsearch commands for appending filenames to the shitpost URL for faster linking, searching for a filename and getting the results, and searching for a filename and getting a random result returned, respectively.

### 8-ball but quantum themed
The ?qball, or ?quantumball, command picks a random either positive, neutral, or negative answer, slightly edited to feel more in theme, with the positive ones having a slightly higher chance of happening (so think carefully of how you ask that question).

### Pet, hug, quantum-pet and quantum-hug
?pet, ?hug, ?quantumpet and ?quantumhug
Because who doesn't need to be petted or hugged by several QuantumKat's at the same time?

### Rock, Paper, Scissors
A game of Rock, Paper and Scissors with ?rps. Though playing against an opponent that can see into the future isn't exactly fair... For you, of course.

### Ping test
Test with ?ping|pong if the bot responds, and optionally how long the response time was, or it's latency.

## Bot owner only
### Bot shutdown
The ?observe command shuts down the bot entirely.

### Reload, start and stop cogs/extensions
The commands ?stabilise, ?entangle and ?unentangle reloads the cogs, starts a stopped cog, and stops a running cog, respectively.

### Download, rename and remove files
The ?quantise command allows files to be downloaded to the /var/www/aaaa and /var/www/possum folders, including support for YouTube. Personally, this is used to add more shitposts and opossums to my server

The ?requantise command renames files, and ?dequantise deletes them.

### Git commands
The ?git command passes any parameters included, to the actual git program running on the server, returning whatever output it gives. Useful for swapping branches/versions, or check it's status, without needing to SSH into the actual server. Input is limited to alphanumeric, underscores and hyphens to still allow parameters that requires either of those, but not enough to allow command chaining

### Updatting
The ?update command runs a 'git pull' to fetch the newest branch version, and checks for changed files between the current running version, and the new one, and reloads any affected cogs/extensions automatically.

### Controlling the Activity
?ActivityStart, ?ActivityRestart and ?ActivityStop can be used to start, restart and stop the loop that displays random activities in the bot's section area on Discord.

## Bot and/or server onwer only
### List joined servers and their owners
?ServerOwnerList lists the servers the bot is in, as well as the owner of each server. Returns both their names, as well as ID's for use in other commands. For privacy, this is limited to the bot's DM's.

### Remote leave a server
In case the bot is in a server that the bot owner is not in, and wish the bot to leave it, the ?LeaveServer command attempts to leave any server with the correct ID supplied.

### Leave current server
?Leave
Leaves the server the command was run in. For moderation purposes, anyone with administrator or members moderator privileges can also run this.