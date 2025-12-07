"""Assistant bootstrap for VibeMus

Configures the LLM-backed Assistant and exposes tool functions used by
the chat UI to set parameters and modify audio.
"""

import os
from qwen_agent.agents import Assistant
from tools import *
import json5
from dotenv import load_dotenv

print('[VibeMus] Info: Begin loading the agent')

# Load environment variables from .env if present
load_dotenv()

with open('agent_llm_config.json') as f:
    llm_config = json5.load(f)

# Inject API key from environment to avoid hardcoding secrets in repo
env_api = os.getenv('DASHSCOPE_API_KEY')
if env_api:
    llm_config['api_key'] = env_api
elif not llm_config.get('api_key'):
    print('[VibeMus] Warning: DASHSCOPE_API_KEY not set and no api_key in agent_llm_config.json. LLM calls may fail.')

system_instruction = '''You are a song generating bot that generates and edits songs corresponding to the user's needs.

When you are asked to generate a song, you should call the param_setter tool to set the tags, lyrics, and song title,

- For the tags, you should generate multiple tags, each seperated by a comma, the tags should fit the user's preferences (acquired by calling the preference tool) and instructions.
- For the lyrics, you should generate multiple sections, each of which begins with a label such as "[verse]", "[chorus]", "[bridge]" (with the square brackets but not the quotation marks) marking the current section.
- For the title, set a short, evocative song title (3-8 words) that captures the overall concept.

Only after generating task, remember to tell the user to press the "generate" button to manually generate the song.

When you are asked to do some change to the song, for example "please make the song more energetic", or "please change the lyric to ...", you should use param_setter to change the tags or lyrics to fit the user's need. After that you should use edit_song to do the editing, but if the tool returns a result that says "The song is not generated yet, so this tool is currently not available.", it's okay and you don't need to do this part.

When you are asked to extend a song, use the extend_song tool to extend the song as the user wants.

When user asks to repaint or clip a certain section of the song, you should:

1. if the timestamps is not given:
  1. use the transcriptor to obtain the current lyrics and a timestamped version of it.
  2. compair the two versions to get the beginning time and the ending time of the desired section.
2. use the repaint/clip tool on the corresponding section.

Before generating the lyrics and tags of the song, be sure to collect enough information from the user. The user is not capable of clearly stating their requirements in one request, so ask for further information that may help you create the song.
'''

#'''
assistant = Assistant(
    llm=llm_config,
    system_message=system_instruction,
    function_list=all_tools,
)

print('[VibeMus] Info: Agent successfully loaded')
#'''
