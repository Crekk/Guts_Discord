# guts_discord
Simple self-hosted Discord bot, allows chatting with a character.ai bot, or local LLM character via **[KoboldCCP](https://github.com/LostRuins/koboldcpp)**

Uses the **[CharacterAI API](https://github.com/kramcat/CharacterAI)** to power the chatbot

Launch through launcher.bat and select version, if running the KoboldCCP version, need that running beforehand


Requires token.json file with the following information:
```json
{
    "DISCORD_TOKEN": "token", 
    "CHARACTER_AI_TOKEN": "token", 
    "CHAR_ID": "token" 
}
```
DISCORD_TOKEN = Discord bot token

CHARACTER_AI_TOKEN = Character AI token, see **[kramcat/CharacterAI](https://github.com/kramcat/CharacterAI)** on how to obtain

CHAR_ID = ID of the character.ai bot, found in the chat link: https://character.ai/chat/CHAR_ID
