# Novasaur
Novasaur is an open-source Discord bot designed for use within the Nova Incorporated community.
Keep in mind my code is **very** messy, but I'll look at improving tidiness and readability in the future.

Novasaur uses Python, and makes use of the discord.py library to communicate with Discord from a Python script.

The only branch used at the moment is the `master` branch. I may make use of release functionality at a later time, but for now it's not paticularly worth the fuss.

It is maintained by Triosar.

***Note: when viewing the `main.py` file, there will be naughty words in the filtered words list!***
# Features
- Extremely basic filter.
- Blacklist system, integrated with a private Trello board.
- Ability to universally gameban people from all Nova Incorporated games using the Lithium ingame Admin system.
- The ability to fetch all group ranks/IDs from a Roblox group.

# Contributing
- Your only concern when contributing should be the `main.py` file. All other files do not make up the "core bot", and are used for various reasons, testing or otherwise.
- Contributions are welcome. Its preferred that you focus minor commands/features, but Nova Incorporated developers are free to request changes pertaining to official development, with prior agreement on the features.
- If you wish to submit a pull request, you are free to do so, although any requested code changes will be examined for security and quality.
- Any new features or commands should accept the pre-existing structure for event and command handlers. 
For example:
```py
@bot.command()
async def hello(ctx,*args):
	toSend = ' '.join(args)
	await ctx.send(toSend)
```
or
```py
@bot.event
async def on_message(message):
if "amogus" in str(message.content).lower():
	await message.send("amogus")
```
- I am new to Github so don't expect me to be a whizz!

# Credits
A credits list is included in the code, as part of the `>credits` command.

Novasaur © 2021 by Triosar is licensed under CC BY-NC 4.0
