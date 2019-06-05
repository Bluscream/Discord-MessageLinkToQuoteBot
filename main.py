import discord
from re import findall
from re import MULTILINE as REGEX_MULTILINE
from config import discord_bot_token

regex_messagelink = r"(https:\/\/(?:\S+.)?discordapp.com\/channels\/(\d{16,21})\/(\d{16,21})\/(\d{16,21}))"

class MessageLink(object):
    Guild = None; Channel = None; Message = None
    def __init__(self, guild, channel, message):
        self.Guild = int(guild); self.Channel = int(channel); self.Message = int(message)

class MyClient(discord.Client):
    async def on_ready(self): print('Logged on as', self.user)
    async def on_message(self, message: discord.Message):
        if message.author == self.user: return
        if message.channel.guild is None: return
        if message.channel.guild.id == 336642139381301249 and message.channel.id != 448285120634421278: return
        if not message.channel.guild.me.permissions_in(message.channel).embed_links: return
        matches = findall(regex_messagelink, message.content, REGEX_MULTILINE)
        if len(matches) < 1: return
        for match in matches:
            if len(match) < 4: continue
            url = MessageLink(match[1], match[2], match[3])
            print("Found message link:")
            print("\tMatch:", match)
            print("\tLink:", match[0])
            print("\tGuild ID:", url.Guild)
            print("\tChannel ID:", url.Channel)
            print("\tMessage ID:", url.Message)
            guild = self.get_guild(url.Guild)
            if guild is None: print("ERROR: Could not find guild!"); return
            channel = guild.get_channel(url.Channel)
            if channel is None: print("ERROR: Could not find channel!"); return
            # msg = discord.Message
            try:
                msg = await channel.fetch_message(url.Message)
                if msg is None: print("ERROR: Could not find message!"); return
            except: print("FATAL: Could not find message!"); return
            # msg = await self.get_guild(url.Guild).get_channel(url.Channel).fetch_message(url.Message)
            print(msg)
            if len(msg.embeds) > 0: print("ERROR: Message is embed!"); return
            if msg.author.bot: print("ERROR: Message author is bot!"); return
            header = ""
            try:
                await message.delete()
                header = match[0]
            except: pass
            em = discord.Embed()
            em.set_author(name=msg.author.name, icon_url=msg.author.avatar_url)
            em.description = msg.content
            em.set_footer(text="Quoted by \"{}\" ({})".format(message.author, message.author.id), icon_url=message.author.avatar_url)
            em.timestamp = msg.edited_at if msg.edited_at else msg.created_at
            print(em)
            await message.channel.send(embed=em, content=header if header else "")

client = MyClient()
client.run(discord_bot_token)