import discord
from discord.ext import commands
from characterai import aiocai
import asyncio
import random
import json

# CUSTOMIZABLE VARIABLES
trigger_words = [
    'guts', 'hornet', 'heracross', 'captain hot', 'evil morty', 'question of the day', 
    'qotd', 'society livers', 'tower of rebirth', 'jailer', 'peakland', 'rhinor', 
    'fire castle', 'creeper', 'gamers', 'hot gun', 'dranoel', 'big gutsus', 'chungling', 'big chungus', 'berserk 2', 'impostor', 
    'pinsir', 'focus sash', 'burning village', 'impostor', 'society',
    'fire capitol', 'police brutality', 'burned village', 'chungus', 'colossal titans', 'berserk'
]
odds = 50  # 1 in odds chance of responding to a message
max_history = 2  # number of previous messages to include

# load tokens from json
with open('token.json') as f:
    config = json.load(f)

DISCORD_TOKEN = config['DISCORD_TOKEN']
CHARACTER_AI_TOKEN = config['CHARACTER_AI_TOKEN']
CHAR_ID = config['CHAR_ID']

# initialize the bot
intents = discord.Intents.default()
intents.message_content = True  # enable reading messages
bot = commands.Bot(command_prefix=",", intents=intents)

# initialize cai client
client = aiocai.Client(CHARACTER_AI_TOKEN)

# start new session, ai side
async def start_ai_chat():
    me = await client.get_me()
    chat = await client.connect()
    new, answer = await chat.new_chat(CHAR_ID, me.id)
    return chat, new.chat_id

# start new session, discord side
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    bot.ai_chat, bot.chat_id = await start_ai_chat()
    bot.message_history = []  # start message history

# command to restart chat 
@bot.command()
async def restart(ctx):
    """start a new chat on c.ai"""
    print("Restarting CharacterAI chat session...")
    
    # create a new chat session
    bot.ai_chat, bot.chat_id = await start_ai_chat()
    bot.message_history = []  # clear message history
    
    # character line about restarting chat
    await ctx.send("Oh, huh, I'm feeling like a brand new person... Something within me feels fresh...")

# command to display all trigger words 
@bot.command()
async def triggers(ctx):
    """Displays all the trigger words"""
    trigger_list = ', '.join(trigger_words)
    await ctx.send(f"Current trigger words: {trigger_list}")


# read messages
@bot.event
async def on_message(message):
    # if bot is the author, ignore
    if message.author == bot.user:
        return

    # ignore empty messages
    if not message.content and not message.embeds:
        print(f"Received empty message from {message.author}")
        return

    # regular text messages
    if message.content:
        bot.message_history.append(f"{message.author}: {message.content}")
        print(f"Received message from {message.author}: {message.content}")

    
    # embeds
    if message.embeds:
        # If the message contains embeds, extract the title and description
        for embed in message.embeds:
            embed_text = f"**{embed.title}**\n{embed.description}" if embed.title else embed.description
            # Print the embed content for debugging
            print(f"Received embed from {message.author}: {embed_text}")
            # Only append to history if embed has content
            if embed_text.strip():  # Ensure there is actual text to process
                bot.message_history.append(f"{message.author}: {embed_text}")

    # keep only the last "max_history" messages
    if len(bot.message_history) > max_history * 2:
        bot.message_history.pop(0)  # remove the oldest message

    # guts triggers
    if any(word in message.content.lower() for word in trigger_words) or random.randint(1, odds) == 1:
        # send the messages to the bot
        context = '\n'.join(bot.message_history[-max_history * 2:])  # include recent 2 * max_history messages
        print(f"Sending to CharacterAI with context:\n{context}")
        
        # send message to c.ai with context, get response
        ai_message = await bot.ai_chat.send_message(CHAR_ID, bot.chat_id, context)
        print(f"Received response: {ai_message.text}")
        
        # send response to discord
        await message.channel.send(ai_message.text)
        bot.message_history = []  # clear message history


    # ensure the bot processes other commands
    await bot.process_commands(message)

# run the bot
bot.run(DISCORD_TOKEN)
