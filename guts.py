import discord
from discord.ext import commands
from characterai import aiocai
import asyncio
import random
import json

# CUSTOMIZABLE VARIABLES
trigger_words = ['guts', 'hornet', 'heracross', 'captain hot', 'evil morty']
odds = 20  # 1 in odds chance of responding to a message

# load tokens from json
with open('token.json') as f:
    config = json.load(f)

DISCORD_TOKEN = config['DISCORD_TOKEN']
CHARACTER_AI_TOKEN = config['CHARACTER_AI_TOKEN']
CHAR_ID = config['CHAR_ID']

# initialize the bot
intents = discord.Intents.default()
intents.message_content = True  # Enable reading messages
bot = commands.Bot(command_prefix=",", intents=intents)

# initialize CharacterAI client
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

# restart chat command
@bot.command()
async def restart(ctx):
    """start a new chat on c.ai"""
    print("Restarting CharacterAI chat session...")
    
    # Create a new chat session
    bot.ai_chat, bot.chat_id = await start_ai_chat()
    
    # Confirm to the user that the chat has been restarted
    await ctx.send("Oh, huh, I'm feeling like a brand new person... Something within me feels fresh...")

# read messages
@bot.event
async def on_message(message):
    # if bot is the author, ignore
    if message.author == bot.user:
        return

    # log received message
    print(f"Received message from {message.author}: {message.content}")

    # guts triggers
    if any(word in message.content.lower() for word in trigger_words) or random.randint(1, odds) == 1:
        # send message to c.ai, get response
        user_message = message.content
        print(f"sending message: {user_message}")
        # await response
        ai_message = await bot.ai_chat.send_message(CHAR_ID, bot.chat_id, user_message)
        print(f"recieved response: {ai_message.text}")
        # send response to discord
        await message.channel.send(ai_message.text)

    # ensure the bot processes other commands
    await bot.process_commands(message)

# run the bot
bot.run(DISCORD_TOKEN)