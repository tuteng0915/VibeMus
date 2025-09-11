"""Single-turn control test harness for group 2.

Transforms requirements and saves dialogs and outputs.
"""

import os
from assistant import *
from tools import *
import json5
from concurrent.futures import ThreadPoolExecutor, as_completed

prompt = '''You are a player in a role-playing game. Your role is a user of a song generating dialogue agent, and your goal is to have the song agent generate a song that meets your requirements. You should tell the agent your requirements about the song, the given input will be a request to find a song, you're going to transform it into a request to generate a song, keeping the features of the song while changing the action from finding to generating.

Meanwhile, the user's role is the song agent, it will respond you and generate the lyrics and the tags of the song.

The first user input will be the user requirements for your role-playing game (the song generating agent will not know it). After that input, please make your request.
'''

comment = '''
@register_tool('param_getter')
class GetParam(BaseTool):
    description = 'getting a parameter of the song, including the tags and the lyrics'
    parameters = [{
        'name': 'name',
        'type': 'string',
        'description': 'the name of the parameter, either "tags" or "lyrics"',
        'required': True
    }]

    def call(self, params, **kwargs) -> str:
        obj = json5.loads(params)
        ret = kwargs['var_dict'].get(obj['name'], 'empty')
        return f'the value of the parameter {obj["name"]} is: \n\n {ret}'

@register_tool('halt')
class Halt(BaseTool):
    description = 'halt the process, the equivalent of "generate" button the agent mentions'
    parameters = []
    
    def call(self, params, **kwargs) -> str:
        kwargs['var_dict']['halt'] = True
        return 'Successfully halted.'
#'''

with open('user_llm_config.json') as f:
    llm_config = json5.load(f)

load_dotenv()

env_api = os.getenv('DASHSCOPE_API_KEY')
if env_api:
    llm_config['api_key'] = env_api
elif not llm_config.get('api_key'):
    print('[VibeMus Test] Warning: DASHSCOPE_API_KEY not set and no api_key in user_llm_config.json. LLM calls may fail.')
#'''
user = Assistant(
    llm=llm_config,
    system_message=prompt,
)

def test_single_data(msg, data_id):
    """Run a single exchange and save artifacts for one item."""
    vd = {
        'halt': False,
        'preference': ''
    }

    print(f'test for {data_id} began')
    messages_for_u = [{
        'role': 'user',
        'content': f'Your Requirements: \n {msg}\n Please begin requesting the agent.' 
    }]

    messages_for_a = []

    dialog_for_saving = []
    for response in user.run(messages_for_u, var_dict=vd):
        ...
    print(f'test for {data_id} user responsed')
    messages_for_u.extend(response)
    curr = '\n'.join(i['content'] for i in response)
    with open(f'../data/transformed/{data_id}', 'w', encoding='utf-8') as f:
        f.write(curr)
    dialog_for_saving.append('User : \n' + curr)
    messages_for_a.append({
        'role': 'user',
        'content': curr
    })
    for response in assistant.run(messages_for_a, var_dict=vd):
        ...
    print(f'test for {data_id} agent responsed')
    messages_for_a.extend(response)
    curr = '\n'.join(i['content'] for i in response)
    dialog_for_saving.append('Agent : \n' + curr)

    with open(f'test_data/lyrics_and_tags/{data_id}.txt', 'w', encoding='utf-8') as f:
        f.write(
            'Tags :\n' \
                + vd.get('tags', 'tags not generated') \
                + '\nLyrics :\n' \
                + vd.get('lyrics', 'lyrics not generated')
        )

    with open(f'test_data/dialogs/{data_id}.txt', 'w', encoding='utf-8') as f:
        f.write(
            '\n'.join(dialog_for_saving)
        )
#'''

with open("../data/data.jsonl") as f:
    all_data = [json5.loads(i) for i in f]

with open('../data/result.json') as f:
    result = json5.load(f)

count = 0


#'''
with ThreadPoolExecutor(8) as executor:
    futures = [executor.submit(test_single_data, i['raw_text'], i['id']) for i in all_data if result.get(i['id'], 0) >= 25]
    for future in as_completed(futures):
        _ = future.result()
        count += 1
        if count % 10 == 0:
            print(f'{count} assessment done!')
#'''
