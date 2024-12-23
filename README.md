# guts_discord
Simple self-hosted Discord bot, that allows chatting with a character.ai bot, uses the **[CharacterAI API](https://github.com/kramcat/CharacterAI)** to power the chatbot. The API is an unofficial wrapper for interacting with CharacterAI's platform.

Requires token.json file with the following information:
```json
{
    "DISCORD_TOKEN": "", 
    "CHARACTER_AI_TOKEN": "", 
    "CHAR_ID": "" 
}
```
DISCORD_TOKEN = Discord bot token

CHARACTER_AI_TOKEN = Character AI token, see **[kramcat/CharacterAI](https://github.com/kramcat/CharacterAI)** on how to obtain

CHAR_ID = ID of the character.ai bot, found in the chat link: https://character.ai/chat/CHAR_ID
