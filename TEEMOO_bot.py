import discord
import requests
import json

client = discord.Client()
token = ''
API_KEY = ''


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


def parse_command(content):
    if not content.startswith('t!'):
        return None, None
    cmd, *arg = content.replace('t!', '').split(' ', 1)
    return cmd.lower(), arg[0] if arg else None


async def cmd_report(message, _):
    counter = 0
    tmp = await client.send_message(message.channel, 'Reporting in...')
    async for log in client.logs_from(message.channel, limit=100):
        if log.author == message.author:
            counter += 1

    await client.edit_message(tmp, 'You have {} messages.'.format(counter))

async def cmd_weather(message, city):
    tmp = await client.send_message(message.channel, "I'll scout ahead!")
    if not city:
        await client.edit_message(tmp, 'Please specify a city (or state)!')
        return
    link = 'http://api.openweathermap.org/data/2.5/weather?q=%s&APPID=%s' % (city, API_KEY)
    r = requests.get(link)
    data = json.loads(r.text)
    location = data['name']
    F = data['main']['temp'] * 1.8 - 459.67
    C = (F - 32) * 5/9
    status = data['weather'][0]['description']
    payload = '%s: %s \nTemperature is: %s°C  (%s°F) ' % (location, status, round(C), round(F))
    await client.edit_message(tmp, payload)

async def cmd_happy(message, _):
    with open('images/happy.jpg', 'rb') as teemo:
        await client.send_file(message.channel, teemo)

async def cmd_tilted(message, _):
    with open('images/tilted.png', 'rb') as teemo:
        await client.send_file(message.channel, teemo)

async def cmd_clear(message, limit):
    perms = message.channel.permissions_for(message.author)
    limit = int(limit) if limit else 50
    if perms.administrator:
        try:
            await client.purge_from(message.channel, limit=limit)
        except Exception:
            await client.send_message(message.channel, "Messages older than 14 days cannot be bulk deleted!")
    else:
        with open('images/deal_with_it.png', 'rb') as teemo:
            await client.send_file(message.channel, teemo)


commands = {
    'happy': cmd_happy,
    'report': cmd_report,
    'tilted': cmd_tilted,
    'weather': cmd_weather,
    'clear': cmd_clear,

}


@client.event
async def on_message(message):
    if message.author.bot:
        return

    cmd, arg = parse_command(message.content)
    if not cmd:
        return

    handler = commands.get(cmd)
    if handler:
        await handler(message, arg)




client.run(token)
