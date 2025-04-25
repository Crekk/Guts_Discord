# guts_discord
Simple self-hosted Discord bot, allows chatting with a character.ai bot, or system prompt using a local LLM **[KoboldCCP](https://github.com/LostRuins/koboldcpp)**, or through OpenAI's API.

Uses the **[CharacterAI API](https://github.com/kramcat/CharacterAI)** to power the chatbot

-If you're using KoboldCCP or OpenAI's API, define your character in system_prompt.txt 
-Launch through launcher.bat and select version. If you're running the KoboldCCP version, that program needs to be running beforehand

Configure token.json file with the following information:
```json
{
    "DISCORD_TOKEN": "", 
    "CHARACTER_AI_TOKEN": "", 
    "CHAR_ID": "" 
    "OPENAI_TOKEN": ""
}
```
DISCORD_TOKEN = Discord bot token

-if using character.ai:

CHARACTER_AI_TOKEN = Character AI token, see **[kramcat/CharacterAI](https://github.com/kramcat/CharacterAI)** on how to obtain
CHAR_ID = ID of the character.ai bot, found in the chat link: https://character.ai/chat/CHAR_ID

-if using openai:

OPENAI_TOKEN = your OpenAI key

also, you can change the model the bot uses in guts_openai.py, by default it's set to gpt-4.1-mini

If running multiple bots on the same network, you have to change the all instances of the port that guts.py uses to something else for the other bot, simply replace 8080 in all scripts with a different port, for example 8090
