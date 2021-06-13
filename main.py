# Novasaur main file. - infinitypupper

# Import like 4532534534543 modules
import requests
import os
from ro_py import users
from ro_py.users import User
import discord
from dotenv import load_dotenv
import keep_alive
import random
import time
from humanfriendly import format_timespan
from discord.ext import commands
from replit import db
import io
import contextlib
from discord.utils import get
from discord import Webhook, AsyncWebhookAdapter
import aiohttp
import logging
from trello import TrelloApi
import asyncio
from ro_py import Client
import traceback
intents = discord.Intents().all()
bot = commands.Bot(command_prefix='>',intents=intents)

# One of the bits for Discord channel logging. Currently off for development purposes.
# logging.basicConfig(filename='test.log', format='%(filename)s: %(message)s',
#     level=logging.ERROR)


db["s3p"] = int(0) # current Stage 3 page

# where blacklist pages are stored
s1bEmbeds = []
s2bEmbeds = []
s3bEmbeds = []


xmasTime = int(1640390400) # define christmas day as unix

# Declare various lists for use.
badwords = ['nigger','niggers','nibber','nigga','nibba','faggot','faget',' fag ','fagging','fagot','mussie','mossie',' cum','ejaculate','jerk  of','lezzo','lezbo','lezzer','lezer','lezza','leza','masturbat','molest','porn', ' rape ','rimjob','rimming','blowjob','sextoy','skank','slut','sperm','sodom','tranny','tranni','trany','trani',' wank',' wog ','retard','f@g','re3tard','cunt','c u m',' c u m','hentai','ahegao','cocaine','crackhead','whore','spunk']
botadmins = ["315193131282726914","314394344465498122","626171285491154944","691770905835077643","340167800561860618","435457720855035914"]
blacklist = [] # yeah idk what this is used for
rps_choices = ["scissors!", "rock!", "paper!"]
serverlist = [] # server names
slist = [] #server objects

# define time
starttime = time.time()
print(starttime)

#load from .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# function to delete a card from the trelloban list
def clearUser(name):
  TRELLO_APP_KEY = os.getenv('TRELLO_APP_KEY')
  TOKEN = os.getenv('TOKEN')
  listID = "6093ccae8f0a0a4e409fa1ce"
  
  trello = TrelloApi(TRELLO_APP_KEY, TOKEN)

  cardList = trello.lists.get_card(listID)

  for x in cardList:
    splity = x["name"].split(":")[0] # i.e. the first split part of the card title
    if str(splity) == str(name):
      trello.cards.delete(x['id'])

# poorly named, but this is the command that continually logs 
async def checkQ():
  while True:
    await asyncio.sleep(1)
    fileq = open("test.log","r")
    for x in fileq:
      toSend = "```py\n"+x+"```"
      bot.loop.create_task((bot.get_channel(832614393279283211)).send(toSend))
    fileq.close()
    open('test.log', 'w').close()

# returns any friends the provided user has who are also blacklisted
async def checkFriends(username):
  RS = os.getenv('ROBLOSECURITY')
  roblox = Client(RS)

  TRELLO_APP_KEY = os.getenv('TRELLO_APP_KEY')
  TOKEN = os.getenv('TOKEN')
  trello = TrelloApi(TRELLO_APP_KEY, TOKEN)
  listIDBL = "6093ccae8f0a0a4e409fa1ce"

  user = await roblox.get_user_by_username(username)
  friendList = []
  trelloBL = []
  badList = []
  crossover = []
  for x in await user.get_friends():
    friendList.append(str(x.id))
  for x in trello.lists.get_card(listIDBL):
    if str(x["name"].split(":")[1]) in ["1","2","3"]:
      badList.append(str(x["name"].split(":")[0]))
  for x in friendList:
    if (x in badList):
      crossover.append(x)
  return crossover

# refreshes the blacklist "pages" with any new additions/deletions/changes
async def blListRefresh():

  s1b = []
  s2b = []
  s3b = []

  global s1bEmbeds 
  s1bEmbeds = []
  global s2bEmbeds
  s2bEmbeds = []
  global s3bEmbeds
  s3bEmbeds = []

  TRELLO_APP_KEY = os.getenv('TRELLO_APP_KEY')
  TOKEN = os.getenv('TOKEN')
  listID = "6093ccae8f0a0a4e409fa1ce"
  
  trello = TrelloApi(TRELLO_APP_KEY, TOKEN)

  cardList = trello.lists.get_card(listID)

  # Putting each blacklisted user in stage lists.
  for x in cardList:
    cardName = x["name"]
    cardNameSplit = cardName.split(":")
    cardStage = cardNameSplit[1]
    if str(cardStage) == "1":
      s1b.append(cardName)
    if str(cardStage) == "2":
      s2b.append(cardName)
    if str(cardStage) == "3":
      s3b.append(cardName)

    
  RS = os.getenv('ROBLOSECURITY')
  roblox = Client(RS)

  counter = 1
  footCount = 1

  newPage = {}

  for x in s3b:
    on24 = False
    cardNameSplit = x.split(":")

    userID = cardNameSplit[0]
    stage = cardNameSplit[1]
    reason = cardNameSplit[2]

    user = await roblox.get_user(int(userID))
    currentName = user.name

    newPage[currentName] = reason
    
    counter = counter + 1
    print(counter)
    if counter == 24:
      print("new page moment")
      s3bEmbeds.append(newPage)
      newPage = {}

      footCount = footCount + 1
      on24 = True


      counter = 1

  if not on24:
    s3bEmbeds.append(newPage)
  #embedVar.clear_fields()

  print("refresh")
  noPage = len(s3bEmbeds)
  channel = bot.get_channel(844991540636286976)
  message = await channel.fetch_message(844991560194064404)

  currentPage = 0
  db["s3p"] = 0
  page = s3bEmbeds[currentPage]
  embedVar = discord.Embed(title="S3B", description="",color=000000)
  foot = "Page "+str(currentPage+1)+"/"+str(len(s3bEmbeds))
  embedVar.set_footer(text=foot)
  for key in page:
    embedVar.add_field(name=key, value=page[key], inline=False)
  await message.edit(embed=embedVar)

  await bot.get_channel(841015343749005392).send("Blacklist Refresh for S3B done.")

# logging function for any kind of "admin" command
def adminLog(userPing,fullmessage,comtype,server,channel):
    embedVar = discord.Embed(title="Admin Command Ran", description="",color=000000)
    embedVar.add_field(name="User", value=userPing, inline=False)
    embedVar.add_field(name="Command Type", value=comtype, inline=False)
    embedVar.add_field(name="Full Command", value=fullmessage, inline=False)
    embedVar.add_field(name="Server", value=server, inline=False)
    embedVar.add_field(name="Channel", value=channel, inline=False)
    embedVar.set_footer(text="Command log | Novasaur")
    bot.loop.create_task(bot.get_channel(790939607268851762).send(embed=embedVar))

# checks if a phrase is in the slur list, and which one
def slurCheck(phrase):
  wordstatus = False
  msg = str((phrase)).lower()
  for x in badwords:
    if x in msg:
      wordstatus = x
  return wordstatus

@bot.event
async def on_member_join(member):

  if str(member.guild.id) == "832614351265333279":
    await member.send('Generic welcome message - Saurland')

    channel = bot.get_channel(840554012470542376)
    embedVar = discord.Embed(title="New Join Request", description="",color=000000)
    
    embedVar.add_field(name="Name", value=member.display_name, inline=False)
    embedVar.add_field(name="Ping", value="<@"+str(member.id)+">", inline=False)  
    embedVar.set_footer(text="New join request | Novasaur")    
    toReact = await channel.send(embed=embedVar)
    
    await toReact.add_reaction('👍')
    await toReact.add_reaction('👎')




# @bot.event
# async def on_command_error(ctx,error):
#   logging.error(error)


# @bot.event
# async def on_error(event, *args, **kwargs):
#     message = args[0] #Gets the message object
#     logging.error(traceback.format_exc()) #logs the error

@bot.event
async def on_raw_reaction_add(payload):
  if payload.channel_id != 844991540636286976:
    return
  if payload.message_id != 844991560194064404:
    return
  print(payload.emoji)
  currentPage = int(db["s3p"]) # get current page

  if str(payload.emoji) == "➡️":
    print("right")
    noPage = len(s3bEmbeds)
    channel = bot.get_channel(844991540636286976)
    message = await channel.fetch_message(844991560194064404)

    if noPage == int(currentPage)+1:
      user = bot.get_user(payload.user_id)
      await message.remove_reaction(payload.emoji, user)
      return

    currentPage = currentPage + 1
    db["s3p"] = int(currentPage)
    page = s3bEmbeds[currentPage]
    embedVar = discord.Embed(title="S3B", description="",color=000000)
    foot = "Page "+str(currentPage+1)+"/"+str(len(s3bEmbeds))
    embedVar.set_footer(text=foot)
    for key in page:
      embedVar.add_field(name=key, value=page[key], inline=False)
    await message.edit(embed=embedVar)
    user = bot.get_user(payload.user_id)
    await message.remove_reaction(payload.emoji, user)

  if str(payload.emoji) == "⬅️":
    print("left")
    noPage = len(s3bEmbeds)
    channel = bot.get_channel(844991540636286976)
    message = await channel.fetch_message(844991560194064404)

    if int(currentPage)+1 == 1:
      user = bot.get_user(payload.user_id)
      await message.remove_reaction(payload.emoji, user)
      return


    currentPage = currentPage - 1
    db["s3p"] = int(currentPage)

    page = s3bEmbeds[currentPage]
    embedVar = discord.Embed(title="S3B", description="",color=000000)
    foot = "Page "+str(currentPage+1)+"/"+str(len(s3bEmbeds))
    embedVar.set_footer(text=foot)
    for key in page:
      embedVar.add_field(name=key, value=page[key], inline=False)
    await message.edit(embed=embedVar)
    user = bot.get_user(payload.user_id)
    await message.remove_reaction(payload.emoji, user)



  

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="you type! | Prefix is '>'!"))
    channel = bot.get_channel(832614393279283211)
    embedVar2 = discord.Embed(title="Bot connected to discord",description=f'Bot successfully connected to Discord at {time.asctime()}.',color=000000)
    embedVar2.set_footer(text="Hello world | Novasaur")
    await channel.send(embed=embedVar2)

    for server in bot.guilds:
      serverlist.append(str(server))
      slist.append(server)
      #await server.me.edit(nick="Novasaur")
      #await server.leave() #activate this to leave all servers
    #inv = await (bot.get_channel(747581697826095260)).create_invite()
    #await user.send(inv)
    await blListRefresh()
    await bot.get_channel(832614393279283211).send("Blacklist refreshed...")
    await checkQ()


@bot.event
async def on_message(message):

  if message.author == bot.user:
    return

  if str(message.author.id) == "819310933197324318":
    # ignore lithium
    return

  if (message.webhook_id):
    # ignore webhook posts
    return

  if "amogus" in str(message.content).lower():
    await message.add_reaction("<:red:760064755649347604>")

  if "owo" in str(message.content).lower():
    toSend = random.choice([
      "(●'◡'●)",
    "ʕʘ‿ʘʔ",
    "༼ つ ◕_◕ ༽つ",
    "(ˉ﹃ˉ)",
    "(⊙_⊙;)",
    "(T_T)",
    "ᓚᘏᗢ",
    "( ´･･)ﾉ(._.`)",
    "(☞ﾟヮﾟ)☞",
    "ඞ"])
    await message.channel.send(toSend)

  if "honk" == str(message.content).lower():
    await message.channel.send("https://cdn.discordapp.com/attachments/642880448862879759/849436442152534016/5b2.png")

  if message.channel.type is not discord.ChannelType.private:
    role = discord.utils.find(lambda r: r.name == 'NOU Agent', message.guild.roles)
    if role in (message.author).roles:
      dynoType = None
      if str(message.content).startswith("?ban "):
        dynoType = "Ban"
      elif str(message.content).startswith("?unban "):
        dynoType = "Unban"
      elif str(message.content).startswith("?warn "):
        dynoType = "Warn"
      elif str(message.content).startswith("?kick "):
        dynoType = "Kick"
      elif str(message.content).startswith("?mute "):
        dynoType = "Mute"
      elif str(message.content).startswith("?unmute "):
        dynoType = "Unmute"
      elif str(message.content).startswith("?delwarn "):
        dynoType = "Warn Deletion"

      if dynoType != None:
        embedVar = discord.Embed(title="Dyno Command Ran", description="",color=000000)
        embedVar.add_field(name="Username", value="<@"+str(message.author.id)+">", inline=False)
        embedVar.add_field(name="Action Type", value=dynoType, inline=False)
        embedVar.add_field(name="Full Message", value=str(message.content), inline=False)
        embedVar.set_footer(text="NOU Dyno Command log | Novasaur")
        channel = bot.get_channel(796891566341226506)
        await channel.send(embed=embedVar)

  if message.channel.type is discord.ChannelType.private:
    channel = bot.get_channel(834397212481028136)
    user = str(message.author.id)
    user = "<@"+user+">"

    embedVar = discord.Embed(title="New Novasaur DM", description="",color=0x00cc00)

    embedVar.add_field(name="Username:", value=(user), inline=False)
    embedVar.add_field(name="Message:",value = message.content,inline=False)
      
    await channel.send(embed=embedVar)

  elif slurCheck(message.content):
    botAdminSlur = False
    slurColour = 000000
    if str(message.author.id) in botadmins:
      botAdminSlur = True
      slurColour = 0xc20000
    phrase = slurCheck(message.content)
    channel = bot.get_channel(832614393279283211) #bot testing server
    pingperson = str(message.author.id)
    pingperson = "<@"+pingperson+">" 
    servername = str(message.guild.name)
    channelname = str(message.channel.name)
    total = str(message.content)

    embedVar = discord.Embed(title="Autofilter Triggered", description="",color=slurColour)

    embedVar.add_field(name="Username:", value=(pingperson), inline=False)
    embedVar.add_field(name="Server:",value = servername,inline=False)
    embedVar.add_field(name="Channel:",value = channelname,inline=False)
    embedVar.add_field(name="Trigger:",value = phrase,inline=False)
    embedVar.add_field(name="Entire Message:",value = total,inline=False)
    embedVar.set_footer(text="Autofilter | Novasaur")
    if botAdminSlur:
        embedVar.set_footer(text="BotAdmin violation - the violating message was not deleted.")
      
    response = "Please don't use words like **"+phrase+"**!"
    channel = bot.get_channel(834397212481028136)
      #nou server

    embedVar = discord.Embed(title="Autofilter Triggered", description="",color=slurColour)
    embedVar.add_field(name="Username:", value=(pingperson), inline=False)
    embedVar.add_field(name="Server:",value = servername,inline=False)
    embedVar.add_field(name="Channel:",value = channelname,inline=False)
    embedVar.add_field(name="Trigger:",value = phrase,inline=False)
    embedVar.add_field(name="Entire Message:",value = total,inline=False)
    embedVar.set_footer(text="Autofilter | Novasaur")
    if botAdminSlur:
        embedVar.set_footer(text="BotAdmin violation - the violating message was not deleted. | Novasaur")
    await channel.send(embed=embedVar)
    channel = bot.get_channel(772748922371440660)
    await channel.send(embed=embedVar)
    channel = bot.get_channel(783668845831127090)
    await channel.send(embed=embedVar)


    try:
      await message.author.send(response)
    except:
      await message.channel.send("Watch your language, "+"<@"+str(message.author.id)+">.")
    finally:
      await message.add_reaction("😡")
      if not botAdminSlur:
        await message.delete()
    return
  if str(message.content).lower() == "good bot":
    await message.channel.send(":D")
  if str(message.content).lower() == "woof":
    await message.channel.send("woof")

  if str(message.author.id) not in blacklist:
    await bot.process_commands(message)

@bot.command()
async def s3b(ctx):
  if str(ctx.message.author.id) != "314394344465498122":
    return
  await blListRefresh()
  for dicto in s3bEmbeds:
    embedVar = discord.Embed(title="S3B", description="",color=000000)
    for key in dicto:
      embedVar.add_field(name=key, value=dicto[key], inline=False)
    await ctx.send(embed=embedVar)

@bot.command()
async def say(ctx,*args):
  if str(ctx.message.author) != "puptaco#3335":
    return
  await ctx.send(' '.join(args))
  await ctx.message.delete()
  adminLog("<@"+str(ctx.message.author.id)+">",str(ctx.message.content),"Say",ctx.message.guild,ctx.message.channel)

@bot.command()
async def logout(ctx):
  if str(ctx.message.author.id) not in botadmins:
    await ctx.send("You are not authorised to shut down this bot.")
    return
  await ctx.send("ZZZZZZZ")
  await ctx.message.delete()
  adminLog("<@"+str(ctx.message.author.id)+">",str(ctx.message.content),"Logout",ctx.message.guild,ctx.message.channel)
  await bot.close()


@bot.command()
async def uptime(ctx):
  print("Fetching time...")
  channel = bot.get_channel(771426494500044851)
  currenttime = time.time()
  timedifference = currenttime - starttime
  humantimedifference = format_timespan(timedifference)
  response = "I've been awake for "+str(humantimedifference)+" !"
  await ctx.send(response)
  await ctx.message.delete()

@bot.command()
async def servers(ctx):
  counter = 1
  embedVar = discord.Embed(title="All Servers", description="Below are all servers this bot is in:")
  for line in serverlist:
    embedVar.add_field(name="Server #"+str(counter), value=(str(line)), inline=False)
    counter = counter + 1
  embedVar.set_footer(text="Server list | Novasaur")
  await ctx.send(embed=embedVar)
  await ctx.message.delete()

@bot.command()
async def botbl(ctx):
  counter = 1
  embedVar = discord.Embed(title="All Blacklisted Users", description="Below are all users who are blacklisted from using this bot. To appeal, please DM <@314394344465498122>.")       
  for line in blacklist:
    embedVar.add_field(name="User #"+str(counter), value=("<@"+str(line)+">"), inline=False)
    counter = counter + 1
  await ctx.send(embed=embedVar)
  await ctx.message.delete()

@bot.command()
async def admins(ctx):
  counter = 1
  embedVar = discord.Embed(title="All Bot Admins", description="Below are all Bot Admins, who may run certain mod-only commands.")       
  for line in botadmins:
    embedVar.add_field(name="Admin #"+str(counter), value=("<@"+str(line)+">"), inline=False)
    counter = counter + 1
  embedVar.set_footer(text="Bot Admins list | Novasaur")
  await ctx.send(embed=embedVar)
  await ctx.message.delete()

@bot.command()
async def oldblsetup(ctx):
  if str(ctx.message.author.id) != "314394344465498122":
    await ctx.send("You are not authorised to run this.")
    return
  keys = db.keys()

  embedVar = discord.Embed(title="Stage 1 Blacklist",color=000000) 
  for x in keys:
    content = db[x]
    contentSplit = content.split(":")
    if contentSplit[0] == "1":
      embedVar.add_field(name=x, value=("*"+contentSplit[1]+"*"), inline=False)
  await ctx.send(embed=embedVar)

  embedVar = discord.Embed(title="Stage 2 Blacklist",color=000000) 
  for x in keys:
    content = db[x]
    contentSplit = content.split(":")
    if contentSplit[0] == "2":
      embedVar.add_field(name=x, value=("*"+contentSplit[1]+"*"), inline=False)
  await ctx.send(embed=embedVar)

  embedVar = discord.Embed(title="Stage 3 Blacklist",color=000000) 
  for x in keys:
    content = db[x]
    contentSplit = content.split(":")
    if contentSplit[0] == "3":
      embedVar.add_field(name=x, value=("*"+contentSplit[1]+"*"), inline=False)
  await ctx.send(embed=embedVar)
  await ctx.message.delete()

@bot.command()
async def oldbl(ctx, *args):
  if str(ctx.message.author.id) != "314394344465498122":
    await ctx.send("You are not authorised to run this.")
    return

  username = args[0]
  username = username.lower()
  stage = args[1]
  reason = ' '.join(args[2:])
  keyVar = username
  keyContent = stage+":"+reason

  try:
    oldstage = str(((db[username]).split(":"))[0])
  except KeyError:
    oldstage = 0
  
  
  db[keyVar] = keyContent

  if stage == "3":
    TRELLO_APP_KEY = os.getenv('TRELLO_APP_KEY')
    TOKEN = os.getenv('TOKEN')
    listID = "600ed147a982530da7b48b87"             #the id for your list 
    cardPos = "bottom"

    trello = TrelloApi(TRELLO_APP_KEY, TOKEN)

    description = "__Discord-issued Trello Ban__\nIssuer: "+str(ctx.message.author.display_name)+"\nReason: "+reason

    newCard = trello.cards.new(username, idList=listID, desc=description, pos=cardPos)
    print(newCard)    #above returns json details of the card just created

  elif (stage == "1") or (stage == "2") or (stage == "0"):
    TRELLO_APP_KEY = os.getenv('TRELLO_APP_KEY')
    TOKEN = os.getenv('TOKEN')
    listID = "600ed147a982530da7b48b87"             #the id for your list 
    cardPos = "bottom"
    trello = TrelloApi(TRELLO_APP_KEY, TOKEN)
    print("Looking for cards with that name...")
    cardList = trello.lists.get_card(listID)
    for x in cardList:
      splity = x["name"].split(":")[0]
      if splity == username:
        print(x['id'])
        toSend = "Card containing the name '"+username+"' has been found, with the ID of: "+x['id']
        print(toSend)
        print("Deleting card...")
        trello.cards.delete(x['id'])
        print("Card deleted!")

  print(keyContent)
  channel = bot.get_channel(771426494500044851)
  await ctx.message.delete()

  keys = db.keys()
  msgs1b = await ctx.fetch_message(840137392991502368)
  msgs2b = await ctx.fetch_message(840137407873679420)
  msgs3b = await ctx.fetch_message(840137436343566399)


  embedVar = discord.Embed(title="Stage 1 Blacklist",color=000000) 
  for x in keys:
    content = db[x]
    contentSplit = content.split(":")
    if contentSplit[0] == "1":
      embedVar.add_field(name=x, value=("*"+contentSplit[1]+"*"), inline=False)
  await msgs1b.edit(embed=embedVar)


  embedVar = discord.Embed(title="Stage 2 Blacklist",color=000000) 
  for x in keys:
    content = db[x]
    contentSplit = content.split(":")
    if contentSplit[0] == "2":
      embedVar.add_field(name=x, value=("*"+contentSplit[1]+"*"), inline=False)
  await msgs2b.edit(embed=embedVar)

  embedVar = discord.Embed(title="Stage 3 Blacklist",color=000000) 
  for x in keys:
    content = db[x]
    contentSplit = content.split(":")
    if contentSplit[0] == "3":
      embedVar.add_field(name=x, value=("*"+contentSplit[1]+"*"), inline=False)
  await msgs3b.edit(embed=embedVar)
  await ctx.message.delete()

  adminLog("<@"+str(ctx.message.author.id)+">",str(ctx.message.content),"Blacklist Setup",ctx.message.guild,ctx.message.channel)

@bot.command()
async def oldblrefresh(ctx,*args):
  if str(ctx.message.author.id) != "314394344465498122":
    await ctx.send("You are not authorised to run this.")
    return
  keys = db.keys()
  msgs1b = await ctx.fetch_message(840137392991502368)
  msgs2b = await ctx.fetch_message(840137407873679420)
  msgs3b = await ctx.fetch_message(840137436343566399)



  embedVar = discord.Embed(title="Stage 1 Blacklist",color=000000) 
  for x in keys:
    content = db[x]
    contentSplit = content.split(":")
    if contentSplit[0] == "1":
      embedVar.add_field(name=x, value=("*"+contentSplit[1]+"*"), inline=False)
  await msgs1b.edit(embed=embedVar)

  embedVar = discord.Embed(title="Stage 2 Blacklist",color=000000) 
  for x in keys:
    content = db[x]
    contentSplit = content.split(":")
    if contentSplit[0] == "2":
      embedVar.add_field(name=x, value=("*"+contentSplit[1]+"*"), inline=False)
  await msgs2b.edit(embed=embedVar)

  embedVar = discord.Embed(title="Stage 3 Blacklist",color=000000) 
  for x in keys:
    content = db[x]
    contentSplit = content.split(":")
    if contentSplit[0] == "3":
      embedVar.add_field(name=x, value=("*"+contentSplit[1]+"*"), inline=False)
  await msgs3b.edit(embed=embedVar)
  await ctx.message.delete()
  adminLog("<@"+str(ctx.message.author.id)+">",str(ctx.message.content),"Blacklist Refresh",ctx.message.guild,ctx.message.channel)

@bot.command()
async def eval(ctx, *, code):
    if (ctx.message.author.id) != 314394344465498122:
      await ctx.send("Denied.")
      return
    str_obj = io.StringIO() #Retrieves a stream of data
    try:
        with contextlib.redirect_stdout(str_obj):
            exec(code)
    except Exception as e:
        return await ctx.send(f"```{e.__class__.__name__}: {e}```")
    await ctx.send(f'```{str_obj.getvalue()}```')
    adminLog("<@"+str(ctx.message.author.id)+">",str(ctx.message.content),"Code Execution",ctx.message.guild,ctx.message.channel)

@bot.command()
async def dm(ctx,*args):
  if (str(ctx.author.id) not in botadmins):
    return
  userID = args[0]
  messagec = ' '.join(args[1:])
  user = await bot.fetch_user(int(userID))
  await user.send(messagec)
  tosend = "**📧 Sent to "+"<@"+str(userID)+"> :** "+messagec+"\nSent by: <@"+str(ctx.message.author.id)+">"
  channel = bot.get_channel(835175591862206524)
  await channel.send(tosend)
  tosend2 = "**📧 Sent to "+"<@"+str(userID)+"> :** "+messagec+"\nSent by: <@"+str(ctx.message.author)+">"
  await ctx.send(tosend2)
  await ctx.message.delete()

@bot.command()
async def bark(ctx):
  await ctx.send("bark")
  
@bot.command()
async def trelloban(ctx):
  if str(ctx.author.id) not in botadmins:
    await ctx.send("You are not authorised to perform this command.")
    return
  TRELLO_APP_KEY = os.getenv('TRELLO_APP_KEY')
  TOKEN = os.getenv('TOKEN')
  listID = "600ed147a982530da7b48b87"             #the id for your list 
  cardPos = "bottom"

  trello = TrelloApi(TRELLO_APP_KEY, TOKEN)
  await ctx.send("Warning: this command should only be used for T3B-ed members, or exploiter alts.")
  await ctx.send("What is the ROBLOX username of the T3B-ed user?")
  msg = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
  username = str(msg.content)

  RS = os.getenv('ROBLOSECURITY')
  await ctx.send("Fetching Roblox instance...")
  try:
    roblox = Client(RS)
  except:
    await ctx.send("Something broke trying to connect to Roblox!")
  try:
    robloxUser = await roblox.get_user_by_username(username)
  except:
    await ctx.send("Error getting user - maybe you gave an invalid user... 🤔")
    return
  userID = robloxUser.id

  userID = str(userID)

  cardName = username + ":"+userID

  await ctx.send("Sending request to Trello to add card.")
  reason = "Not specified."
  description = "__Discord-issued Trello Ban__\nIssuer: "+str(ctx.message.author.display_name)+"\nReason: "+reason
  newCard = trello.cards.new(cardName, idList=listID, desc=description, pos=cardPos)
  await ctx.send("Card created!\nCard details have been logged to the console.")
  print(newCard)    #above returns json details of the card just created
  await ctx.message.delete()
  adminLog("<@"+str(ctx.message.author.id)+">",str(ctx.message.content),"Trelloban",ctx.message.guild,ctx.message.channel)

@bot.command()
async def untrelloban(ctx):
  if str(ctx.author.id) not in botadmins:
    await ctx.send("You are not authorised to perform this command.")
    return
  TRELLO_APP_KEY = os.getenv('TRELLO_APP_KEY')
  TOKEN = os.getenv('TOKEN')
  listID = "600ed147a982530da7b48b87"             #the id for your list 
  cardPos = "bottom"
  trello = TrelloApi(TRELLO_APP_KEY, TOKEN)

  await ctx.send("What is the username of the user being untrellobanned?")
  msg = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
  username = str(msg.content)
  await ctx.send("Looking for cards with that name...")
  cardList = trello.lists.get_card(listID)
  for x in cardList:
    splity = x["name"].split(":")[0]
    if splity == username:
      print(x['id'])
      toSend = "Card containing the name '"+username+"' has been found, with the ID of: "+x['id']
      await ctx.send(toSend)
      await ctx.send("Deleting card...")
      trello.cards.delete(x['id'])
      await ctx.send("Card deleted!")
  await ctx.message.delete()
  adminLog("<@"+str(ctx.message.author.id)+">",str(ctx.message.content),"Untrelloban",ctx.message.guild,ctx.message.channel)

@bot.command()
async def oldblsearch(ctx,args):

  if str(ctx.message.channel.id) != "832652981659893820":
    await ctx.send("Please go to #rt-bot-commands to use this command.")
    return

  TRELLO_APP_KEY = os.getenv('TRELLO_APP_KEY')
  TOKEN = os.getenv('TOKEN')
  listID = "600ed147a982530da7b48b87"             #the id for your list 
  cardPos = "bottom"
  trello = TrelloApi(TRELLO_APP_KEY, TOKEN)
  cardList = trello.lists.get_card(listID)

  username = args
  username = username.lower()
  keys = db.keys()
  trelloBanned = "No"
  stage = "0"
  reason = "N/A"
  try:
    for x in cardList:
      cardname = x["name"]
      if ((cardname.split(":"))[0]).lower() == username:
        trelloBanned = "Yes"
  except:
    print("Trelloban lookup failed")
    trelloBanned = "Unknown"

  if (username in keys):
    content = db[username]
    contentList = content.split(":")
    reason = ' '.join(contentList[1:])
    stage = contentList[0]
    cardList = trello.lists.get_card(listID)
    if (str(stage) == "1") or (str(stage) == "2") or (str(stage) == "3"):
      embedVar = discord.Embed(title=username, description="*This command is deprecated.*\n*It may not show information that is totally up-to-date or correct.*\n*It will be replaced in the future.*",color=000000)
      embedVar.add_field(name="Stage:", value=stage, inline=False)
      embedVar.add_field(name="Reason:", value=reason, inline=False)
      embedVar.add_field(name="Trello Banned?:", value=str(trelloBanned), inline=False)
      await ctx.send(embed=embedVar)
  elif trelloBanned == "Yes":
    embedVar = discord.Embed(title=username, description="*This command is deprecated.*\n*It may not show information that is totally up-to-date or correct.*\n*It will be replaced in the future.*",color=000000)
    embedVar.add_field(name="Stage:", value=stage, inline=False)
    embedVar.add_field(name="Reason:", value=reason, inline=False)
    embedVar.add_field(name="Trello Banned?:", value=str(trelloBanned), inline=False)
    await ctx.send(embed=embedVar)
  else:
    await ctx.send("That user is not BL-ed or trello-banned.")

@bot.command()
async def cmds(ctx):
  embedVar = discord.Embed(title="Public Commands", description="",color=000000)
  embedVar.add_field(name=">about", value="About le bot.", inline=False)
  embedVar.add_field(name=">admins", value="Lists all botadmins i.e. NCs, HoNOU, HoS, Nova Chairman.", inline=False)
  embedVar.add_field(name=">bark", value="Bark!", inline=False)
  embedVar.add_field(name=">dontwoof", value="Oh no! Don't woof!", inline=False)
  embedVar.add_field(name=">botbl", value="Lists all users blacklisted from using the bot (i.e. are ignored).", inline=False)
  embedVar.add_field(name=">cmds", value="This command!", inline=False)
  embedVar.add_field(name=">help", value="Lists all commands.", inline=False)
  embedVar.add_field(name=">floppa", value="Shows floppa gif.", inline=False) ## Floppa Added to the list.
  embedVar.add_field(name=">servers", value="Lists all servers the bot is in.", inline=False)
  embedVar.add_field(name=">uptime", value="Shows how long the bot has been connected to Discord.", inline=False)
  await ctx.send(embed=embedVar)

  embedVar = discord.Embed(title="Restricted Commands (NOU-related)", description="These are commands that can only be run in the NOU Guild.",color=000000)
  embedVar.add_field(name=">nousearch <username>", value="Currently a blsearch clone.\nIn the future, will show NOU records on an individual as well as any blacklist information.", inline=False)
  await ctx.send(embed=embedVar)

  embedVar = discord.Embed(title="Restricted Commands (NS/management-related)", description="Some commands are not shown here as they are legacy commands kept as a backup.",color=000000)
  embedVar.add_field(name=">blsearch <username>", value="[RT+/ADV+] Allows lookup of a user, showing blacklist and trelloban status.\nMust be run in rt-bot-commands.", inline=False)
  embedVar.add_field(name=">bl <username> <stage> <reason>", value="[BotAdmin+] Allows blacklist status of a user to be modified.\nMust be run in #rt-blacklist to function correctly.", inline=False)
  embedVar.add_field(name=">logout", value="[BotAdmin+] Disconnects the bot from Discord temporarily.\nOnly use in emergencies/when told to by Trio or fat.", inline=False)
  embedVar.add_field(name=">trelloban", value="[BotAdmin+] Manually trellobans the provided Roblox username.", inline=False)
  embedVar.add_field(name=">untrelloban", value="[BotAdmin+] Manually untrellobans the provided Roblox username.", inline=False)
  embedVar.add_field(name=">dm <Discord user id>", value="[BotAdmin+] DMs the provided user with the provided content.\n*Report abuse of this command to Trio.*", inline=False)
  embedVar.add_field(name=">granks <group id>", value="[BotAdmin+] Fetches the group ranks of the Roblox group with the provided group ID.\nBotAdmin+ to avoid abuse.", inline=False)
  embedVar.add_field(name=">say <text>", value="[Trio] Says the provided string in chat.", inline=False)
  embedVar.add_field(name=">blsetup", value="[Trio] Setups the blacklist posts.\nNeeds internal configuration after the command is run.", inline=False)  
  embedVar.add_field(name=">blrefresh", value="[Trio] Refreshes the blacklist.\nMust be run in #rt-blacklist to function correctly.\nPrivate to prevent abuse and ratelimiting.", inline=False)
  embedVar.add_field(name=">eval <code>", value="[Trio] Executes the provided python code.", inline=False)
  await ctx.send(embed=embedVar)

@bot.command()
async def about(ctx):
  embedVar = discord.Embed(title="<:triodoge:784565546036232192>", description="",color=000000)
  embedVar.add_field(name="About", value="Novasaur is a small auxiliary bot which works alongside <@819310933197324318> and the Lithium in-game admin to complete management and moderation tasks.\nIn the past, it performed a wider range of jobs, but many of these tasks have since been transferred to <@819310933197324318>.\nMore features may be given to this bot, but this is not considered a priority.\nContact <@314394344465498122> for bugs or suggestions.", inline=False)
  embedVar.set_footer(text="About | Novasaur")
  await ctx.send(embed=embedVar)

@bot.command()
async def credits(ctx):
  embedVar = discord.Embed(title="Credits <:triodoge:784565546036232192>", description="",color=000000)
  embedVar.add_field(name="Triosar", value="- Most of the code used in this bot, not including modules\n- Maintaining and development of the bot", inline=False)
  embedVar.add_field(name="Oveckin890", value="- Github contributor - minor commands.", inline=False)
  embedVar.add_field(name="P3tray", value="- Developed Lithium ingame admin, which shares information with Novasaur on trellobans.\n- Helped develop past Novasaur functions.", inline=False)
  embedVar.add_field(name="RandomArsenalAcc", value="- Helped with testing.", inline=False)
  embedVar.add_field(name="JMKDev", value="- Developed the ro.py module, which is used to connect this bot to Roblox.", inline=False)
  embedVar.add_field(name="Other Credits", value="This bot uses many other modules to simplify my life, such as:\n- discord.py\n- A python module to connect to Trello", inline=False)
  embedVar.set_footer(text="Credits | Novasaur")
  await ctx.send(embed=embedVar)

@bot.command()
async def noucheck(ctx,*args):
  user = ctx.author
  role = discord.utils.find(lambda r: r.name == 'NOU Agent', ctx.message.guild.roles)
  if role in (ctx.author).roles:
    await ctx.send("you are nou person")
  else:
    await ctx.send("no nou moment")

@bot.command()
async def oldsuscheck(ctx): # suscheck based on my bl 
  return

@bot.command()
async def suscheck(ctx): # suscheck based on p3s bl
  return

@bot.command()
async def zero(ctx):
  await bot.fetch_user(5567)

@bot.command()
async def bl(ctx,*args):
  toClear = []
  if str(ctx.author.id) not in botadmins:
    await ctx.send("You must be a botadmin to use this command.")
    return
  username = str(args[0])
  newStage = str(args[1])
  reason = str(' '.join(args[2:]))

  if (str(newStage).isdigit()) == False:
    await ctx.send("You haven't entered a valid stage! (Probably, you entered a word).")
    return

  RS = os.getenv('ROBLOSECURITY')
  a = await ctx.send("Fetching Roblox instance...")
  toClear.append(a)
  try:
    roblox = Client(RS)
  except:
    await ctx.send("Something broke trying to connect to Roblox!")
  try:
    robloxUser = await roblox.get_user_by_username(username)
  except:
    await ctx.send("Error getting user - maybe you gave an invalid user... 🤔")
    return
  userID = robloxUser.id

  clearUser(userID)

  TRELLO_APP_KEY = os.getenv('TRELLO_APP_KEY')
  TOKEN = os.getenv('TOKEN')
  cardPos = "bottom"
  listID = "6093ccae8f0a0a4e409fa1ce"
  title = str(userID) + ":" + str(newStage)+":"+reason
  
  description = "__Blacklist__\nIssuer: "+str(ctx.message.author.display_name)+"\nReason: "+reason
  b = await ctx.send("Getting Trello thingies")
  toClear.append(b)

  try: 
    trello = TrelloApi(TRELLO_APP_KEY, TOKEN)
  except: 
    await ctx.send("Something broke getting Trello...")
  c = await ctx.send("Writing new card...")
  toClear.append(c)
  try:
    newCard = trello.cards.new((title), idList=listID, desc=description, pos=cardPos)
  except:
    await ctx.send("Couldn't add new card :(")

  channel = bot.get_channel(839861409448984626)
  await channel.send("Username: "+username+"\nID: "+str(userID)+"\nNew Stage: "+str(newStage)+"\nReason: "+reason+"\nIssuer: "+str(ctx.message.author.display_name))

  d = await ctx.send("Card added!")
  toClear.append(d)

  if str(newStage) == "3":
    e = await ctx.send("Adding new card to trello-ban list..")
    toClear.append(e)
    listID = "600ed147a982530da7b48b87"
    title = str(username)+":"+str(userID)
    try:
      newCard = trello.cards.new(title, idList=listID, desc=description, pos=cardPos)
    except:
      await ctx.send("Couldn't add new card :(")
    f = await ctx.send("Card added!")
    toClear.append(f)
  else:
    listID = "600ed147a982530da7b48b87"
    e = await ctx.send("Checking if user is trello-banned...")
    toClear.append(e)
    try:
      cardList = trello.lists.get_card(listID)
    except:
      await ctx.send("Couldn't get list...")
    for x in cardList:
      try:
        splity = str(x["name"].split(":")[1])
      except:
        print("uh oh, stinky")
      if splity == str(userID):
        f = await ctx.send("Card for this ID found...")
        toClear.append(f)
        try:
          trello.cards.delete(x['id'])
        except: 
          await ctx.send("Couldn't delete card...")
        g = await ctx.send("Card deleted!")
        toClear.append(g)
  h = await ctx.send("Trelloban check finished!")
  toClear.append(h)

  i = await ctx.send("Command done!\n*These messages will be deleted shortly.*")
  toClear.append(i)  
  
  msgs1b = await ctx.fetch_message(840137392991502368)
  msgs2b = await ctx.fetch_message(840137407873679420)
  msgs3b = await ctx.fetch_message(840137436343566399)


  TRELLO_APP_KEY = os.getenv('TRELLO_APP_KEY')
  TOKEN = os.getenv('TOKEN')
  listID = "6093ccae8f0a0a4e409fa1ce"
  trello = TrelloApi(TRELLO_APP_KEY, TOKEN)
  cardList = trello.lists.get_card(listID)


  embedVar = discord.Embed(title="Stage 1 Blacklist",color=000000)
  for x in cardList:
    try:
      print(x["name"])
      ID = (str(x["name"].split(":")[0]))
      stage = (str(x["name"].split(":")[1]))
      if str(stage) == "1":
        print("yes")
        RS = os.getenv('ROBLOSECURITY')
        roblox = Client(RS)
        user = await roblox.get_user(int(ID))
        currentName = user.name
        embedVar.add_field(name=currentName, value=((str(x["name"].split(":")[2]))), inline=False)
        print("added")
      else:
        print("no")
    except:
      print("error")
  await msgs1b.edit(embed=embedVar)


  embedVar = discord.Embed(title="Stage 2 Blacklist",color=000000)
  for x in cardList:
    try:
      print(x["name"])
      ID = (str(x["name"].split(":")[0]))
      stage = (str(x["name"].split(":")[1]))
      if str(stage) == "2":
        print("yes")
        RS = os.getenv('ROBLOSECURITY')
        roblox = Client(RS)
        user = await roblox.get_user(int(ID))
        currentName = user.name
        embedVar.add_field(name=currentName, value=((str(x["name"].split(":")[2]))), inline=False)
        print("added")
      else:
        print("no")
    except:
      print("error")
  await msgs2b.edit(embed=embedVar)


  embedVar = discord.Embed(title="Stage 3 Blacklist",color=000000)
  for x in cardList:
    try:
      print(x["name"])
      ID = (str(x["name"].split(":")[0]))
      stage = (str(x["name"].split(":")[1]))
      if str(stage) == "3":
        print("yes")
        RS = os.getenv('ROBLOSECURITY')
        roblox = Client(RS)
        user = await roblox.get_user(int(ID))
        currentName = user.name
        embedVar.add_field(name=currentName, value=((str(x["name"].split(":")[2]))), inline=False)
        print("added")
      else:
        print("no")
    except:
      print("error")
  await msgs3b.edit(embed=embedVar)

  await asyncio.sleep(5)



  for msg in toClear:
    await msg.delete()
  await ctx.message.delete()
  adminLog("<@"+str(ctx.message.author.id)+">",str(ctx.message.content),"Blacklist",ctx.message.guild,ctx.message.channel)

@bot.command()
async def blsetup(ctx):
  if str(ctx.message.author.id) != "314394344465498122":
    await ctx.send("This command is private to prevent abuse.")
    return
  TRELLO_APP_KEY = os.getenv('TRELLO_APP_KEY')
  TOKEN = os.getenv('TOKEN')
  listID = "6093ccae8f0a0a4e409fa1ce"
  trello = TrelloApi(TRELLO_APP_KEY, TOKEN)
  cardList = trello.lists.get_card(listID)


  embedVar = discord.Embed(title="Stage 1 Blacklist",color=000000)
  for x in cardList:
    try:
      print(x["name"])
      ID = (str(x["name"].split(":")[0]))
      stage = (str(x["name"].split(":")[1]))
      if str(stage) == "1":
        print("yes")
        RS = os.getenv('ROBLOSECURITY')
        roblox = Client(RS)
        user = await roblox.get_user(int(ID))
        currentName = user.name
        embedVar.add_field(name=currentName, value=((str(x["name"].split(":")[2]))), inline=False)
        print("added")
      else:
        print("no")
    except:
      print("error")
  await ctx.send(embed=embedVar)


  embedVar = discord.Embed(title="Stage 2 Blacklist",color=000000)
  for x in cardList:
    try:
      print(x["name"])
      ID = (str(x["name"].split(":")[0]))
      stage = (str(x["name"].split(":")[1]))
      if str(stage) == "2":
        print("yes")
        RS = os.getenv('ROBLOSECURITY')
        roblox = Client(RS)
        user = await roblox.get_user(int(ID))
        currentName = user.name
        embedVar.add_field(name=currentName, value=((str(x["name"].split(":")[2]))), inline=False)
        print("added")
      else:
        print("no")
    except:
      print("error")
  await ctx.send(embed=embedVar)


  embedVar = discord.Embed(title="Stage 3 Blacklist",color=000000)
  for x in cardList:
    try:
      print(x["name"])
      ID = (str(x["name"].split(":")[0]))
      stage = (str(x["name"].split(":")[1]))
      if str(stage) == "3":
        print("yes")
        RS = os.getenv('ROBLOSECURITY')
        roblox = Client(RS)
        user = await roblox.get_user(int(ID))
        currentName = user.name
        embedVar.add_field(name=currentName, value=((str(x["name"].split(":")[2]))), inline=False)
        print("added")
      else:
        print("no")
    except:
      print("error")
  await ctx.send(embed=embedVar)
  adminLog("<@"+str(ctx.message.author.id)+">",str(ctx.message.content),"Blacklist Setup",ctx.message.guild,ctx.message.channel)



@bot.command()
async def blrefresh(ctx):
  if str(ctx.message.author.id) != "314394344465498122":
    await ctx.send("This command is private to prevent abuse.")
    return

  msgs1b = await ctx.fetch_message(840137392991502368)
  msgs2b = await ctx.fetch_message(840137407873679420)
  msgs3b = await ctx.fetch_message(840137436343566399)


  TRELLO_APP_KEY = os.getenv('TRELLO_APP_KEY')
  TOKEN = os.getenv('TOKEN')
  listID = "6093ccae8f0a0a4e409fa1ce"
  trello = TrelloApi(TRELLO_APP_KEY, TOKEN)
  cardList = trello.lists.get_card(listID)


  embedVar = discord.Embed(title="Stage 1 Blacklist",color=000000)
  for x in cardList:
    try:
      print(x["name"])
      ID = (str(x["name"].split(":")[0]))
      stage = (str(x["name"].split(":")[1]))
      if str(stage) == "1":
        print("yes")
        RS = os.getenv('ROBLOSECURITY')
        roblox = Client(RS)
        user = await roblox.get_user(int(ID))
        currentName = user.name
        embedVar.add_field(name=currentName, value=((str(x["name"].split(":")[2]))), inline=False)
        print("added")
      else:
        print("no")
    except:
      print("error")
  await msgs1b.edit(embed=embedVar)


  embedVar = discord.Embed(title="Stage 2 Blacklist",color=000000)
  for x in cardList:
    try:
      print(x["name"])
      ID = (str(x["name"].split(":")[0]))
      stage = (str(x["name"].split(":")[1]))
      if str(stage) == "2":
        print("yes")
        RS = os.getenv('ROBLOSECURITY')
        roblox = Client(RS)
        user = await roblox.get_user(int(ID))
        currentName = user.name
        embedVar.add_field(name=currentName, value=((str(x["name"].split(":")[2]))), inline=False)
        print("added")
      else:
        print("no")
    except:
      print("error")
  await msgs2b.edit(embed=embedVar)


  embedVar = discord.Embed(title="Stage 3 Blacklist",color=000000)
  for x in cardList:
    try:
      print(x["name"])
      ID = (str(x["name"].split(":")[0]))
      stage = (str(x["name"].split(":")[1]))
      if str(stage) == "3":
        print("yes")
        RS = os.getenv('ROBLOSECURITY')
        roblox = Client(RS)
        user = await roblox.get_user(int(ID))
        currentName = user.name
        embedVar.add_field(name=currentName, value=((str(x["name"].split(":")[2]))), inline=False)
        print("added")
      else:
        print("no")
    except:
      print("error")
  await msgs3b.edit(embed=embedVar)
  await ctx.message.delete()
  adminLog("<@"+str(ctx.message.author.id)+">",str(ctx.message.content),"Blacklist Refresh",ctx.message.guild,ctx.message.channel)


@bot.command()
async def transfer(ctx):
  if str(ctx.author.id) != "314394344465498122":
    await ctx.send("This is a testing command intended to replace the existing blacklist system.\nOnly Triosar can use it at the moment. Sorry!")
    return

  TRELLO_APP_KEY = os.getenv('TRELLO_APP_KEY')
  TOKEN = os.getenv('TOKEN')
  listID = "6093ccae8f0a0a4e409fa1ce"
  
  trello = TrelloApi(TRELLO_APP_KEY, TOKEN)

  file = open("temp.txt","r")
  lastSeen = None
  toPost = ""
  reason = ""
  for x in file:
    x = x.strip()
    if lastSeen != "name":
      RS = os.getenv('ROBLOSECURITY')
      roblox = Client(RS)
      print(x)
      user = await roblox.get_user_by_username(x)
      ID = user.id
      ID = str(ID)
      toPost = ID+":1"
      asyncio.sleep(1)
      print(toPost)
      lastSeen = "name"
    else:
      reason = x
      toPost = toPost+":"+reason
      print(toPost)
      newCard = trello.cards.new(toPost, idList=listID, desc="Automatic, reasons may be added later.", pos="bottom")
      asyncio.sleep(1)
      lastSeen = "reason"
  await ctx.send("done")

@bot.command()
async def blsearch(ctx,*args):
  toClear = []
  if str(ctx.message.channel.id) != "832652981659893820":
    await ctx.send("This command can only be used in <#832652981659893820>.")
    return
  name = ' '.join(args)
  name = str(name)
  RS = os.getenv('ROBLOSECURITY')
  try:
    roblox = Client(RS)
  except:
    await ctx.send("Something broke trying to connect to Roblox!")
  a = await ctx.send("Fetching Roblox user from username... <a:loading:841014732529598495>")
  try:
    user = await roblox.get_user_by_username(name)
  except:
    await ctx.send("Error getting user - maybe you gave an invalid user... 🤔")
    return
  b = await ctx.send("Found!")
  userId = str(user.id)
  robloxName = str(user.name)


  TRELLO_APP_KEY = os.getenv('TRELLO_APP_KEY')
  TOKEN = os.getenv('TOKEN')
  trello = TrelloApi(TRELLO_APP_KEY, TOKEN)
  listIDBans = "600ed147a982530da7b48b87"
  listIDBL = "6093ccae8f0a0a4e409fa1ce"

  c = await ctx.send("Fetching Trello lists... <a:loading:841014732529598495>")
  cardListBans = trello.lists.get_card(listIDBans)
  cardListBL = trello.lists.get_card(listIDBL)
  d = await ctx.send("Fetched!")
  
  e = await ctx.send("Checking Trelloban list... <a:loading:841014732529598495>")
  trelloBan = False


  for x in cardListBans:
    cardName = x["name"]
    if userId == cardName.split(":")[1]:
      trelloBan = True
  f = await ctx.send("Done!")
  g = await ctx.send("Checking blacklist... <a:loading:841014732529598495>")

  BLBan = False
  for x in cardListBL:
    cardName = x["name"]
    if userId == cardName.split(":")[0]:
      BLBan = True
      try:
        stage = (x["name"].split(":"))[1]
        reason = (x["name"].split(":"))[2]
        stage = str(stage)
      except:
        print("no")
  h = await ctx.send("Done!")
  
  embedVar = discord.Embed(title=robloxName,color=000000)
  embedVar.add_field(name="Trellobanned?", value=(str(trelloBan)), inline=False)
  if BLBan == True:
    if (str(stage) == "1") or (str(stage) == "2") or (str(stage) == "3"):
      embedVar.add_field(name="Blacklisted?", value=(str(BLBan)), inline=False)
      embedVar.add_field(name="Blacklist Stage?", value=(str(stage)), inline=False)
      embedVar.add_field(name="Blacklist Reason?", value=(str(reason)), inline=False)
    else:
      embedVar.add_field(name="Blacklisted?", value=("False"), inline=False)
  else:
    embedVar.add_field(name="Blacklisted?", value=("False"), inline=False)
  try:
    badFriends = await checkFriends(name)
    print(badFriends)
    badFriendsStr = ""
    for x in badFriends:
      badUser = await roblox.get_user(int(x))
      badName = badUser.name
      badFriendsStr = badFriendsStr+badName+" "
    badFriendsStr = "```"+badFriendsStr+"```"
    embedVar.add_field(name="Blacklisted Friends", value=(str(badFriendsStr)), inline=False)
  except:
    print("error getting bad friends")
  embedVar.set_footer(text="Requested by "+str(ctx.message.author.display_name))
  await ctx.send(embed=embedVar)

  for msg in [a,b,c,d,e,f,g,h]:
    await msg.delete()
  await ctx.message.delete()


@bot.command()
async def nousearch(ctx,*args):
  toClear = []
  if str(ctx.message.guild.id) != "665233870689533993":
    await ctx.send("This command can only be used in the NOU guild.")
    return
  name = ' '.join(args)
  name = str(name)
  RS = os.getenv('ROBLOSECURITY')
  try:
    roblox = Client(RS)
  except:
    await ctx.send("Something broke trying to connect to Roblox!")
  a = await ctx.send("Fetching Roblox user from username... <a:loading:841014732529598495>")
  try:
    user = await roblox.get_user_by_username(name)
  except:
    await ctx.send("Error getting user - maybe you gave an invalid user... 🤔")
    return
  b = await ctx.send("Found!")
  userId = str(user.id)
  robloxName = str(user.name)


  TRELLO_APP_KEY = os.getenv('TRELLO_APP_KEY')
  TOKEN = os.getenv('TOKEN')
  trello = TrelloApi(TRELLO_APP_KEY, TOKEN)
  listIDBans = "600ed147a982530da7b48b87"
  listIDBL = "6093ccae8f0a0a4e409fa1ce"

  c = await ctx.send("Fetching Trello lists... <a:loading:841014732529598495>")
  cardListBans = trello.lists.get_card(listIDBans)
  cardListBL = trello.lists.get_card(listIDBL)
  d = await ctx.send("Fetched!")
  
  e = await ctx.send("Checking Trelloban list... <a:loading:841014732529598495>")
  trelloBan = False


  for x in cardListBans:
    cardName = x["name"]
    if userId == cardName.split(":")[1]:
      trelloBan = True
  f = await ctx.send("Done!")
  g = await ctx.send("Checking blacklist... <a:loading:841014732529598495>")

  BLBan = False
  for x in cardListBL:
    cardName = x["name"]
    if userId == cardName.split(":")[0]:
      BLBan = True
      try:
        stage = (x["name"].split(":"))[1]
        reason = (x["name"].split(":"))[2]
        stage = str(stage)
      except:
        print("no")
  h = await ctx.send("Done!")
  
  embedVar = discord.Embed(title=robloxName,color=000000)
  embedVar.add_field(name="Trellobanned?", value=(str(trelloBan)), inline=False)
  if BLBan == True:
    if (str(stage) == "1") or (str(stage) == "2") or (str(stage) == "3"):
      embedVar.add_field(name="Blacklisted?", value=(str(BLBan)), inline=False)
      embedVar.add_field(name="Blacklist Stage?", value=(str(stage)), inline=False)
      embedVar.add_field(name="Blacklist Reason?", value=(str(reason)), inline=False)
    else:
      embedVar.add_field(name="Blacklisted?", value=("False"), inline=False)
  else:
    embedVar.add_field(name="Blacklisted?", value=("False"), inline=False)
  try:
    badFriends = await checkFriends(name)
    print(badFriends)
    badFriendsStr = ""
    for x in badFriends:
      badUser = await roblox.get_user(int(x))
      badName = badUser.name
      badFriendsStr = badFriendsStr+badName+" "
    badFriendsStr = "```"+badFriendsStr+"```"
    embedVar.add_field(name="Blacklisted Friends", value=(str(badFriendsStr)), inline=False)
  except:
    print("error getting bad friends")
  embedVar.set_footer(text="Requested by "+str(ctx.message.author.display_name))
  await ctx.send(embed=embedVar)

  for msg in [a,b,c,d,e,f,g,h]:
    await msg.delete()
  await ctx.message.delete()

@bot.command()
async def loading(ctx):
  if str(ctx.author.id) != "314394344465498122":
    return
  await ctx.message.delete()
  await ctx.send("<a:loading:841014732529598495>")

@bot.command()
async def badfriends(ctx,args):
  await ctx.send(args)
  RS = os.getenv('ROBLOSECURITY')
  try:
    roblox = Client(RS)
  except:
    await ctx.send("Something broke trying to connect to Roblox!")
  badFriends = await checkFriends(args)
  print(badFriends)
  if badFriends:
    badFriendsStr = ""
    for x in badFriends:
      badUser = await roblox.get_user(int(x))
      badName = badUser.name
      badFriendsStr = badFriendsStr+badName+" "
    badFriendsStr = "```"+badFriendsStr+"```"
    await ctx.send(badFriendsStr)

@bot.command()
async def poc(ctx,*args):
  if str(ctx.author.id) != "314394344465498122":
    return
  embedVar = discord.Embed(title="Stage 3 Blacklist",color=000000)
  embedVar.add_field(name="Triosar", value=("Being poopy"), inline=False)
  sent = await ctx.send(embed=embedVar)
  await sent.add_reaction("⬅️")
  await sent.add_reaction("➡️")
  await sent.add_reaction("🔄")
  
@bot.command()
async def poll(ctx,*args):
  embed = discord.Embed(title=' '.join(args),description=f'Sent by: {ctx.message.author}',color=000000)  ## Added embed instead of message.
  embed.set_footer(text="Poll | Novasaur")
  msg = await ctx.send(embed=embed)
  await msg.add_reaction("✅")
  await msg.add_reaction("❌") 

@bot.command()
async def floppa(ctx,*args):
  await ctx.send(random.choice([
    "https://tenor.com/btvbY.gif",
    "https://tenor.com/btFVt.gif",
    "https://tenor.com/bthES.gif",
    "https://tenor.com/bDsKF.gif",
    "https://tenor.com/bC7yO.gif"
  ]))

@bot.command()
async def granks(ctx,*args):
  if str(ctx.message.author.id) not in botadmins:
    await ctx.send("You are not authorised to run this command.")
    return
  idGroup = ' '.join(args)
  idGroup = int(idGroup)
  await ctx.send("Fetching group ranks.\nThis will take a few seconds - assume the command broke if it took longer, and try again in a couple of seconds.")
  RS = os.getenv('ROBLOSECURITY')
  roblox = Client(RS)
  await asyncio.sleep(2)
  name = "pee"
  try:
    await asyncio.sleep(2)
    groupObj = await roblox.get_group(idGroup)
    name = groupObj.name
    await asyncio.sleep(2)
    roles = await groupObj.get_roles()

  except Exception as e:
    e = "Error: "+"`"+str(e)+"`"
    await ctx.send(str(e))
    try:
      await ctx.send("Failed. Retrying... (1/3)")
      await asyncio.sleep(2)
      groupObj = await roblox.get_group(idGroup)
      name = groupObj.name
      await asyncio.sleep(2)
      roles = await groupObj.get_roles()

    except Exception as e:
      e = "Error: "+"`"+str(e)+"`"
      await ctx.send(str(e))
      try:
        await ctx.send("Failed. Retrying... (2/3)")
        await asyncio.sleep(2)
        groupObj = await roblox.get_group(idGroup)
        name = groupObj.name
        await asyncio.sleep(2)
        roles = await groupObj.get_roles()
      
      except Exception as e:
        e = "Error: "+"`"+str(e)+"`"
        await ctx.send(str(e))
        try:
          await ctx.send("Failed. Retrying... (3/3)")
          await asyncio.sleep(2)
          groupObj = await roblox.get_group(idGroup)
          name = groupObj.name
          await asyncio.sleep(2)
          roles = await groupObj.get_roles()

        except Exception as e:
          e = "Error: "+"`"+str(e)+"`"
          await ctx.send(str(e))
          await ctx.send("Couldn't get group ranks.")
          return
  print(groupObj.name)
  embedVar = discord.Embed(title=name,color=000000)
  for x in roles:
    name = (x.name)
    val = (x.rank)
    embedVar.add_field(name=x.name, value=(x.rank), inline=False)
  embedVar.set_footer(text="Group Ranks | Novasaur")    
  await ctx.send(embed=embedVar)

@bot.command()
async def dontwoof(ctx):
  await ctx.send("https://cdn.discordapp.com/attachments/657008895776129028/771842764894896138/Woof.mov")
  await ctx.message.delete()

@bot.command()
async def bloxsearch(ctx,*args):
  if str(ctx.message.author.id) not in botadmins:
    await ctx.send("You are not authorised to run this command.")
    return

  baseURL = "https://api.blox.link/v1/user/"
  discID = args[0] # the discord id provided
  discID = str(discID)
  reqURL = baseURL + discID

  r = requests.get(reqURL)
  r = r.json() # make it accessible as a dict

  if r["status"] == "error": # if the request failed
    errorText = r["error"]
    await ctx.send("This command failed.\nError reason is:")
    toSend = "`"+errorText+"`"
    await ctx.send(toSend)
  else:
    await ctx.send("Primary account of the user is:")
    toSend = "`"+r["primaryAccount"]+"`"
    await ctx.send(toSend)

keep_alive.keep_alive()
bot.run(TOKEN)