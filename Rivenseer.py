import asyncio
import csv
import discord
import json
import requests
import time
from collections import deque
from datetime import datetime

TOKEN = 'NTYyMzg4ODk5MzY0NzMyOTMw.XKKRag.ILc62i-5kgTejgDQV9dYS4Ss2W4'

client = discord.Client()

defaultPrefix = '.'
defaultPlatform = 'pc'

pcRivenData = list()
xb1RivenData = list()
ps4RivenData = list()
nsRivenData = list()

serverPrefixes = dict()
serverPlatforms = dict()

@client.event
async def on_ready():
	global client
	
	await fetch_riven_data()
	client.loop.create_task(riven_refresh())
	
	get_server_data()
	
	client.loop.create_task(server_data_update())
	
	print('Bot initiated.')
	
@client.event
async def on_server_join(server):
	global defaultPrefix
	global serverPrefixes
	global defaultPlatform
	global serverPlatforms

	serverPrefixes[server.id] = defaultPrefix
	serverPlatforms[server.id] = defaultPlatform
	
@client.event
async def on_server_remove(server):
	global serverPrefixes
	global serverPlatforms
	
	del serverPrefixes[server.id]
	del serverPlatforms[server.id]

@client.event
async def on_message(message):
	global serverPrefixes
	global serverPlatforms

	if message.author == client.user:
		return
	
	# Prefix change ---------
	if message.content.startswith('{0}prefix'.format(serverPrefixes[message.server.id])):
		if message.author.server_permissions.manage_server:
			cmd = message.content.split(" ")
			serverPrefixes[message.server.id] = cmd[1]
			msg = 'My prefix is now \"{0}\"! Use that to summon me!'.format(serverPrefixes[message.server.id])
			await client.send_message(message.channel, msg)
		else:
			await client.send_message(message.channel, 'You do not have permission to change the prefix!')
		
	# Message cleaner -------
	elif message.content.startswith('{0}clean'.format(serverPrefixes[message.server.id])):
		deletedList = await client.purge_from(message.channel, check=is_bot)
		await client.send_message(message.channel, 'Deleted {0} message(s)'.format(len(deletedList)))
		
	# Riven search ----------
	elif message.content.startswith('{0}riven'.format(serverPrefixes[message.server.id])):
		queryString = message.content.replace('{0}riven '.format(serverPrefixes[message.server.id]), '', 1)
		query = queryString.split(", ")
		
		veiled = False
		
		riven = query[0].upper()
		itemType = ''
		
		if riven == 'VEILED KITGUN' or riven == 'VEILED MELEE' or riven == 'VEILED PISTOL' or riven == 'VEILED RIFLE' or riven == 'VEILED SHOTGUN' or riven == 'VEILED ZAW':
			veiled = True
		
		platform = ''
		
		if len(query) == 1:
			platform = serverPlatforms[message.server.id]
		else:
			plat = query[1].lower()
			
			if plat == 'pc':
				platform = 'pc'
			elif plat == 'xb1':
				platform = 'xb1'
			elif plat == 'ps4':
				platform = 'ps4'
			elif plat == 'ns':
				platform = 'ns'
			else:
				await client.send_message(message.channel, 'Platform not recognized. Use `{0}help platform` for a list of valid platforms!'.format(serverPrefixes[message.server.id]))
				return
		
		searchList = list()
		
		global pcRivenData
		global xb1RivenData
		global ps4RivenData
		global nsRivenData
		
		if platform == 'pc':
			searchList = pcRivenData
		elif platform == 'xb1':
			searchList = xb1RivenData
		elif platform == 'ps4':
			searchList = ps4RivenData
		elif platform == 'ns':
			searchList = nsRivenData
		
		rivenEmbed = discord.Embed()
		rivenEmbed.title = 'Rivenseer - Riven Data for {0} -- ({1})'.format(riven.strip(), platform.upper())
		rivenEmbed.description = 'This is the Riven data for {0}'.format(riven.strip())
		rivenEmbed.colour = 0xF7BF25
		
		unrolled = ''
		rolled = ''
		
		foundRiven = False
		
		if veiled == False:
			for r in searchList:
				if riven.strip() == r.compatibility:
					foundRiven = True
					
					if r.rerolled == False:
						unrolled = r
					
					elif r.rerolled == True:
						rolled = r
			
			if foundRiven == True:
				rivenEmbed.add_field(name='UNROLLED RIVEN DATA\n----------------------------------------', value='**Average Price:** {0}\n**Standard Deviation:** {1}\n**Minimum Price:** {2}\n**Maximum Price:** {3}\n**Median:** {4}\n**Riven Popularity:** {5}\n\n'.format(unrolled.avg, unrolled.stddev, unrolled.min, unrolled.max, unrolled.median, unrolled.pop), inline=False)
				
				rivenEmbed.add_field(name='ROLLED RIVEN DATA\n----------------------------------------', value='**Average Price:** {0}\n**Standard Deviation:** {1}\n**Minimum Price:** {2}\n**Maximum Price:** {3}\n**Median:** {4}\n**Riven Popularity:** {5}'.format(rolled.avg, rolled.stddev, rolled.min, rolled.max, rolled.median, rolled.pop), inline=False)
					
		else:
			if riven == 'VEILED KITGUN':
				itemType = 'Kitgun Riven Mod'
				riven = None
			elif riven == 'VEILED MELEE':
				itemType = 'Melee Riven Mod'
				riven = None
			elif riven == 'VEILED PISTOL':
				itemType = 'Pistol Riven Mod'
				riven = None
			elif riven == 'VEILED RIFLE':
				itemType = 'Rifle Riven Mod'
				riven = None
			elif riven == 'VEILED SHOTGUN':
				itemType = 'Shotgun Riven Mod'
				riven = None
			elif riven == 'VEILED ZAW':
				itemType = 'Zaw Riven Mod'
				riven = None
			
				
			for r in searchList:
				if itemType == r.itemType and r.compatibility == None:
					rivenEmbed.add_field(name='VEILED RIVEN DATA\n----------------------------------------', value='**Average Price:** {0}\n**Standard Deviation:** {1}\n**Minimum Price:** {2}\n**Maximum Price:** {3}\n**Median:** {4}\n**Riven Popularity:** {5}'.format(r.avg, r.stddev, r.min, r.max, r.median, r.pop), inline=False)
					foundRiven = True
					
		if foundRiven == True:
			await client.send_message(message.channel, embed=rivenEmbed)
				
		else:
			await client.send_message(message.channel, 'No Riven was found. Try again!')
	
	# Help prompt -----------------
	elif message.content.startswith('{0}help'.format(serverPrefixes[message.server.id])):
		help = message.content.split()
		em = discord.Embed()
		em.title = 'Rivenseer'
		em.colour = 0xF7BF25
		
		if len(help) == 1:
			em.description = 'Hello! I am a bot designed to fetch Warframe Riven Data (provided by the developers) and make it available here in Discord!\nCurrently, my prefix is `{0}`\nIf you would like more info on a command, type `{1}help <command>`!'.format(serverPrefixes[message.server.id], serverPrefixes[message.server.id])
			em.add_field(name='COMMANDS', value='`help` - displays this prompt\n`riven` - gets current Riven data on a weapon\n`platform` - sets the default platform used by the riven command\n`clean` - removes some (if not all) of messages produced by me\n`prefix` - changes the prefix used to summon me', inline=False)
			await client.send_message(message.channel, embed=em)
		else:
			if help[1] == 'help':
				em.description = '`help` - displays the generic help prompt\n`help <command>` - displays more info about the given command'
				await client.send_message(message.channel, embed=em)
			elif help[1] == 'riven':
				em.description = '`riven <weapon>, [platform]` - gets Riven data for that weapon (unrolled rivens and rolled rivens).\n\n**NOTE:** Variant types (Prime, Prisma, Wraith, Vaykor, etc.) should not be included in the weapon name __(with the exception of Euphona Prime, Dakra Prime, and Reaper Prime)__. Sword and Shield weapons must include spaces and the ampersand:\n(Ack & Brunt, Sigma & Octantis, etc.)\n\nThe platform argument is optional, but you can use it to override the default platform setting. If it is omitted, this command will return the Riven data for the default platform (currently {0}).\n\nAll data is actual trade data and not taken from trade chat.\n\n**Examples of valid queries:**\n`{1}riven Lato`, `{2}riven cobra & crane, ns`, `{3}riven REAPER PRIME, xb1`'.format(defaultPlatform.upper(), serverPrefixes[message.server.id], serverPrefixes[message.server.id], serverPrefixes[message.server.id])
				await client.send_message(message.channel, embed=em)
			elif help[1] == 'platform':
				em.description = '`platform <platform>` - sets the default platform for searching rivens (you must have Manage Server permission to use this command).\n\nCurrently, the default platform is {0}\n\nValid platform parameters are `pc`, `xb1`, `ps4`, `ns`'.format(defaultPlatform.upper())
				await client.send_message(message.channel, embed=em)
			elif help[1] == 'clean':
				em.description = '`clean` - removes some (if not all) of my messages from the channel this command is invoked from (bot requires Manage Message permissions)'
				await client.send_message(message.channel, embed=em)
			elif help[1] == 'prefix':
				em.description = '`prefix <newPrefix>` - changes the prefix used to summon me (you must have Manage Server permissions)'
				await client.send_message(message.channel, embed=em)
			else:
				await client.send_message(message.channel, 'No command by that name exists!')
	
	# Default platform switcher -------------
	elif message.content.startswith('{0}platform'.format(serverPrefixes[message.server.id])):
		platform = message.content.replace('{0}platform '.format(serverPrefixes[message.server.id]), '')
		
		if message.author.server_permissions.manage_server == True:
			if platform.lower() == 'pc':
				serverPlatforms[message.server.id] = 'pc'
				await client.send_message(message.channel, 'Default platform changed to PC!')
			elif platform.lower() == 'xb1':
				serverPlatforms[message.server.id] = 'xb1'
				await client.send_message(message.channel, 'Default platform changed to XBox One!')
			elif platform.lower() == 'ps4':
				serverPlatforms[message.server.id] = 'ps4'
				await client.send_message(message.channel, 'Default platform changed to PlayStation 4!')
			elif platform.lower() == 'ns':
				serverPlatforms[message.server.id] = 'ns'
				await client.send_message(message.channel, 'Default platform changed to Nintendo Switch!')
			else:
				await client.send_message(message.channel, 'Platform not recognized. Use `{0}help platform` for more info!'.format(prefix))
		else:
			await client.send_message('You do not have permission to change the default platform!')
			
	elif message.content.startswith('{0}writeCSV'.format(serverPrefixes[message.server.id])):
		with open('serverPrefixes.csv', 'w', newline='') as csvFile:
			write = csv.writer(csvFile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
			write.writerow([message.server.id] + [serverPrefixes[message.server.id]])
				
	elif message.content.startswith('{0}'.format(serverPrefixes[message.server.id])):
		await client.send_message(message.channel, 'Command not recognized. Use the `help` command to see a list of my commands!')

# --------------------------------------------------------------


class Riven:
	def __init__(self, d):
		self.__dict__ = d
	
# --------------------------------------------------------------

async def server_data_update():
	global serverPrefixes
	global serverPlatforms
	
	while True:
		await asyncio.sleep(600)
		
		with open('serverPrefixes.csv', 'w', newline='') as csvfile:
                        prefixWriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        for k, v in serverPrefixes.items():
                                prefixWriter.writerow([k] + [v])
			
		with open('serverPlatforms.csv', 'w', newline='') as csvfile:
			platformWriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
			for k, v in serverPlatforms.items():
				platformWriter.writerow([k] + [v])

async def fetch_riven_data():
	pc = requests.get('http://n9e5v4d8.ssl.hwcdn.net/repos/weeklyRivensPC.json')
	xb1 = requests.get('http://n9e5v4d8.ssl.hwcdn.net/repos/weeklyRivensXB1.json')
	ps4 = requests.get('http://n9e5v4d8.ssl.hwcdn.net/repos/weeklyRivensPS4.json')
	ns = requests.get('http://n9e5v4d8.ssl.hwcdn.net/repos/weeklyRivensSWI.json')
	
	pcDictList = json.loads(pc.text)
	xb1DictList = json.loads(xb1.text)
	ps4DictList = json.loads(ps4.text)
	nsDictList = json.loads(ns.text)
	
	global pcRivenData
	global xb1RivenData
	global ps4RivenData
	global nsRivenData
	
	pcRivenData = dict_list_to_object_list(pcDictList)
	xb1RivenData = dict_list_to_object_list(xb1DictList)
	ps4RivenData = dict_list_to_object_list(ps4DictList)
	nsRivenData = dict_list_to_object_list(nsDictList)
	
	if len(pcRivenData) == 0 or len(xb1RivenData) == 0 or len(ps4RivenData) == 0 or len(nsRivenData) == 0:
		print('Error occurred while getting Riven data! Restart the bot and try again!')
	
async def riven_refresh():
	while True:
		dt = datetime.utcnow()
		if dt.weekday() == 1 and dt.hour == 0 and dt.minute == 5:
			fetch_riven_data()
			print('New Riven data received!')
		else:
			await asyncio.sleep(60)

def dict_list_to_object_list(dictList):
        obList = list()
        for d in dictList:
                riven = Riven(d)
                obList.append(riven)

        return obList
	
def get_server_data():
	global serverPrefixes
	global serverPlatforms
	
	serverPrefixes = dict()
	serverPlatforms = dict()

	with open('serverPrefixes.csv', newline='') as csvfile:
		prefixReader = csv.reader(csvfile, delimiter=' ', quotechar='|')
		for row in prefixReader:
			entry = {row[0]: row[1]}
			serverPrefixes.update(entry)
	
	with open('serverPlatforms.csv', newline='') as csvfile:
		platformReader = csv.reader(csvfile, delimiter=' ', quotechar='|')
		for row in platformReader:
			entry = {row[0]: row[1]}
			serverPlatforms.update(entry)

def is_bot(message):
	return message.author == client.user or message.content.startswith('{0}'.format(serverPrefixes[message.server.id]))

client.run(TOKEN)
