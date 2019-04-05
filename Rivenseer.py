import discord
import json
import requests
import time
from datetime import datetime

TOKEN = 'NTYyMzg4ODk5MzY0NzMyOTMw.XKKRag.ILc62i-5kgTejgDQV9dYS4Ss2W4'

client = discord.Client()

prefix = '.'
defaultPlatform = 'pc'

pcRivenData = list()
xb1RivenData = list()
ps4RivenData = list()
nsRivenData = list()

@client.event
async def on_message(message):
	global defaultPlatform

	if message.author == client.user:
		return
	
	# Prefix change ---------
	global prefix
	if message.content.startswith('{0}prefix'.format(prefix)):
		if message.author.server_permissions.manage_server:
			cmd = message.content.split(" ")
			prefix = cmd[1]
			msg = 'My prefix is now \"{0}\"! Use that to summon me!'.format(prefix)
			await client.send_message(message.channel, msg)
		else:
			await client.send_message(message.channel, 'You do not have permission to change the prefix!')
		
	# Message cleaner -------
	elif message.content.startswith('{0}clean'.format(prefix)):
		deletedList = await client.purge_from(message.channel, check=is_bot)
		await client.send_message(message.channel, 'Deleted {0} message(s)'.format(len(deletedList)))
		
	# Riven search ----------	
	elif message.content.startswith('{0}riven'.format(prefix)):
		queryString = message.content.replace('{0}riven '.format(prefix), '', 1)
		query = queryString.split(", ")
		
		riven = query[0].upper()
		
		platform = ''
		
		if len(query) == 1:
			platform = defaultPlatform
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
				await client.send_message(message.channel, 'Platform not recognized. Use `{0}help platform` for a list of valid platforms!')
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
		
		foundRiven = False
		
		print('Search List: {0}'.format(len(searchList)))
		
		for r in searchList:
			if riven.strip() == r.compatibility:
				foundRiven = True
				
				if r.rerolled == False:
					rivenEmbed.add_field(name='UNROLLED RIVEN DATA\n----------------------------------------', value='**Average Price:** {0}\n**Standard Deviation:** {1}\n**Minimum Price:** {2}\n**Maximum Price:** {3}\n**Riven Popularity:** {4}\n\n'.format(r.avg, r.stddev, r.min, r.max, r.pop), inline=False)
				
				elif r.rerolled == True:
					rivenEmbed.add_field(name='ROLLED RIVEN DATA\n----------------------------------------', value='**Average Price:** {0}\n**Standard Deviation:** {1}\n**Minimum Price:** {2}\n**Maximum Price:** {3}\n**Riven Popularity:** {4}'.format(r.avg, r.stddev, r.min, r.max, r.pop), inline=False)
					
		if foundRiven == True:
			await client.send_message(message.channel, embed=rivenEmbed)
				
		else:
			await client.send_message(message.channel, 'No Riven was found. Try again!')
	
	# Help prompt -----------------
	elif message.content.startswith('{0}help'.format(prefix)):
		help = message.content.split()
		em = discord.Embed()
		em.title = 'Rivenseer'
		em.colour = 0xF7BF25
		
		if len(help) == 1:
			em.description = 'Hello! I am a bot designed to fetch Warframe Riven Data (provided by the developers) and make it available here in Discord!\nCurrently, my prefix is `{0}`\nIf you would like more info on a command, type `{1}help <command>`!'.format(prefix, prefix)
			em.add_field(name='COMMANDS', value='`help` - displays this prompt\n`riven` - gets current Riven data on a weapon\n`platform` - sets the default platform used by the riven command\n`clean` - removes some (if not all) of messages produced by me\n`prefix` - changes the prefix used to summon me', inline=False)
			await client.send_message(message.channel, embed=em)
		else:
			if help[1] == 'help':
				em.description = '`help` - displays the generic help prompt\n`help <command>` - displays more info about the given command'
				await client.send_message(message.channel, embed=em)
			elif help[1] == 'riven':
				em.description = '`riven <weapon>, [platform]` - gets Riven data for that weapon (unrolled rivens and rolled rivens).\n\n**NOTE:** Variant types (Prime, Prisma, Wraith, Vaykor, etc.) should not be included in the weapon name __(with the exception of Euphona Prime, Dakra Prime, and Reaper Prime)__. Sword and Shield weapons must include spaces and the ampersand:\n(Ack & Brunt, Sigma & Octantis, etc.)\n\nThe platform argument is optional, but you can use it to override the default platform setting. If it is omitted, this command will return the Riven data for the default platform (currently {0}).\n\nAll data is actual trade data and not taken from trade chat.\n\n**Examples of valid queries:**\n`{1}riven Lato`, `{2}riven cobra & crane, ns`, `{3}riven REAPER PRIME, xb1`'.format(defaultPlatform.upper(), prefix, prefix, prefix)
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
	elif message.content.startswith('{0}platform'.format(prefix)):
		platform = message.content.replace('{0}platform '.format(prefix), '')
		
		if message.author.server_permissions.manage_server == True:
			if platform.lower() == 'pc':
				defaultPlatform = 'pc'
				await client.send_message(message.channel, 'Default platform changed to PC!')
			elif platform.lower() == 'xb1':
				defaultPlatform = 'xb1'
				await client.send_message(message.channel, 'Default platform changed to XBox One!')
			elif platform.lower() == 'ps4':
				defaultPlatform = 'ps4'
				await client.send_message(message.channel, 'Default platform changed to PlayStation 4!')
			elif platform.lower() == 'ns':
				defaultPlatform = 'ns'
				await client.send_message(message.channel, 'Default platform changed to Nintendo Switch!')
			else:
				await client.send_message(message.channel, 'Platform not recognized. Use `{0}help platform` for more info!'.format(prefix))
		else:
			await client.send_message('You do not have permission to change the default platform!')
				
	elif message.content.startswith('{0}'.format(prefix)):
		await client.send_message(message.channel, 'Command not recognized. Use the `help` command to see a list of my commands!')
		
@client.event
async def on_ready():

	await fetch_riven_data()

	prefix = '.'
	
	riven_refresh()
	
	print('Bot initiated.')

# --------------------------------------------------------------


class Riven:
	def __init__(self, d):
		self.__dict__ = d
		

# --------------------------------------------------------------

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
	
	print('PC: {0}'.format(len(pcRivenData)))
	print('XB1: {0}'.format(len(xb1RivenData)))
	print('PS4: {0}'.format(len(ps4RivenData)))
	print('NS: {0}'.format(len(nsRivenData)))
	
async def riven_refresh():
	dt = datetime.utcnow()
	
	while True:
		if dt.weekday() == 0 and dt.hour == 0 and dt.minute == 5:
			fetch_riven_data()
		else:
			time.sleep(60)

def dict_list_to_object_list(dictList):
        obList = list()
        for d in dictList:
                riven = Riven(d)
                obList.append(riven)

        return obList

def is_bot(message):
	return message.author == client.user

client.run(TOKEN)