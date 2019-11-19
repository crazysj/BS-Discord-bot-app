# Works with Python 3.6
# Author: Chandan Gupta 
# https://discordapp.com/
##############
#
# Dependencies:
# python3 -m pip install discord.py==0.16.12
# pip3 install google
# pip3 install beautifulsoup4
# 
##############
#
import random
import asyncio
import aiohttp
import json
import shelve
import urllib.parse
from discord import Game
from discord.ext.commands import Bot
from googlesearch import search


BOT_PREFIX = ("!")
SEARCH_KEY_PREFIX = 'search-history-'
DB_STORAGE = 'user_data_shelf.db'
TOKEN = <TOKEN> #Add token

client = Bot(command_prefix=BOT_PREFIX)


@client.event
async def on_ready():
    await client.change_presence(game=Game(name="with humans"))
    print("Logged in as: " + client.user.name)



@client.command(pass_context=True,)
async def google(context):
    user_result = ""
    result_count = 0
    user_query= context.message.content[8:] #remove !google
    user_query.strip()
    if user_query is None or user_query == '':
        await client.say('Search query can\'t be empty.')
        return
    user_query = user_query[:150] #allowing max length to 150
    print(user_query)
    try:
        
        for j in search(user_query, tld="co.in", num=5, start=0, stop=5, pause=2):
            user_result = user_result + "\n" + urllib.parse.unquote(j)
            result_count += 1
            #print(j)
        print((context.message.author.id)) #Author id is unique

        key = SEARCH_KEY_PREFIX + client.user.name + '-' + str(context.message.author.id)
        search_history = []
        s = shelve.open(DB_STORAGE)

        try:
            search_history = s[key]
        except KeyError:
            print("key not found")

        search_history.append(user_query)
        s[key] = search_history #write new search to storage

        s.close()

    except Exception as e:
        print(e)    

    if result_count == 0:
        await client.say('Oops! Nothing Found.')
    else:
        await client.say("Top " + str(result_count) + " results: \n" + user_result)


@client.command(pass_context=True,)
async def recent(context):
    user_query= context.message.content[8:] #remove !recent 
    user_result = ""
    result_count = 0
    search_history = []
    user_query.strip()
    if user_query is None or user_query == '':
        await client.say('Search query can\'t be empty.')
        return
    elif len(user_query) > 150:
        await client.say('Query length can\'t be more than 150 characters.')
        return     
    try:
        with shelve.open(DB_STORAGE, flag='r') as s:
            try:
                key = SEARCH_KEY_PREFIX + client.user.name + '-' + str(context.message.author.id)
                print(key)
                search_history = s[key]
            except KeyError:
                print("key not found")
        matching_results = [x for x in search_history if user_query in x]
        print(matching_results)
        if matching_results is None or matching_results == []:
            await client.say("Nothing matching found in your serach history.")
        else:
            await client.say("From your search history: \n" + '\n'.join(matching_results)) #can have duplicate queries. user might have serached same query multiple times
    except Exception as e:
        print(e)  
        await client.say("Nothing matching found in your serach history")

@client.event
async def on_message(message):  # event that happens per any message.

    if(message.author == client.user):
        return
    if message.content.lower() == "hi":
        await client.send_message(message.channel, content="hey!")
    await client.process_commands(message)


async def list_servers():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current servers:")
        for server in client.servers:
            print(server.name)
        await asyncio.sleep(600)


client.loop.create_task(list_servers())
client.run(TOKEN)
