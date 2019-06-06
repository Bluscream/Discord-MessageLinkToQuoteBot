import discord, re
from config import discord_bot_token, admins

regex_discordid = re.compile(r"(\d{16,21})")
regex_messagelink = r"(https:\/\/(?:\S+.)?discordapp.com\/channels\/(\d{16,21})\/(\d{16,21})\/(\d{16,21}))"

class MessageLink(object):
    Guild = None; Channel = None; Message = None
    def __init__(self, guild, channel, message):
        self.Guild = int(guild); self.Channel = int(channel); self.Message = int(message)

class MyClient(discord.Client):
    own_prefix = "<@{0}>"
    async def on_ready(self):
        print('Logged on as', self.user)
        self.own_prefix = self.own_prefix.format(self.user.id)
    async def on_message(self, message: discord.Message):
        if message.author == self.user: return
        if message.author.bot: return
        if message.content.startswith(self.own_prefix):
            command = message.content.split(" ")[1:]
            origin = "#" + message.channel.name if message.guild is None else ("{}:#{}".format(message.guild.name, message.channel.name))
            print("Got command in", origin, "from", message.author, ":", command)
            if command[0] == "invite": await message.channel.send(content=f"{message.author.mention} Invite me to your server: <https://discordapp.com/api/oauth2/authorize?client_id=585621762650406952&permissions=93184&scope=bot>")
            return
        if message.guild is None: return
        # if message.guild.id == 336642139381301249 and message.channel.id != 448285120634421278: return
        if not message.guild.me.permissions_in(message.channel).embed_links: return
        if message.content.isdigit():
            if not regex_discordid.match(message.content): return
            header = f"https://discordapp.com/channels/{message.guild.id}/{message.channel.id}/{message.content}"
            await self.quote_message_from_channel(message, message.channel, message.content, header)
            return
        matches = re.findall(regex_messagelink, message.content, re.MULTILINE)
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
            await self.quote_message_from_channel(message, channel, url.Message, match[0])

    async def quote_message_from_channel(self, message : discord.Message, channel : discord.TextChannel, msgid : int, header = ""):
            try:
                msg = await channel.fetch_message(msgid)
                if msg is None: print("ERROR: Could not find message!"); return
            except: print("FATAL: Could not find message!"); return
            # msg = await self.get_guild(url.Guild).get_channel(url.Channel).fetch_message(url.Message)
            if not message.author.id in admins:
                if len(msg.embeds) > 0: print("ERROR: Message is embed!"); return
                if msg.author.bot: print("ERROR: Message author is bot!"); return
            can_delete = message.guild.me.permissions_in(message.channel).manage_messages
            if can_delete: await message.delete()
            em = discord.Embed()
            origin = "#" + msg.channel.name if message.guild == msg.guild else ("{}:#{}".format(msg.guild.name, msg.channel.name))
            # em.set_author(name="\"{}\" ({}) said in {}".format(msg.author, msg.author.id, origin), icon_url=msg.author.avatar_url)
            em.set_author(name="{} said in {}".format(msg.author.display_name, origin), icon_url=msg.author.avatar_url)
            em.description = msg.content
            # em.set_footer(text="Quoted by \"{}\" ({})".format(message.author, message.author.id), icon_url=message.author.avatar_url)
            em.set_footer(text="Quoted by {}".format(message.author.display_name), icon_url=message.author.avatar_url)
            em.timestamp = msg.edited_at if msg.edited_at else msg.created_at
            em.colour = msg.author.color
            print("Sending Embed:", em)
            await message.channel.send(embed=em, content=header if can_delete else "")

client = MyClient()
client.run(discord_bot_token)