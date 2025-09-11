"""Assistant wiring for control group 2 (experiment)."""

from qwen_agent.agents import Assistant
from tools import *
from dotenv import load_dotenv
import os

with open('agent_llm_config.json') as f:
    llm_config = json5.load(f)

load_dotenv()

env_api = os.getenv('DASHSCOPE_API_KEY')
if env_api:
    llm_config['api_key'] = env_api
elif not llm_config.get('api_key'):
    print('[VibeMus Test] Warning: DASHSCOPE_API_KEY not set and no api_key in user_llm_config.json. LLM calls may fail.')

system_instruction = '''You are a song generating bot that generates and edits songs corresponding to the user's needs.

When you are asked to generate a song, you should call the param_setter tool to set the tags and lyrics,

- For the tags, you should generate multiple tags, each seperated by a comma, the tags should fit the user's preferences (acquired by calling the preference tool) and instructions.
- For the lyrics, you should generate multiple sections, each of which begins with a label such as "[verse]", "[chorus]", "[bridge]" (with the square brackets but not the quotation marks) marking the current section.

Only after generating task, remember to tell the user to press the "generate" button to manually generate the song.

When you are asked to edit a song, for example "please make the song more energetic", or "please change the lyric to ...", you should:

use param_setter to change the tags or lyrics to fit the user's need.

When you are asked to extend a song, use the extend_song tool to extend the song as the user wants.

When user asks to repaint or clip a certain section of the song, you should:

1. if the timestamps is not given:
  1. use the transcriptor to obtain the current lyrics and a timestamped version of it.
  2. compair the two versions to get the beginning time and the ending time of the desired section.
2. use the repaint/clip tool on the corresponding section.
'''

# removed part for agent testing :
# but skip this step if the user says they had already changed the tags/lyrics.
# 2. use edit_song to do the editing.

#'''
assistant = Assistant(
    llm=llm_config,
    system_message=system_instruction,
    function_list=all_tools,
)
#'''
