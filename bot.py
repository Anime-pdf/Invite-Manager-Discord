import discord
from discord.ext import commands
import asyncio
import datetime
import json
import os
import sqlite3
from discord.utils import get

client = commands.Bot( command_prefix = '%')
cfg = open("config.json", "r")
tmpconfig = cfg.read()
cfg.close()
config = json.loads(tmpconfig)

connection = sqlite3.connect('server.db')
cursor = connection.cursor() 
client.remove_command('help')

token = config["token"]
guild_id = config["server-id"]
logs_channel = config["logs-channel-id"]


invites = {}
last = ""

async def fetch():
 global last
 global invites
 await client.wait_until_ready()
 gld = client.get_guild(int(guild_id))
 logs = client.get_channel(int(logs_channel))
 while True:
  invs = await gld.invites()
  tmp = []
  for i in invs:
   for s in invites:
    if s[0] == i.code:
     if int(i.uses) > s[1]:
      usr = gld.get_member(int(last))
      eme = discord.Embed(description = "Just joined the server", color = 0x03d692, title = " ")
      eme.set_author(name = usr.name + "#" + usr.discriminator, icon_url = usr.avatar_url)
      eme.set_footer(text = "ID: " + str(usr.id))
      eme.timestamp = usr.joined_at
      eme.add_field(name = "Used invite", value = "Inviter: " + i.inviter.mention + " (`" + i.inviter.name + "#" + i.inviter.discriminator + "`)\nCode: `" + i.code + "`\nUses: `" + str(i.uses) + "`", inline = False)
      await logs.send(embed = eme)
   tmp.append(tuple((i.code, i.uses)))
  invites = tmp
  await asyncio.sleep(4)


@client.event
async def on_ready():
    print("ready!")
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        name TEXT,
        id TEXT,
        invites INT,
        points BIGINT
    ) """)
    for guild in client.guilds:
        for member in guild.members:
            if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
                cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0)")
                connection.commit()
    await client.change_presence(activity = discord.Activity(name = "joins", type = 2))


@client.event
async def on_member_join(member):
    global last
    last = str(member.id)
    if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
        cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0)")
        connection.commit()
    else:
        pass

@client.command(aliases = ['invites', 'inv'])
async def __invites(ctx, member: discord.Member = None):
  if member is None:
    await ctx.send(embed = discord.Embed(
      description = f"""**{ctx.author}** have **{cursor.execute("SELECT invites FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}** invites""",colour = discord.Color.dark_gold()
      ))
  else:
    await ctx.send(embed = discord.Embed(
      description = f"""**{member}** have **{cursor.execute("SELECT invites FROM users WHERE id = {}".format(member.id)).fetchone()[0]}** invites""",colour = discord.Color.dark_gold()
      ))

client.loop.create_task(fetch())
client.run(token)
