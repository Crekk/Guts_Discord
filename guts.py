import discord # type: ignore
from discord.ext import commands # type: ignore
import asyncio
import random
import json
import time
import requests
import re

# ------------------ CUSTOMIZABLE BOT SETTINGS ------------------

# url of the local message server
url = "http://127.0.0.1:8080/send_message"

BOT_NAME = "Guts" # used for stripping "Guts: " prefix

trigger_words = [
    'guts', 'hornet', 'heracross', 'captain hot', 'evil morty', 'question of the day', 
    'qotd', 'society livers', 'tower of rebirth', 'jailer', 'peakland', 'rhinor', 
    'fire castle', 'creeper', 'gamers', 'hot gun', 'dranoel', 'big gutsus', 'chungling', 'big chungus', 'berserk 2', 'impostor', 
    'pinsir', 'focus sash', 'burning village', 'impostor', 'society',
    'fire capitol', 'police brutality', 'burned village', 'chungus', 'colossal titans', 'berserk'
]
USERNAME_MAP = {
    'crekkers': 'Crek',
    'pochitaman': 'Pochita Man',
    'wiwern': 'Crustle',
}
CMD_PREFIX = ','  # command prefix for the bot
RESTART_MSG = "I'm feeling like a brand new person... Something within me feels fresh..." #,restart command message

odds = 250  # 1 in odds chance of responding to a message
react_odds = 1000 # 1 in react_odds chance of reacting to a message
max_history = 3  # number of previous messages to include
inactivity_timer = 15 * 60 # resets message history after this many minutes of inactivity

typing_max = 5.0 # 5s max
typing_perchar = 0.03 # 0.03s per character

wall_enabled = True  # enable wall command
wall_url = "https://i.imgur.com/rY19O49.png" # URL for the wall image
wall_count_min = 4  # minimum number of wall images to send
wall_count_max = 9  # maximum number of wall images to send

# ------------------ END CUSTOMIZABLE SETTINGS ------------------

# load tokens from json
try:
    with open('token.json') as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Failed to load token file: {e}")
    exit(1)

DISCORD_TOKEN = config['DISCORD_TOKEN']

# initialize the bot
intents = discord.Intents.default()
intents.message_content = True  # enable reading messages
bot = commands.Bot(command_prefix=CMD_PREFIX, intents=intents)


# start new session, ai side
async def start_ai_chat():
    retry_count = 0
    while True:
        try:
            response = requests.post(url, json={'user_input': "start conversation"})
            if response.status_code == 200:
                return response.json().get('response', ''), None
            else:
                print(f"Error: Received status code {response.status_code}")
        except Exception as e:
            print(f"Exception occurred: {e}")

        retry_count += 1
        if retry_count <= 12:
            wait_time = 10  # retry every 10 seconds for first 12 tries
        else:
            wait_time = 3600  # retry every hour after that

        print(f"Retrying in {wait_time} seconds... (Attempt #{retry_count})")
        await asyncio.sleep(wait_time)

# start new session, discord side
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    bot.ai_chat, bot.chat_id = await start_ai_chat()
    bot.message_history = []  # start message history
    bot.last_activity = time.time() # start last message activity
    bot.loop.create_task(inactivity_reset())  # Start the inactivity timer task

async def send_to_guts(message, bot, max_history, url):
    # Get the last max_history messages from message history
    context = '\n'.join(bot.message_history[-max_history * 2:])  # include recent 2 * max_history messages
    print(f"Sending to {BOT_NAME} with context:\n{context}")
    print(f"Triggered by message: {message.content.lower()}")
    
    try:
        # Prepare the data to send
        data = {'user_input': context}  # Use a structured payload like in chat_with_guts
        
        print(f"Sending data to {BOT_NAME}: {data}")

        # Send the request to guts
        response = requests.post(url, json=data)
        
        # Debugging: Check response status and content
        print(f"API Response Status: {response.status_code}")
        print(f"API Response Text: {response.text}")

        if response.status_code == 200:
            ai_message = response.json().get('response', '')
            print(f"Received response from {BOT_NAME}: {ai_message}")
        else:
            raise Exception(f"Failed to get a valid response from server, status code: {response.status_code}")

        # Remove prefix if it exists
        prefix = f"{BOT_NAME}:"
        if ai_message.lower().startswith(prefix.lower()):
            processed_text = ai_message[len(prefix):].lstrip()
        else:
            processed_text = ai_message.strip()

        # Clear the history after sending the response
        bot.message_history = []  # Clear history after processing the message

        # Calculate delay based on message length (e.g. 0.05s per character, max 5 seconds)
        typing_delay = min(len(processed_text) * typing_perchar, typing_max)

        # Show the typing indicator
        typing_task = bot.loop.create_task(message.channel.trigger_typing())
        await asyncio.sleep(typing_delay)
        if not typing_task.done():
            typing_task.cancel()
        await message.channel.send(processed_text)

    except Exception as e:
        print(f"Error during sending/receiving message: {e}")
        await message.channel.send("An error occurred while processing your message.")


# Inactivity timer
async def inactivity_reset():
    while True:
        await asyncio.sleep(60)  # check every minute
        elapsed = time.time() - bot.last_activity
        if elapsed >= inactivity_timer and bot.message_history:
            bot.message_history.clear()
            print("Message history cleared due to inactivity.")


@bot.command()
async def restart(ctx):
    """start a new chat on the server"""
    print(f"Restarting chat session with {BOT_NAME}...")
    
    # Send a reset command to the server or just restart by sending "start conversation" again
    response = requests.post(url, json={'user_input': "NEW_CHAT_123456789"})
    
    if response.status_code == 200:
        async with ctx.channel.typing():
            await asyncio.sleep(0.5)  # Simulate the bot "typing"
            await ctx.send(RESTART_MSG)
    else:
        await ctx.send("Sorry, I couldn't restart the chat session.")


# command to display all trigger words 
@bot.command()
async def triggers(ctx):
    """Displays all the trigger words"""
    trigger_list = ', '.join(trigger_words)
    await ctx.send(f"Current trigger words: {trigger_list}")

# command to change odds
@bot.command()
async def changeodds(ctx, new_odds: int = None):
    """Change the odds of responding to a message"""
    global odds  # Referencing the global odds variable
    if new_odds is None:
        await ctx.send(f"The current odds are 1 in {odds}")
    else:
        odds = new_odds
        await ctx.send(f"Changed odds to 1 in {odds}")

# command to change history
@bot.command()
async def changehistory(ctx, new_max_history: int = None):
    """Change the number of messages to include in context"""
    global max_history  # Referencing the global odds variable
    if new_max_history is None:
        await ctx.send(f"The current messages included are {max_history+1}")
    else:
        max_history = new_max_history
        await ctx.send(f"Changed the number of messages to include to {max_history+1}")

# wall command
if wall_enabled:
    print("Wall command is enabled")
    @bot.command()
    async def wall(ctx):
        """Create a wall"""
        rand_wallcount = random.randint(wall_count_min, wall_count_max)
        for i in range(rand_wallcount):
            rand_walldelay = random.randint(1,500)/1000
            await ctx.send(wall_url)
            await asyncio.sleep(rand_walldelay)
else:
    print("Wall command is disabled")


# read messages
@bot.event
async def on_message(message):
    
    # set last activity
    bot.last_activity = time.time()

    # if bot is the author, ignore
    if message.author == bot.user:
        return

    # ignore empty messages
    if not message.content and not message.embeds:
        print(f"Received empty message from {message.author}")
        return
    
    # regular text messages
    if message.content:
        name = USERNAME_MAP.get(message.author.name, str(message.author))
        bot.message_history.append(f"{name}: {message.content}")

    # embeds
    embed_texts = []
    if message.embeds:
        # If the message contains embeds, extract the title and description
        for embed in message.embeds:
            embed_text = f"**{embed.title}**\n{embed.description}" if embed.title else embed.description
            # Print the embed content for debugging
            print(f"Received embed from {message.author}: {embed_text}")
            # Only append to history if embed has content
            if embed_text.strip():  # Ensure there is actual text to process
                bot.message_history.append(f"{message.author}: {embed_text}")
                embed_texts.append(embed_text)

    # keep only the last "max_history" messages
    if len(bot.message_history) > max_history * 2:
        bot.message_history.pop(0)  # remove the oldest message

    # guts triggers
    message_content = message.content.lower()
    embed_content = ' '.join(embed_texts).lower()
    
    # check if bot is mentioned in message
    if bot.user in message.mentions:
        await send_to_guts(message, bot, max_history, url)
    
    # check trigger words
    elif any(re.search(rf'\b{re.escape(word)}\b', message_content) for word in trigger_words) or any(re.search(rf'\b{re.escape(word)}\b', embed_content) for word in trigger_words):
        await send_to_guts(message, bot, max_history, url)

    # try random odds
    elif random.randint(1, odds) == 1:
        await send_to_guts(message, bot, max_history, url)

    # check if the message is a reply to a previous message
    elif message.reference:
        original_message = await message.channel.fetch_message(message.reference.message_id)
        
        # Trigger the response if the original message was from the bot (e.g., "Guts" message)
        if original_message.author == bot.user:
            await send_to_guts(message, bot, max_history, url)

    # Ensure the bot processes commands after custom message logic
    await bot.process_commands(message)

# run the bot
bot.run(DISCORD_TOKEN)