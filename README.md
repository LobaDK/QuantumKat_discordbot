# QuantumKat-discordbot
A personal project for a Discord bot, purely for fun.

**This is a private bot**. It is not intended to be added by other people except for myself and close friends I trust. Furthermore, it is limited to a very small amount of servers I trust.

If you wish to use this bot and it's features yourself, in your own server(s), please git-clone or fork the project, and run it from there. However be aware that editing of the code is required as most features attempt to be or use local resources only, which may not be available in the same manner or at all externally.

# Running it yourself
If you chose to run it yourself, please note the following:

#### Token/API key
Required tokens/keys can be stored in a file named `.env`. The file is ignored by git to prevent leaking secrets.  
`OPENAI_API_KEY=` sets the API key used by OpenAI.  
`OPENAI_SESSION_KEY=` sets the session key used to login to the user page and fetch data.  
`TOKEN=` sets the API key used to connect the bot to Discord.  
`OWNER_ID=` sets the Discord ID of the bot owner

#### ar and pr commands
The ar and pr commands get the appropriate files locally through Python itself or shell commands, and then chooses 1-5 random files in the list. For external use, https://aaaa.lobadk.com/botrandom.php and https://possum.lobadk.com/botrandom.php can be used to get a single random file

### Cogs/Extensions
The cogs are split up into different groups of purposes/accessibility.

`Field` is for standard commands that anyone should have access to, generally just to provide entertainment.  
`Entanglement` contains bot-owner only commands, for management of the bot's features.  
`Activity` is anything that requires or uses a loop, and also limited to the bot owner.  
`Tunnel` is background code for handling exceptions, or listening to specific actions.  
`Control` is anything used to control either the bot, or manage the users in the server, and is a mix of bot-owner, server-owner and admin/mod-limited commands.  
`Chat` Is used to chat with the bot via OpenAI/ChatGPT and manage it's chat history.  
`Auth` Is used to authenticate the bot with the server it is in. Without being authenticated (Approved) by the owner, all commands in that server will fail with an appropriate message.

# Features

## Standard commands
### Random meme/shitpost and opossums
No, the last part is not a joke. The bot features a command `?ar` which returns a random file from my shitpost subdomain https://aaaa.lobadk.com, as well as `?or` which returns random images and videos of opossums from https://possum.lobadk.com.

Also features:  
`?a` Appends an exact, or the closest match if no other filename matches, filename to https://aaaa.lobadk.com  
`?aaaasearch`|`?as`|`?asearch` Returns a list of files matching the search query  
`?arsearch`|`?aaaarandomsearch`|`?ars`|`?asr` Searches for files matching the search query and returns a single random file from the list

### 8-ball but quantum themed
`?qball`|`?quantumball` picks a random either positive, neutral, or negative answer, slightly edited to feel more in theme, with the positive ones having a slightly higher chance of happening (so think carefully of how you ask that question).

### Pet, hug, quantum-pet and quantum-hug
`?pet`, `?hug`, `?quantumpet` and `?quantumhug`.
Because who doesn't need to be petted or hugged by several QuantumKat's at the same time?

### Rock, Paper, Scissors
A game of Rock, Paper and Scissors with `?rps`. Though playing against an opponent that can see into the future isn't exactly fair... For you, of course.

### Ping test
Test with `?ping`|`?pong` if the bot responds, and optionally how long the response time was/it's latency.

## Bot owner only
### Bot shutdown
The `?observe` command shuts down the bot entirely.

### Reload, start and stop cogs/extensions
`?stabilise` Reloads the specified cog. Optionally reloads all cogs if `*` is used instead.  
`?entangle` Loads the specified cog.  
`?unentangle` Unloads the specified cog.

### Download, rename and remove files
`?quantise` Downloads the specified file to /var/www/aaaa or /var/www/possum. Supports using yt-dlp for YouTube or other annoying video hosting sites.  
`?requantise` Renames the specified file.  
`?dequantise` Deletes the specified file.

### Git commands
The `?git` command passes any parameters included, to the actual git program running on the server, returning whatever output it gives. Useful for swapping branches/versions, or check it's status, without needing to SSH into the actual server. Input is limited to alphanumeric, underscores and hyphens to still allow parameters that requires either of those, but not enough to allow command chaining and arbitrary commands.

### Updating
The `?update` command runs a 'git pull' to fetch the newest branch version, and checks for changed files between the current running version, and the new one, and reloads any affected cogs/extensions automatically. If the main script has changes detected, the bot will prompt and ask if the bot should restart it's own process to apply new changes.

### Controlling the Activity
`?ActivityStart` Start a loop that changes the bot's activity randomly.  
`?ActivityRestart` Restart the loop. Applies a new activity.  
`?ActivityStop` Stop the loop.

## Bot and/or server owner only
### List joined servers and their owners
`?ServerOwnerList` lists the servers the bot is in, as well as the owner of each server. Returns both their names, as well as ID's for use in other commands. For privacy, this is limited to the bot's DM's.

### Remote leave a server
In case the bot is in a server that the bot owner is not in, and wish the bot to leave it, the `?LeaveServer` command attempts to leave any server with the correct ID supplied.

### Leave current server
`?Leave` Leaves the server the command was run in. For moderation purposes, anyone with administrator or members moderator privileges can also run this.

## Chat
### Chat with QuantumKat via OpenAI API
`?Chat` Sends an attached message to ChatGPT via the OpenAI API, set up with an included custom system message that defines its behaviors. Messages and its replies are stored in a database, each related to the UUID of the user and server that initiated the command, allowing for unique history between multiple users, in multiple servers. A maximum of 10 messages are retrieved and used as history, to help provide context but still keep token lengths somewhat low.
### View the chat history
`?Chatview` Returns up to 10 of the most recent conversations stored in the database for the user, in the current server, whom initiated the command. How it's displayed is also how ChatGPT sees it when a new chat prompt is initiated.
### Clear the chat history
`?Chatclear`Clears the entire chat history for the user, in the current server, that initiated the command. Useful in case the prompts are starting to return garbage/deteriorated text, or they just wanna start new a chat.
### shared[command]
`?Shared[command]` All commands have an additional shared version where a prompt is not tied to a specific user i.e. everyone in a server is sharing the same history. The only difference in the commands here is that clearing is limited to the bot owner, server owner and server moderators.
### View chat status
`?chatstatus` Checks and shows if there's an API key present. If there's also a session key, it attempts to get the current monthly total spending.
## Auth
### Authenticating the bot
`auth` Before any commands from the bot can be used within a new server, a server admin/mod, the owner, or the bot owner, must run this command to request approval. Regardless if the request is approved or denied, the server will get added to the database, with a flag respective to the choice. If it's approved, it can run commands, and if it's denied, it will prevent subsequent approval requests, as well as any commands from being run. If the owner has not decided within 5 minutes, the command will simply time out.
### Removing an approved server from the list
`deauth` Can be used to remove a server that has previously been approved. If nothing is specified, it assume the current server should be deauthenticated. If a server ID or name is included, it will attempt to look it up in the database and remove it from the list. For obvious reasons, deauthenticating a specific server is limited to the bot owner.