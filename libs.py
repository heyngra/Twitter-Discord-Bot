import os, json, asyncio, discord, json, datetime
#from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType
from discord.ext.commands import command, Cog, Bot as Bot_cmd
from discord_slash.context import ComponentContext
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle
from discord_slash import SlashCommand




def check_files():
    if not os.path.isfile("tweets.json"):
        f = open("tweets.json","w+")
        f.write("""
        {}
        """)
        f.close()
        print("tweets.json created")
    if not os.path.isfile("pings.json"):
        f = open("pings.json","w+")
        f.write("""{"a": []}""")
        f.close()
        print("pings.json created")
    if not os.path.isfile("tokens.py"):
        f = open("tokens.py", "w+")
        f.write(
"""#Paste all of your tokens here

DISCORD_TOKEN = "" #Discord bot token"

#Twitter bot tokens
Access_Token = ""
Access_Token_Secret = ""

API_Key = ""
API_Secret_Key = ""

user = "" #User to pull tweets from
owner_id = "" #Your discord ID
enable_auto_messages = True #Bot will ping all people in list with new tweets if enabled.
channel_id = 0 #Only matters when setting above is enabled: Channel, where notifications should be sent.
guild_ids = [0] #Put here your server id. If you want to make command global, leave it as 0. IMPORTANT: Global Commands synchronize for 1 hour.
""")
        f.close()
        print("tokens.py created")

def write(dict_, filename):
    f = open("%s.json" % filename, "w")
    json.dump(dict(dict_), f)
    f.close()

def import_twt_db():
    file = open("tweets.json", "r")
    _ = json.load(file)
    file.close()
    file = open("pings.json", "r")
    __ = json.load(file)
    file.close()
    return(_, __)
    
class message:
    def __init__(self, ctx, tweets, pings):
        self.page = 0
        self.ctx = ctx
        self.buttons = []
        self.tweets = tweets
        self.pings = pings
        self.keys = list(self.tweets)
        self.sent = False
    async def refresh(self, ctx, **kwargs):
        if self.page == 0:
            self.buttons = [
                manage_components.create_button(
                style=ButtonStyle.blue,
                label="Newest Tweet"
                ),
                manage_components.create_button(
                style=ButtonStyle.red,
                label="Add/Remove from Ping List"
                ),
            ]
            self.action_row1 = manage_components.create_actionrow(*self.buttons)
            _ = discord.Embed(title="Please click one of the buttons below to go forward.")
            if not self.sent:
                await ctx.send(embed = _, components=[self.action_row1], hidden=True)
                self.sent = True
            else:
                await ctx.edit_origin(embed = _, components=[self.action_row1], hidden=True)
        elif self.page == -1:
            self.buttons = [
                manage_components.create_button(
                    style=ButtonStyle.red,
                    label="Menu"
                ),
            ]
            if ctx.author_id in kwargs["pings"]["a"]:
                self.buttons.append(
                    manage_components.create_button(
                        style=ButtonStyle.red,
                        label="Disable pings"
                    )
                )
            else:
                self.buttons.append(
                    manage_components.create_button(
                        style=ButtonStyle.green,
                        label="Enable pings"
                    )
                )
            embed = discord.Embed(title="Enable or Disable your pings here.")
            self.action_row1 = manage_components.create_actionrow(*self.buttons)
            await ctx.edit_origin(embed=embed, components=[self.action_row1], hidden=True)
        elif self.page >= 1:
            _ = self.page - 1
            __ = len(self.tweets) - self.page
            if __ < 0: __ = 0
            self.buttons = [
                manage_components.create_button(
                    style=ButtonStyle.red,
                    label="Menu"
                ),
                manage_components.create_button(
                    style=ButtonStyle.blue,
                    label="Previous",
                    disabled= not bool(_)
                ),
                manage_components.create_button(
                    style=ButtonStyle.blue,
                    label="Next",
                    disabled=not bool(__)
                ),
            ]
            twt = self.tweets[self.keys[self.page - 1]]
            embed=discord.Embed(description="%s" % twt["title"])
            if twt["rtd"]:
                embed.set_author(name="%s (%s) retweeted %s (%s)" % (twt["tweeter"], twt["tweeter2"], twt["rtd_user"], twt["rtd_scr"]), url="https://twitter.com/%s/status/%s" % (twt["tweeter2"], twt["id"]))
            else:    
                embed.set_author(name="%s (%s)" % (twt["tweeter"], twt["tweeter2"]), url="https://twitter.com/%s/status/%s" % (twt["tweeter2"], twt["id"]))
            if twt["media_jpg"] != None:
                embed.set_image(url=twt["media_jpg"])
            embed.add_field(name="Retweets", value=twt["rts"], inline=True)
            embed.add_field(name="Hearts", value=twt["hearts"], inline=True)
            embed.set_footer(text="Tweeted @ %s. https://github.com/heyngra/twitter-discord-bot)" % datetime.datetime.fromtimestamp(float(list(self.tweets)[self.page - 1])).strftime('%Y-%m-%d %H:%M:%S'))
            self.action_row1 = manage_components.create_actionrow(*self.buttons)
            await ctx.edit_origin(embed=embed, components=[self.action_row1], hidden=True)
    async def next_page(self, ctx):
        self.page += 1
        await self.refresh(ctx)
    async def prev_page(self, ctx):
        self.page -= 1
        await self.refresh(ctx)
    async def menu(self, ctx):
        self.page = 0
        await self.refresh(ctx)
    async def change_pings(self, ctx, pings):
        self.page = -1
        await self.refresh(ctx, pings=pings)