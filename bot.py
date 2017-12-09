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
    twitchhead['Client-ID'] = "jxhlk3btt2jdev100dv9vhvs0qtm2c"
    url = "https://api.twitch.tv/helix/streams?user_login=loadingartist&type=live"
    resp = requests.get(url=url, headers=twitchhead)
    data = json.loads(resp.text)
    if not data['data']:
        return msg
    else:
        game = data['data'][0]['game_id']
        url = "https://api.twitch.tv/helix/games?id={0}".format(game)
        resp = requests.get(url=url, headers=twitchhead)
        data = json.loads(resp.text)
        return "Loading Artist IS LIVE, Playing {0}".format(data['data'][0]['name'])

async def social(message):
    command = message.content.lower()
    command = command.split(" ")
    msg = ""
    msg = socialmsg[command[0].replace("!","")]
    return msg

async def next(message):

    now = datetime.now(pytz.utc)

    time=now.strftime("%Y-%m-%dT%H:%M:%S.0Z")
    url = "https://www.speq.me/api/streamschedule/?format=json&limit=1&start={0}&user={1}".format(time, speqname)
    resp = requests.get(url=url, headers=headers)
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
    msg = checktwitch(msg)
    return msg

async def youtube(message):
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

async def hug(msg):
    if not msg.mentions:
        return "_Hugs {}_".format(msg.author.mention)
    else:
        return "_Gives a hug to {} from {}_".format(msg.mentions[0].mention,msg.author.mention)

@client.event
async def on_message(message):
    command = message.content.lower()
    print(command)
    if not message.author.bot and message.content.startswith("!"):
        command = command.split(" ")
        if command[0] in cmds:
            if not message.content.startswith("!help"):
                await client.send_typing(message.channel)
            msg = await cmds[command[0]](message)
            if msg != "":
                tmp = await client.send_message(message.channel, msg)

@client.event
async def on_server_join(server):
    logger.info("Joined server{0}".format(server.name))

# load config, im doing this here so that i can use it to use lists to set the commands
if os.path.exists("config.ini"):
    cmds["!hug"] = hug
    cmds["!help"] = help
    cmdhelp["!hug"] = "We have ironed out the bug in the orginal bot and this bot now gives warm hugs. Mention a user **after** the command to send a hug to them"

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

client.run(token)


