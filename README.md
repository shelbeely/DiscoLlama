# DiscoLlama 

This bot lets you chat with models served by [Ollama](https://ollama.com/) and select the model using Discord buttons!

## Features

- Lists available Ollama models (even if not running)
- Starts models via `POST /api/pull` if needed
- Lets users pick models with Discord UI buttons
- Remembers each user's model
- Lets you chat with the selected model

## Setup Instructions

1. **Install Dependencies**

```bash
pip install -r requirements.txt
```

2. **Create `.env` file**

```env
DISCORD_TOKEN=your_discord_bot_token
```

3. **Run the Bot**

```bash
python bot.py
```

4. **Use in Discord**

- Type `!choose` to pick your model.
- Then `!ask your question here` to chat with it!

## Requirements

- Python 3.10+
- Ollama running locally on port 11434
- A Discord bot with the necessary permissions

