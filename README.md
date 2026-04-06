# guts_discord
Simple self-hosted Discord bot, allows chatting with a character.ai bot, or system prompt using a local LLM **[KoboldCCP](https://github.com/LostRuins/koboldcpp)**, or through OpenAI's API.

-If you're using KoboldCCP or OpenAI's API, define your character in system_prompt.txt  
-Launch through launcher.bat and select version. If you're running the KoboldCCP version, that program needs to be running beforehand  

---

## Setup

The repo now includes example config files:

- `config.example.json`
- `token.example.json`
- `system_prompt.example.txt`

You need to copy them before running:

```bash
cp config.example.json config.json
cp token.example.json token.json
cp system_prompt.example.txt system_prompt.txt
