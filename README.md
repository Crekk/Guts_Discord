# guts_discord
Simple self-hosted Discord bot, allows chatting with a character.ai bot, or system prompt using a local LLM **[KoboldCCP](https://github.com/LostRuins/koboldcpp)**, or through OpenAI's API.

Uses the **[CharacterAI API](https://github.com/kramcat/CharacterAI)** to power the chatbot

- If you're using KoboldCCP or OpenAI's API, define your character in system_prompt.txt  
- Launch through launcher.bat and select version. If you're running the KoboldCCP version, that program needs to be running beforehand  

---

## Setup

The repo now includes example config files:

- config.example.json  
- token.example.json  
- system_prompt.example.txt  

You must copy them before running:

cp config.example.json config.json  
cp token.example.json token.json  
cp system_prompt.example.txt system_prompt.txt  

Then edit them with your own values.

---

## token.json

Configure token.json file with the following information:

{
    "DISCORD_TOKEN": "", 
    "CHARACTER_AI_TOKEN": "", 
    "CHAR_ID": "", 
    "OPENAI_TOKEN": ""
}

DISCORD_TOKEN = Discord bot token  

- if using character.ai (DEPRECATED):

CHARACTER_AI_TOKEN = Character AI token, see https://github.com/kramcat/CharacterAI on how to obtain  

CHAR_ID = ID of the character.ai bot, found in the chat link: https://character.ai/chat/CHAR_ID  

- if using openai:

OPENAI_TOKEN = your OpenAI key  

You can change the model the bot uses in guts_openai.py, by default it's set to gpt-4.1-mini  

---

## Notes

- config.json, token.json, and system_prompt.txt are ignored by git  
- this prevents committing tokens or private configs  
- do NOT edit the .example files directly  

---

If running multiple bots on the same network, you have to change all instances of the port that guts.py uses to something else for the other bot, simply replace 8080 in all scripts with a different port, for example 8090
