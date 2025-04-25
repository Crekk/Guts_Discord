import asyncio
import json
from aiohttp import web
import requests

KOBOLD_API_URL = "http://127.0.0.1:5001/api/v1/generate"  # or whatever port you used!

with open("system_prompt.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()
        
history = system_prompt + "\n"

async def handle_request(request):
    global history
    try:
        # Get the user input from the request
        data = await request.json()
        user_input = data.get('user_input', '')
        
        if user_input.lower() in ['exit', 'quit']:
            return web.json_response({"response": "Exiting chat."})

        # Create the payload for the API request
        payload = {
            "prompt": history + f"User: {user_input}\nGuts:",
            "temperature": 0.7,
            "max_new_tokens": 300,
            "stop_sequence": ["User:","User","Guts:","Crek:","Pochita Man:","Crustle:"],
            "top_p": 0.9,
            "top_k": 50
        }

        # Send the request to the KOBOLD_API_URL
        response = requests.post(KOBOLD_API_URL, json=payload)
        result = response.json()

        # Extract the response text
        ai_text = result["results"][0]["text"].strip()

        # Fix accidental trailing "User:", "Guts:", "Crek:"
        if ai_text.endswith("User:") or ai_text.endswith("Guts:") or ai_text.endswith("Crek:"):
            ai_text = ai_text[:-5].strip()

        # Fix accidental trailing "User":
        if ai_text.endswith("User"):
            ai_text = ai_text[:-4].strip()

        # Fix accidental trailing "Crustle:":
        if ai_text.endswith("Crustle:"):
            ai_text = ai_text[:-8].strip()

        # Fix accidental trailing "Pochita Man:":
        if ai_text.endswith("Pochita Man:"):
            ai_text = ai_text[:-12].strip()

        # Update history
        history += f"User: {user_input}\nGuts: {ai_text}\n"

        return web.json_response({"response": ai_text})

    except Exception as e:
        return web.json_response({"error": str(e)})

async def init():
    app = web.Application()
    app.add_routes([web.post('/send_message', handle_request)])
    return app

# Run the web server
if __name__ == '__main__':
    web.run_app(init(), port=8080)
