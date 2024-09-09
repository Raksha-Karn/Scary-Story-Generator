
# Scary Story Generator

Welcome to the Scary Story Generator! 👻 This project takes a Reddit post containing a scary story, divides it into three distinct sections, and converts it into a spooky audio experience with sound effects.

## Features

- **Reddit Integration:** Fetches scary stories from Reddit.
- **Text Analysis:** Uses AI to divide the story into an introduction, build-up, and climax.
- **Audio Conversion:** Converts text sections into spoken audio.
- **Sound Effects:** Applies creepy effects and overlays wind sound for a chilling atmosphere.
- **Playback:** Plays the generated audio with an introduction and ending.

## Requirements

- Python 3.x
- Required Python libraries:
  - `praw` for Reddit API interaction
  - `python-dotenv` for environment variable management
  - `gtts` for text-to-speech conversion
  - `pydub` for audio manipulation
  - `langchain-ollama` for AI-driven text analysis
