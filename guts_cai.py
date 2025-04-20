import asyncio
import json
from aiohttp import web
from characterai import aiocai

# Store chat sessions for different users (in-memory for simplicity)
chat_sessions = {}

# Define the long message code that triggers a new chat session
NEW_CHAT_CODE = "NEW_CHAT_123456789"

async def handle_request(request):
    # Get the user input from the request
    data = await request.json()
    user_input = data.get('user_input', '')
    
    if not user_input:
        return web.json_response({"error": "No user input provided."}, status=400)
    
    # Load tokens from JSON
    with open('token.json') as f:
        config = json.load(f)
        CHARACTER_AI_TOKEN = config['CHARACTER_AI_TOKEN']
        CHAR_ID = config['CHAR_ID']
    
    client = aiocai.Client(CHARACTER_AI_TOKEN)

    try:
        # Start a chat session
        me = await client.get_me()
        
        # Check if the user input is the code to start a new chat session
        if user_input.strip() == NEW_CHAT_CODE:
            print("Starting a new chat session...")
            # If the code is matched, start a new chat and reset the chat_id
            async with await client.connect() as chat:
                new_chat_info, first_response = await chat.new_chat(CHAR_ID, me.id)
                chat_sessions.clear()  # Clear all stored chat sessions to reset
                chat_sessions['chat_id'] = new_chat_info.chat_id  # Store the new chat_id
                print(f'{first_response.name}: {first_response.text}')
                return web.json_response({"response": "New chat session started."})
        elif 'chat_id' not in chat_sessions:
            # If no session, create a new chat
            async with await client.connect() as chat:
                new_chat_info, first_response = await chat.new_chat(CHAR_ID, me.id)
                chat_sessions['chat_id'] = new_chat_info.chat_id  # Store chat_id
                print(f'{first_response.name}: {first_response.text}')
        else:
            # Use the existing chat session
            chat_id = chat_sessions['chat_id']

        # Send user input to the chat using the existing or new chat_id
        async with await client.connect() as chat:
            message = await chat.send_message(CHAR_ID, chat_id, user_input)

        print(f'{message.name}: {message.text}')
        return web.json_response({"response": message.text})
    
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def init():
    app = web.Application()
    app.add_routes([web.post('/send_message', handle_request)])
    return app

# Run the web server
if __name__ == '__main__':
    web.run_app(init(), port=8080)
