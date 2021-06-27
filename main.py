from discord_slash.context import ComponentContext
import tweepy, discord, json, asyncio, sys, datetime, copy, time, traceback
#unique_id = secrets.token_urlsafe(24)
from discord.ext.commands import command, Cog, Bot as Bot_cmd
from discord_slash import SlashCommand
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle
from libs import *
check_files()
from tokens import *
if not user or not DISCORD_TOKEN or not Access_Token or not Access_Token_Secret or not API_Key or not API_Secret_Key or not owner_id or not channel_id:
    print("Make sure to fill all the variables in tokens.py")
    time.sleep(3)
    sys.exit(0)
elif enable_auto_messages == True and not channel_id:
    print("Put channel id into tokens.py, and run again.")
    time.sleep(3)
    sys.exit(0)
if 0 in guild_ids:
    print("Your slash command will be global!")
    guild_ids = None
client = Bot_cmd(command_prefix = ".", intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True, sync_on_cog_reload=True)
auth = tweepy.OAuthHandler(API_Key, API_Secret_Key)
auth.set_access_token(Access_Token, Access_Token_Secret)
api = tweepy.API(auth)
global tweets, pings
tweets, pings = import_twt_db()
commands = []
@slash.slash(name="menu", guild_ids=guild_ids, description="Open the Interactive GUI.")
async def menu(ctx):
    _ = message(ctx, tweets, pings)
    commands.append(_)
    await _.refresh(ctx)


@client.event
async def on_component(ComponentContext):
    temp_id = ComponentContext.component_id
    for i in commands:
        for _ in i.buttons:
            if temp_id == _["custom_id"]:
                valid_ui = i
                valid_button = _
                if valid_button["label"] == "Newest Tweet":
                    await valid_ui.next_page(ComponentContext)
                elif valid_button["label"] == "Next":
                    await valid_ui.next_page(ComponentContext)
                elif valid_button["label"] == "Menu":
                    await valid_ui.menu(ComponentContext)
                elif valid_button["label"] == "Previous":
                    await valid_ui.prev_page(ComponentContext)
                elif valid_button["label"] == "Add/Remove from Ping List":
                    await valid_ui.change_pings(ComponentContext, pings)
                elif valid_button["label"] == "Enable pings":
                    if ComponentContext.author_id not in pings["a"]:
                        pings["a"].append(ComponentContext.author_id)
                        write(pings, "pings")
                    await valid_ui.change_pings(ComponentContext, pings)
                elif valid_button["label"] == "Disable pings":
                    if ComponentContext.author_id in pings["a"]:
                        pings["a"].remove(ComponentContext.author_id)
                        write(pings, "pings")
                    await valid_ui.change_pings(ComponentContext, pings)
                break

async def update():
    global tweets, pings
    while True:
        temp_tweets = copy.deepcopy(tweets)
        if temp_tweets == {}:
            temp_tweets = {"Placeholder":{"id":"placeholder"}}
        timeline = api.user_timeline(user, tweet_mode="extended")
        timeline.reverse()
        for tweet in timeline:
            date_unix = int(round(datetime.datetime.timestamp(tweet.created_at)))
            if date_unix not in tweets:
                media_jpg = None
                rt_full_text, rts, hearts = ["" for i in range(3)]
                try:
                    try:
                        rtd = tweet._json["retweeted_status"]
                        rtd = True
                        rtd_author = tweet._json["retweeted_status"]["user"]["name"]
                        rtd_scr_author = tweet._json["retweeted_status"]["user"]["screen_name"]
                    except:
                        rtd = False
                        rtd_author = None
                        rtd_scr_author = None
                    try:
                        rt_full_text = tweet._json["retweeted_status"]["full_text"]
                    except KeyError:
                        #traceback.print_exc()
                        rt_full_text = tweet.full_text
                    try:
                        rts = tweet._json["retweeted_status"]["retweet_count"]
                    except KeyError:
                        rts = tweet._json["retweet_count"]
                    try:
                        hearts = tweet._json["retweeted_status"]["favorite_count"]
                    except KeyError:
                        hearts = tweet._json["favorite_count"]
                    tweet._json["entities"]["media"][0]["media_url_https"]
                    media_jpg = tweet._json["entities"]["media"][0]["media_url_https"]
                except Exception:
                    pass
                    #traceback.print_exc()
                _ = {date_unix:{"title":rt_full_text, "media_jpg":media_jpg, "tweeter":tweet.user.name, "tweeter2": tweet.user.screen_name, "rts": rts, "hearts": hearts, "rtd": rtd, "rtd_user": rtd_author, "rtd_scr": rtd_scr_author, "id": tweet.id}}
                tweets = {**_, **tweets}
                #print(tweets)
        write(tweets, "tweets")
        if enable_auto_messages:
            print(tweets[list(tweets)[0]]["id"])
            print(temp_tweets[list(temp_tweets)[0]]["id"])
            if tweets[list(tweets)[0]]["id"] != temp_tweets[list(temp_tweets)[0]]["id"]:
                _channel = client.get_channel(channel_id)
                twt = tweets[list(tweets)[0]]
                embed=discord.Embed(description="%s" % twt["title"])
                if twt["rtd"]:
                    embed.set_author(name="%s (%s) retweeted %s (%s)" % (twt["tweeter"], twt["tweeter2"], twt["rtd_user"], twt["rtd_scr"]), url="https://twitter.com/%s/status/%s" % (twt["tweeter2"], twt["id"]))
                else:    
                    embed.set_author(name="%s (%s)" % (twt["tweeter"], twt["tweeter2"]), url="https://twitter.com/%s/status/%s" % (twt["tweeter2"], twt["id"]))
                if twt["media_jpg"] != None:
                    embed.set_image(url=twt["media_jpg"])
                embed.add_field(name="Retweets", value=twt["rts"], inline=True)
                embed.add_field(name="Hearts", value=twt["hearts"], inline=True)
                embed.set_footer(text="Tweeted @ %s. https://github.com/heyngra/twitter-discord-bot)" % datetime.datetime.fromtimestamp(float(list(tweets)[0])).strftime('%Y-%m-%d %H:%M:%S'))
                ping_txt = ""
                for i in pings["a"]:
                    ping_txt += "<@%s> " % i
                await _channel.send(content=ping_txt, embed=embed)
        await asyncio.sleep(60)
@client.event
async def on_ready():
    print("Running at account: %s" % client.user)
    client.loop.create_task(update())
client.run(DISCORD_TOKEN)
