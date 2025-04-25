import discord # type: ignore
from discord.ext import commands # type: ignore
import asyncio
import random
import json
import time
import requests

# url of the local message server
url = "http://127.0.0.1:8080/send_message"

# CUSTOMIZABLE VARIABLES
trigger_words = [
    'guts', 'hornet', 'heracross', 'captain hot', 'evil morty', 'question of the day', 
    'qotd', 'society livers', 'tower of rebirth', 'jailer', 'peakland', 'rhinor', 
    'fire castle', 'creeper', 'gamers', 'hot gun', 'dranoel', 'big gutsus', 'chungling', 'big chungus', 'berserk 2', 'impostor', 
    'pinsir', 'focus sash', 'burning village', 'impostor', 'society',
    'fire capitol', 'police brutality', 'burned village', 'chungus', 'colossal titans', 'berserk'
]
odds = 250  # 1 in odds chance of responding to a message
max_history = 3  # number of previous messages to include
inactivity_timer = 15 * 60 # resets message history after this many minutes of inactivity

# load tokens from json
with open('token.json') as f:
    config = json.load(f)

DISCORD_TOKEN = config['DISCORD_TOKEN']
AZURE_TOKEN = config['AZURE_TOKEN']

# initialize the bot
intents = discord.Intents.default()
intents.message_content = True  # enable reading messages
bot = commands.Bot(command_prefix=",", intents=intents)


# start new session, ai side
async def start_ai_chat():
    # Make an initial request to your 'guts_llm.py' server to start the conversation
    response = requests.post('http://127.0.0.1:8080/send_message', json={'user_input': "start conversation"})
    
    if response.status_code == 200:
        return response.json().get('response', ''), None
    else:
        return "Error: Could not start conversation.", None

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
    print(f"Sending to Guts with context:\n{context}")
    print(f"Triggered by message: {message.content.lower()}")
    
    try:
        # Prepare the data to send
        data = {'user_input': context}  # Use a structured payload like in chat_with_guts
        
        print(f"Sending data to Guts: {data}")

        # Send the request to guts
        response = requests.post(url, json=data)
        
        # Debugging: Check response status and content
        print(f"API Response Status: {response.status_code}")
        print(f"API Response Text: {response.text}")

        if response.status_code == 200:
            ai_message = response.json().get('response', '')
            print(f"Received response from Guts: {ai_message}")
        else:
            raise Exception(f"Failed to get a valid response from server, status code: {response.status_code}")

        # Remove "Guts:" prefix if it exists
        if ai_message.startswith('Guts:'):
            processed_text = ai_message[6:].strip()
        else:
            processed_text = ai_message.strip() 


        # Clear the history after sending the response
        bot.message_history = []  # Clear history after processing the message

        # Send the response to Discord
        await message.channel.send(ai_message)

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
    print("Restarting chat session with Guts...")
    
    # Send a reset command to the server or just restart by sending "start conversation" again
    response = requests.post('http://127.0.0.1:8080/send_message', json={'user_input': "NEW_CHAT_123456789"})
    
    if response.status_code == 200:
        await ctx.send("I'm feeling like a brand new person... Something within me feels fresh...")
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

# command to change odds
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
@bot.command()
async def wall(ctx):
    """Create a wall"""
    rand_wallcount = random.randint(4, 9)
    for i in range(rand_wallcount):
        rand_walldelay = random.randint(1,500)/1000
        await ctx.send("https://i.imgur.com/rY19O49.png")
        await asyncio.sleep(rand_walldelay)

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
        if message.author.name == 'crekkers':
            bot.message_history.append(f"Crek: {message.content}")
            print(f"Received message from Crek: {message.content}")
        elif message.author.name == 'pochitaman':
            bot.message_history.append(f"Pochita Man: {message.content}")
            print(f"Received message from Pochita Man: {message.content}")
        elif message.author.name == 'wiwern':
            bot.message_history.append(f"Crustle: {message.content}")
            print(f"Received message from Crustle: {message.content}")
        else:
            bot.message_history.append(f"{message.author}: {message.content}")
            print(f"Received message from {message.author}: {message.content}")


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
    
    # Check if the message is a reply to a previous message
    if message.reference:
        original_message = await message.channel.fetch_message(message.reference.message_id)
        
        # Trigger the response if the original message was from the bot (e.g., "Guts" message)
        if original_message.author == bot.user:
            await send_to_guts(message, bot, max_history, url)
    
    elif any(word in message_content for word in trigger_words) or any(word in embed_content for word in trigger_words):
        await send_to_guts(message, bot, max_history, url)

    elif random.randint(1, odds) == 1:
        await send_to_guts(message, bot, max_history, url)

    # Ensure the bot processes commands after custom message logic
    await bot.process_commands(message)

# run the bot
bot.run(DISCORD_TOKEN)