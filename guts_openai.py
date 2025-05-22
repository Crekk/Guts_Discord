import asyncio
import json
from aiohttp import web
from openai import AsyncOpenAI  # Use the async version!
import os

# Load OpenAI token
with open('token.json') as f:
    config = json.load(f)

OPENAI_TOKEN = config['OPENAI_TOKEN']
client = AsyncOpenAI(api_key=OPENAI_TOKEN)

# System prompt
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()

# Store chat history (for now globally, could be upgraded later)
chat_history = [
    {"role": "system", "content": system_prompt}
]

# Handler for POST /send_message
async def handle_send_message(request):
    global chat_history
    try:
        data = await request.json()
        user_input = data.get('user_input', '')

        # Special reset code sent by Discord bot
        if user_input.strip() == "NEW_CHAT_123456789":
            print("Received reset command, clearing history.")
            chat_history = [{"role": "system", "content": system_prompt}]
            return web.json_response({'response': "Chat history reset."})

        # Add new user message to chat history
        chat_history.append({"role": "user", "content": user_input})

        # Call OpenAI with the full history
        response = await client.chat.completions.create(
            model="gpt-4.1-mini",  # or your model
            messages=chat_history
        )
        ai_response = response.choices[0].message.content.strip()

        # Add the AI's reply to chat history
        chat_history.append({"role": "assistant", "content": ai_response})

        print(f"AI Response: {ai_response}")

        return web.json_response({'response': ai_response})

    except Exception as e:
        print(f"Error: {e}")
        return web.json_response({'error': str(e)}, status=500)

# Set up app
app = web.Application()
app.router.add_post('/send_message', handle_send_message)

# Run server
if __name__ == '__main__':
    web.run_app(app, host='127.0.0.1', port=8080)
