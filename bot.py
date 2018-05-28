#! /usr/bin/python3

ill = 0

import json
import logging
import os
import requests
import sys
import tomd
import emoji
from datetime import datetime

import configparser
import dateutil.parser
import discord

import pytz
from pytz import common_timezones

retrys = 0 # enter number of allowed reconnects(0 = no limit)

print(os.getcwd())

logging.basicConfig(level=logging.INFO)


headers = {
    'User-Agent': 'Mozilla/5.0 (gogoBot; Ubuntu; Linux x86_64; rv:1) Gecko/20100101 gogoBot/1.0'}

config = configparser.ConfigParser()

def ordenal(number):
    if number % 10 == 1 and number % 100//10 != 1:
        return "ˢᵗ"
    elif number % 10 == 2 and number % 100//10 != 1:
        return "ⁿᵈ"
    elif number % 10 == 3 and number % 100//10 != 1:
        return "ʳᵈ"
    else:
        return "ᵗʰ"


cmdhelp = {}
cmds= {}

client = discord.Client()

logger = logging.getLogger('bot')

@client.event
async def on_ready():
    print('Logged in as '+client.user.name)
    await client.change_presence(game=discord.Game(name='type !help for commands'))

def checktwitch(msg):
    twitchhead=headers
    twitchhead['Client-ID'] = "get your own ID"
    url = "https://api.twitch.tv/helix/streams?user_login=loadingartist&type=live"
    resp = requests.get(url=url, headers=twitchhead, timeout=5)

    data = json.loads(resp.text)

    if not data['data']:
        return msg
    else:
        game = data['data'][0]['game_id']
        url = "https://api.twitch.tv/helix/games?id={0}".format(game)
        resp = requests.get(url=url, headers=twitchhead)
        data = json.loads(resp.text)
        return "Loading Artist IS LIVE, Playing {0}".format(data['data'][0]['name'])

async def gettime(msg):
    await client.send_typing(msg.channel)
    fmt = '%H:%M %Y-%m-%d'
    if msg.content.startswith("!gregtime"):
        tz = pytz.timezone("Pacific/Auckland")
    elif msg.content.startswith("!time"):
        tz = pytz.timezone("Etc/UTC")
        try:
            cmd = msg.content.split(" ")
            tz = pytz.timezone(cmd[1])
        except exception as e:
            logger.warn(e)
    now = datetime.now(tz)
    timefmt = now.strftime(fmt)
    return "The time in {} is {}".format(tz.zone, timefmt)

async def wiki(message):
    await client.send_typing(message.channel)

    search=message.content.split(" ",1)
    link="https://en.wikipedia.org/w/api.php"
    payload = {'action': 'query', 'list': 'search', 'format': 'json', 'srsearch': search[1]}
    page = requests.get(link, headers=headers, timeout=5, params=payload)
    page.encoding = 'UTF-8'
    response = json.loads(page.text)
    result = response['query']['search'][0]

    url = "https://en.wikipedia.org/wiki/" + result['title'].replace(" ", "_")

    msg = "{}: {}... {}".format(result['title'], tomd.Tomd(result['snippet'].split(".")[0]).markdown, url)
    return msg

async def blocktext(msg):
    await client.send_typing(msg.channel)
    word = msg.content.split(" ")
    wordarray=word[1].spit()
    output = ""
    for letter in wordarray:
        output += " :regional_indicator_{0}:".format(letter.lower())
    output = emoji.emojize(output,use_aliases=True)
    return output


async def social(message):
    await client.send_typing(message.channel)
    command = message.content.lower()
    command = command.split(" ")
    msg = ""
    msg = socialmsg[command[0].replace("!","")]
    return msg

speq=0

async def next(message):
    await client.send_typing(message.channel)

    now = datetime.now(pytz.utc)

    time=now.strftime("%Y-%m-%dT%H:%M:%S.0Z")
    url = "https://www.speq.me/api/streamschedule/?format=json&limit=1&start={0}&user={1}".format(time, speqname)
    if speq == 1:
        resp = requests.get(url=url, headers=headers, timeout=3)
        data = json.loads(resp.text)
        streamtype = data["results"][0]['title']
        nexttime= dateutil.parser.parse(data["results"][0]['starttime'])
        if nexttime > now:
            td = nexttime - now
            intime = ""
            if td.days != 0:
                intime += "{0}d ".format(td.days)
            if td.seconds // 3600 != 0:
                intime += "{0}h ".format(td.seconds // 3600)
            if td.seconds % 3600 // 60 != 0:
                intime += "{0}m ".format(td.seconds % 3600 // 60)
            msg = "The next stream is {0}!!! in {1}({2})".format(streamtype, intime, str(nexttime.strftime('aka %H:%M on the %-d{0} of %b UTC'.format(ordenal(nexttime.day)))))
        else:
            msg="<@98372271772553216> IS LATE"
            la=discord.utils.get(message.server.members, discriminator = 6142)
    else:
        msg = "Speq Is Down"
    if(ill==0):
            msg = checktwitch(msg)
    else:
            msg = "Loading Artist is ill"
    return msg

async def youtube(message):
    await client.send_typing(message.channel)
    query = message.content.replace("!yt ", "")
    url = "https://www.googleapis.com/youtube/v3/search?q={1}&part=snippet&maxResults=1&key={0}&type=video".format(ytkey,query)
    resp = requests.get(url=url)
    data = json.loads(resp.text)
    id = data["items"][0]["id"]["videoId"]
    return "https://youtu.be/"+id

async def help(message):
    msg = "Hello, this is gogoBot under the name {0}\r\n".format(client.user.name)
    for key, value in cmdhelp.items():
        msg+="\r\n**{0}**: {1}\r\n".format(key, value)
    msg += "\r\nThe source, raw source: https://github.com/ioangogo/gogoBot/"
    await client.send_message(message.author, msg)
    return ""

async def give(msg):
    emoji = ""
    if msg.content.startswith("!coffee"):
        emoji = "☕"
    elif msg.content.startswith("!cake"):
        emoji = "🎂"

    if not msg.mentions:
        await client.add_reaction(msg, emoji)
    else:
        await client.send_typing(msg.channel)
        return "_Gives {} to {} from {}_".format(emoji, msg.mentions[0].mention,msg.author.mention)

async def hug(msg):
    await client.send_typing(msg.channel)
    if not msg.mentions:
        return "_Hugs {}_".format(msg.author.mention)
    else:
        return "_Gives a hug to {} from {}_".format(msg.mentions[0].mention,msg.author.mention)

#@client.event
#async def discord.on_member_join(member):
#    msg = "Morning {}, Welcome to The Loading Artist Discord".format(member.mention)
#    await client.send_message(message.channel, msg)

@client.event
async def on_message(message):
    command = message.content.lower()
    print(command)
    if not message.author.bot and message.content.startswith("!"):
        command = command.split(" ")
        if command[0] in cmds:
            msg = await cmds[command[0]](message)
            if msg != "":
                tmp = await client.send_message(message.channel, msg)

@client.event
async def on_server_join(server):
    logger.info("Joined server{0}".format(server.name))

# load config, im doing this here so that i can use it to use lists to set the commands
if os.path.exists("config.ini"):
    cmds["!hug"] = hug
    cmds["!cake"] = give
    cmds["!coffee"] = give
    cmds["!help"] = help
    cmds["!wiki"] = wiki
    cmds["!gregtime"] = gettime
    cmds["!time"] = gettime
    cmds["!bubbletext"] = blocktext
    cmdhelp["!wiki"] = "Searches wikipedia. Syntax: ```!wiki [query]```"
    cmdhelp["!hug"] = "We have ironed out the bug in the orginal bot and this bot now gives warm hugs. Mention a user **after** the command to send a hug to them"
    cmdhelp["!gregtime"] = "Returns the time for LoadingArtist"
    cmdhelp["!time"] = "Gets the time in the timezone, Syntax ```!time [TZ formatted timezone]```consult this list for timezones and their TZ format https://en.wikipedia.org/wiki/List_of_tz_database_time_zones"

    config.read("config.ini")
    try:
        token = config['Config']['token']
    except configparser.NoSectionError:
        sys.exit("Error, Missing token, please make a bot for this")
    socialmsg={}
    if 'Messages' in config:
        messages = config['Messages']
        for site in messages:
             cmds["!"+site]=social
             socialmsg[site] = messages[site]
        cmdhelp["![site]"] = "This command prints out the url for the site that called it. list of sites: {0}".format( list(socialmsg))
    if 'speqname' in config['Config']:
        cmdhelp["!next"] = "This command returns the time remaining till the next stream, all times are in utc"
        cmds["!next"]=next
        speqname = config['Config']['speqname']
    if 'youtubekey' in config['Config']:
        cmdhelp["!yt"] = "Searches youtube. Syntax: ```!yt [query]```"
        cmds["!yt"]=youtube
        ytkey = config['Config']['youtubekey']

else:
    sys.exit("Error, No Config")

trys=0

while(True):
    try:
        client.run(token)
    except:
        logger.error("Connection faliure")
