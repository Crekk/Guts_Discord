import asyncio
import json
from aiohttp import web
from openai import AsyncOpenAI 
import os
from urllib.parse import urlparse

# Load OpenAI token
with open('token.json') as f:
    config = json.load(f)
# Load config file
with open("config.json") as f:
    settings = json.load(f)

OPENAI_TOKEN = config['OPENAI_TOKEN']
client = AsyncOpenAI(api_key=OPENAI_TOKEN)
model = settings.get("openai_api_model", "gpt-5-mini")
# Parse URL from config
parsed_url = urlparse(settings.get("url", "http://127.0.0.1:8080/send_message"))
host = parsed_url.hostname or "127.0.0.1"
port = parsed_url.port or 8080

# System prompt
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()

# Store chat history (per channel)

chat_histories = {}

# Handler for POST /send_message
async def handle_send_message(request):
    global chat_histories

    try:
        data = await request.json()
        user_input = data.get("user_input", "")
        channel_id = str(data.get("channel_id", "default"))

        # Special reset code sent by Discord bot
        if user_input.strip() == "NEW_CHAT_123456789":
            print("Received reset command, clearing all histories.")
            chat_histories.clear()
            return web.json_response({"response": "Chat history reset."})

        # Create this channel's history if it does not exist yet
        if channel_id not in chat_histories:
            chat_histories[channel_id] = [
                {"role": "system", "content": system_prompt}
            ]

        channel_history = chat_histories[channel_id]

        # Add new user message to this channel's chat history
        channel_history.append({"role": "user", "content": user_input})

        # Call OpenAI with this channel's history only
        response = await client.chat.completions.create(
            model=model,
            messages=channel_history
        )

        ai_response = response.choices[0].message.content.strip()

        # Add the AI's reply to this channel's chat history
        channel_history.append({"role": "assistant", "content": ai_response})

        print(f"Channel {channel_id} AI Response: {ai_response}")

        return web.json_response({"response": ai_response})

    except Exception as e:
        print(f"Error: {e}")
        return web.json_response({"error": str(e)}, status=500)
    
# Set up app
app = web.Application()
app.router.add_post('/send_message', handle_send_message)

# Run server
if __name__ == '__main__':
    web.run_app(app, host=host, port=port)