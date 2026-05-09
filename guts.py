import discord  # type: ignore
from discord.ext import commands  # type: ignore
import aiohttp
import asyncio
import random
import json
import time
import re

try:
    with open("config.json") as f:
        settings = json.load(f)
        print("Config loaded from config.json.")
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Failed to load config file: {e}")
    raise SystemExit(1)

# Assign settings to variables
url = settings.get("url", "http://127.0.0.1:8080/send_message")
BOT_NAME = settings.get("bot_name", "Guts")
trigger_words = settings.get("trigger_words", [])
USERNAME_MAP = settings.get("username_map", {})
CMD_PREFIX = settings.get("command_prefix", ",")
RESTART_MSG = settings.get(
    "restart_message",
    "I'm feeling like a brand new person... Something within me feels fresh..."
)
odds = settings.get("odds", 250)
react_odds = settings.get("react_odds", 1000)
max_history = settings.get("max_history", 3)
inactivity_timer = settings.get("inactivity_timer", 15 * 60)
typing_max = settings.get("typing_max", 5.0)
typing_perchar = settings.get("typing_perchar", 0.03)
wall_enabled = settings.get("wall_enabled", True)
wall_url = settings.get("wall_url", "https://i.imgur.com/rY19O49.png")
wall_count_min = settings.get("wall_count_min", 4)
wall_count_max = settings.get("wall_count_max", 9)
http_timeout_seconds = settings.get("http_timeout_seconds", 120)

MAX_DISCORD_MESSAGE_LEN = 1800

# Load token from json
try:
    with open("token.json") as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Failed to load token file: {e}")
    raise SystemExit(1)

DISCORD_TOKEN = config["DISCORD_TOKEN"]

# Initialize the bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=CMD_PREFIX, intents=intents)

# Initialize state so attributes always exist
bot.message_history = []
bot.last_activity = time.time()
bot.inactivity_task = None


async def post_json(target_url: str, payload: dict) -> dict:
    timeout = aiohttp.ClientTimeout(total=http_timeout_seconds)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(target_url, json=payload) as response:
            response_text = await response.text()

            print(f"API Response Status: {response.status}")
            print(f"API Response Text: {response_text}")

            if response.status != 200:
                raise Exception(
                    f"Failed to get a valid response from server, "
                    f"status code: {response.status}, body: {response_text}"
                )

            try:
                return json.loads(response_text)
            except json.JSONDecodeError as e:
                raise Exception(f"Invalid JSON response: {e}. Body: {response_text}")


def clean_ai_message(text: str, bot_name: str) -> str:
    prefix = f"{bot_name}:"
    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.lower().startswith(prefix.lower()):
            line = line[len(prefix):].lstrip()

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def split_message(text: str, limit: int = MAX_DISCORD_MESSAGE_LEN) -> list[str]:
    text = text.strip()
    if not text:
        return []

    chunks = []
    remaining = text

    while remaining:
        if len(remaining) <= limit:
            chunks.append(remaining)
            break

        split_at = remaining.rfind("\n", 0, limit)
        if split_at == -1:
            split_at = remaining.rfind(" ", 0, limit)
        if split_at == -1:
            split_at = limit

        chunk = remaining[:split_at].rstrip()
        if not chunk:
            chunk = remaining[:limit]
            split_at = len(chunk)

        chunks.append(chunk)
        remaining = remaining[split_at:].lstrip()

    return chunks


async def send_long_message(channel: discord.abc.Messageable, text: str) -> None:
    chunks = split_message(text)
    print(f"Sending {len(chunks)} Discord message chunk(s).")

    if not chunks:
        return

    typing_delay = min(len(text) * typing_perchar, typing_max)

    try:
        async with channel.typing():
            await asyncio.sleep(typing_delay)
    except Exception as e:
        print(f"Typing indicator skipped: {repr(e)}", flush=True)

    for chunk in chunks:
        await channel.send(chunk)


# Start new session, AI side
async def start_ai_chat():
    retry_count = 0

    while True:
        try:
            response_data = await post_json(url, {"user_input": "start conversation"})
            return response_data.get("response", ""), None
        except Exception as e:
            print(f"Exception occurred: {e}")

        retry_count += 1
        if retry_count <= 12:
            wait_time = 10
        else:
            wait_time = 3600

        print(f"Retrying in {wait_time} seconds... (Attempt #{retry_count})")
        await asyncio.sleep(wait_time)


# Start new session, Discord side
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    bot.ai_chat, bot.chat_id = await start_ai_chat()
    bot.message_history = []
    bot.last_activity = time.time()

    if bot.inactivity_task is None or bot.inactivity_task.done():
        bot.inactivity_task = bot.loop.create_task(inactivity_reset())


async def send_to_guts(message, bot, max_history, url):
    context = "\n".join(bot.message_history[-max_history * 2:])
    print(f"Sending to {BOT_NAME} with context:\n{context}")
    print(f"Triggered by message: {message.content.lower()}")

    try:
        data = {"user_input": context}
        print(f"Sending data to {BOT_NAME}: {data}")

        response_data = await post_json(url, data)
        ai_message = response_data.get("response", "")
        print(f"Received response from {BOT_NAME}: {ai_message}")

        processed_text = clean_ai_message(ai_message, BOT_NAME)

        bot.message_history = []

        if not processed_text:
            print("Received empty processed_text; nothing to send.")
            return

        await send_long_message(message.channel, processed_text)

    except Exception as e:
        print(f"Error during sending/receiving message: {e}")
        await message.channel.send("An error occurred while processing your message.")


# Inactivity timer
async def inactivity_reset():
    while True:
        await asyncio.sleep(60)
        elapsed = time.time() - bot.last_activity
        if elapsed >= inactivity_timer and bot.message_history:
            bot.message_history.clear()
            print("Message history cleared due to inactivity.")


@bot.command()
async def restart(ctx):
    """Start a new chat on the server."""
    print(f"Restarting chat session with {BOT_NAME}...")

    try:
        await post_json(url, {"user_input": "NEW_CHAT_123456789"})
        bot.message_history = []
        await ctx.send(RESTART_MSG)
    except Exception as e:
        print(f"Restart failed: {e}")
        await ctx.send("Sorry, I couldn't restart the chat session.")


@bot.command()
async def triggers(ctx):
    """Displays all the trigger words."""
    trigger_list = ", ".join(trigger_words)
    await ctx.send(f"Current trigger words: {trigger_list}")


@bot.command()
async def changeodds(ctx, new_odds: int = None):
    """Change the odds of responding to a message."""
    global odds
    if new_odds is None:
        await ctx.send(f"The current odds are 1 in {odds}")
    else:
        odds = new_odds
        await ctx.send(f"Changed odds to 1 in {odds}")


@bot.command()
async def changehistory(ctx, new_max_history: int = None):
    """Change the number of messages to include in context."""
    global max_history
    if new_max_history is None:
        await ctx.send(f"The current messages included are {max_history + 1}")
    else:
        max_history = new_max_history
        await ctx.send(f"Changed the number of messages to include to {max_history + 1}")


if wall_enabled:
    print("Wall command is enabled")

    @bot.command()
    async def wall(ctx):
        """Create a wall."""
        rand_wallcount = random.randint(wall_count_min, wall_count_max)
        for _ in range(rand_wallcount):
            rand_walldelay = random.randint(1, 500) / 1000
            await ctx.send(wall_url)
            await asyncio.sleep(rand_walldelay)
else:
    print("Wall command is disabled")


@bot.event
async def on_message(message):
    bot.last_activity = time.time()

    if message.author == bot.user:
        return

    if not message.content and not message.embeds:
        print(f"Received empty message from {message.author}")
        return

    author_name = USERNAME_MAP.get(message.author.name, str(message.author))

    # Regular text messages
    if message.content:
        bot.message_history.append(f"{author_name}: {message.content}")

    # Embeds
    embed_texts = []
    if message.embeds:
        for embed in message.embeds:
            parts = []

            if embed.title:
                parts.append(f"**{embed.title}**")
            if embed.description:
                parts.append(embed.description)

            embed_text = "\n".join(parts).strip() if parts else ""

            print(f"Received embed from {message.author}: {embed_text if embed_text else 'None'}")

            if embed_text:
                bot.message_history.append(f"{author_name}: {embed_text}")
                embed_texts.append(embed_text)

    # Keep only the last max_history*2 messages
    while len(bot.message_history) > max_history * 2:
        bot.message_history.pop(0)

    message_content = message.content.lower() if message.content else ""
    embed_content = " ".join(embed_texts).lower()

    # Check if bot is mentioned
    if bot.user in message.mentions:
        await send_to_guts(message, bot, max_history, url)

    # Check trigger words
    elif any(re.search(rf"\b{re.escape(word)}\b", message_content) for word in trigger_words) or \
         any(re.search(rf"\b{re.escape(word)}\b", embed_content) for word in trigger_words):
        await send_to_guts(message, bot, max_history, url)

    # Random odds
    elif odds > 0 and random.randint(1, odds) == 1:
        await send_to_guts(message, bot, max_history, url)

    # Check if the message is a reply to a previous bot message
    elif message.reference and message.reference.message_id:
        try:
            original_message = await message.channel.fetch_message(message.reference.message_id)
            if original_message.author == bot.user:
                await send_to_guts(message, bot, max_history, url)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException) as e:
            print(f"Failed to fetch referenced message: {e}")

    await bot.process_commands(message)


bot.run(DISCORD_TOKEN)