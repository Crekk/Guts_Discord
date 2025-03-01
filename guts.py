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
odds = 100  # 1 in odds chance of responding to a message
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
    if any(word in message_content for word in trigger_words) or any(word in embed_content for word in trigger_words):
        
        # set the context as last couple messages
        context = '\n'.join(bot.message_history[-max_history * 2:])  # include recent 2 * max_history messages
        print(f"Sending to CharacterAI with context:\n{context}")
        print(f"Triggered by message: {message_content}")
        # Send message to c.ai, get response
        try:
            ai_message = await bot.ai_chat.send_message(CHAR_ID, bot.chat_id, context)
            print(f"Received response: {ai_message.text}")
        except Exception as e:
            print(f"Error encountered: {e}. Restarting session...")
            bot.ai_chat, bot.chat_id = await start_ai_chat() # start new session       
            ai_message = await bot.ai_chat.send_message(CHAR_ID, bot.chat_id, context) # send message again
            print(f"Received response after retry: {ai_message.text}")

        # remove "Guts:" prefix if it exists
        if ai_message.text.startswith('Guts:'):
            processed_text = ai_message.text[6:].strip()
        else:
            processed_text = ai_message.text

        # send response to discord
        await message.channel.send(processed_text)
        bot.message_history = []  # clear message history

    elif random.randint(1, odds) == 1:
            
            # set the context as last couple messages
            context = '\n'.join(bot.message_history[-max_history * 2:])  # include recent 2 * max_history messages
            print(f"Sending to CharacterAI with context:\n{context}")
            print(f"Triggered by random chance")
            # Send message to c.ai, get response
            try:
                ai_message = await bot.ai_chat.send_message(CHAR_ID, bot.chat_id, context)
                print(f"Received response: {ai_message.text}")
            except Exception as e:
                print(f"Error encountered: {e}. Restarting session...")
                bot.ai_chat, bot.chat_id = await start_ai_chat() # start new session       
                ai_message = await bot.ai_chat.send_message(CHAR_ID, bot.chat_id, context) # send message again
                print(f"Received response after retry: {ai_message.text}")

            # remove "Guts:" prefix if it exists
            if ai_message.text.startswith('Guts:'):
                processed_text = ai_message.text[6:].strip()
            else:
                processed_text = ai_message.text

            # send response to discord
            await message.channel.send(processed_text)
            bot.message_history = []  # clear message history


    # ensure the bot processes other commands
    await bot.process_commands(message)

# run the bot
bot.run(DISCORD_TOKEN)