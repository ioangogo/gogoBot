#! /usr/bin/python3
import json
import logging
import os
import requests
import sys
from datetime import datetime

import configparser
import dateutil.parser
import discord
import pytz

print(os.getcwd())

logging.basicConfig(level=logging.INFO)

config = configparser.ConfigParser()

cmdhelp = {}
cmds= {}

client = discord.Client()

logger = logging.getLogger('bot')

@client.event
async def on_ready():
    print('Logged in as '+client.user.name)
    await client.change_presence(game=discord.Game(name='type !help for commands'))

async def social(message):
    command = message.content.split(" ")
    msg = ""
    if len(command) > 1:
        if(command[1] == "list"):
            keynum = len(socialmsg)
            for key, value in socialmsg.items():
                comma = ""
                if keynum != 0:
                    comma = ", "
                msg += "{0}{1}".format(key,comma)
        else:
            msg = socialmsg[command[1]]
    else:
        msg = "You can find " + message.server.name + " on\r\n"
        keynum = len(socialmsg)
        for s, txt in socialmsg.items():
            comma = ""
            if keynum != 0:
                    comma = ", "
            msg += "{0}: {1}{2}".format(s, txt, comma)
    return msg

async def next(message):
    now = datetime.now(pytz.utc)

    time=now.strftime("%Y-%m-%dT%H:%M:%S.0Z")
    url = "https://www.speq.me/api/streamschedule/?format=json&limit=1&start={0}&user={1}".format(time, speqname)
    resp = requests.get(url=url)
    data = json.loads(resp.text)
    nexttime= dateutil.parser.parse(data["results"][0]['starttime'])

    td = nexttime - now
    intime = ""
    if td.days != 0:
        intime += "{0}d, ".format(td.days)
    if td.seconds // 3600 != 0:
        intime += "{0}h, ".format(td.seconds // 3600)
    if td.seconds % 3600 // 60 != 0:
        intime += "{0}m, ".format(td.seconds % 3600 // 60)
    if td.seconds % 60 != 0:
        intime += "{0}s".format(td.seconds % 60)

    streamtype = data["results"][0]['title']
    msg = "The next stream is {0}!!! in {1}({2})".format(streamtype, intime, str(nexttime.strftime('aka %H:%M %-dᵗʰ of %b UTC')))


    return msg

async def youtube(message):
    query = message.content.replace("!yt ", "")
    url = "https://www.googleapis.com/youtube/v3/search?q={1}&part=snippet&maxResults=1&key={0}".format(ytkey,query)
    resp = requests.get(url=url)
    data = json.loads(resp.text)
    id = data["items"][0]["id"]["videoId"]
    return "https://youtu.be/"+id

async def help(message):
    msg = "Hello, this is gogoBot under the name {0}\r\n".format(client.user.name)
    for key, value in cmdhelp.items():
        msg+="**{0}**: {1}\r\n".format(key, value)
    msg += "The source, raw source: https://github.com/ioangogo/gogoBot/"
    await client.send_message(message.author, msg)
    return ""

@client.event
async def on_message(message):
    if not message.author.bot and message.content.startswith("!"):
        command = message.content.split(" ")
        try:
            await client.send_typing(message.channel)
            msg = await cmds[command[0]](message)
            if msg != "":
                tmp = await client.send_message(message.channel, msg)
        except KeyError:
            await client.send_message(message.author, "The command you entered is invalid or has not been setup")

@client.event
async def on_server_join(server):
    logger.info("Joined server{0}".format(server.name))

# load config, im doing this here so that i can use it to use lists to set the commands
if os.path.exists("config.ini"):
    cmds["!help"] = help
    config.read("config.ini")
    try:
        token = config['Config']['token']
    except configparser.NoSectionError:
        sys.exit("Error, Missing token, please make a bot for this")
    socialmsg={}
    if 'Messages' in config:
        cmdhelp["!social"] = "This command prints out the urls for the social feeds. Syntax: ```!social [name|list]```"
        cmds["!social"]=social
        messages = config['Messages']
        for site in messages:
             socialmsg[site] = messages[site]
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

client.run(token)
