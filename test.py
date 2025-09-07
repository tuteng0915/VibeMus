"""Automated dialog simulation between a 'user' agent and the Assistant.

Used to generate/collect tags & lyrics and save conversation transcripts.
"""

from assistant import *
from tools import *
import json5
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

prompt = '''You are a player in a role-playing game. Your role is a user of a song generating dialogue agent, you should tell the agent your requirements about the song, but as a user, you should express your needs in a vague and non-professional way as a real human would do. You also shouldn't express all your needs in the first request, instead, do follow-up requests about your requirements when the agent asks you for further information. Specifically, you should say no more than a simple sentence for each reply.

Meanwhile, the user's role is the song agent, it will respond you and generate the lyrics and the tags of the song, you will be able to retrieve them via the "param_getter" tool. When the generating agent asks you about details of the song, you can either make up some information or simply claim that it's irrelevant. When you feel the song is perfect, use the "halt" tool to terminate the process, this is the equivalent of the "generate" button that the song generating agent mentions.

The first user input will be your requirements. After that input, please make your first request.
'''

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
        """Return current value of a requested parameter."""
        obj = json5.loads(params)
        ret = kwargs['var_dict'].get(obj['name'], 'empty')
        return f'the value of the parameter {obj["name"]} is: \n\n {ret}'

@register_tool('halt')
class Halt(BaseTool):
    description = 'halt the process, the equivalent of "generate" button the agent mentions'
    parameters = []
    
    def call(self, params, **kwargs) -> str:
        """Signal the driver loop to stop further turns."""
        kwargs['var_dict']['halt'] = True
        return 'Successfully halted.'

load_dotenv()
with open('user_llm_config.json') as f:
    llm_config = json5.load(f)

# Prefer environment variable over file to avoid hardcoding secrets
env_api = os.getenv('DASHSCOPE_API_KEY')
if env_api:
    llm_config['api_key'] = env_api
elif not llm_config.get('api_key'):
    print('[VibeMus Test] Warning: DASHSCOPE_API_KEY not set and no api_key in user_llm_config.json. LLM calls may fail.')

#'''
user = Assistant(
    llm=llm_config,
    system_message=prompt,
    function_list=['param_getter', 'halt'],
)
#'''
revert = {
    'assistant': 'user',
    'user': 'assistant',
    'function': 'function',
}

vd = {
    'halt': False,
    'preference': ''
}



def test_single_data(msg, data_id):
    """Run a short back-and-forth to elicit tags/lyrics for one item."""
    print(f'test for {data_id} began')
    messages_for_u = [{
        'role': 'user',
        'content': msg
    }]

    messages_for_a = []

    dialog_for_saving = []
    for i in range(10):
        for response in user.run(messages_for_u, var_dict=vd):
            ...
        print(f'test for {data_id} round {i} user responsed')
        if vd['halt']:
            break
        messages_for_u.extend(response)
        curr = '\n'.join(i['content'] for i in response)
        dialog_for_saving.append('User : \n' + curr)
        messages_for_a.append({
            'role': 'user',
            'content': curr
        })
        for response in assistant.run(messages_for_a, var_dict=vd):
            ...
        print(f'test for {data_id} round {i} agent responsed')
        messages_for_a.extend(response)
        curr = '\n'.join(i['content'] for i in response)
        dialog_for_saving.append('Agent : \n' + curr)
        messages_for_u.append({
            'role': 'user',
            'content': curr
        })

    with open(f'test_data/lyrics_and_tags/{data_id}.txt', 'w') as f:
        f.write(
            'Tags :\n' \
                + vd.get('tags', 'tags not generated') \
                + 'Lyrics :\n' \
                + vd.get('lyrics', 'lyrics not generated')
        )

    with open(f'test_data/dialogs/{data_id}.txt', 'w') as f:
        f.write(
            '\n'.join(dialog_for_saving)
        )
#'''
with open("test_data/data.jsonl") as f:
    all_data = [json5.loads(i) for i in f]

with open('test_data/result.json') as f:
    result = json5.load(f)

count = 0

with ThreadPoolExecutor(8) as executor:
    futures = [executor.submit(test_single_data, i['raw_text'], i['id']) for i in all_data if result.get(i['id'], 0) >= 25]
    for future in as_completed(futures):
        _ = future.result()
        count += 1
        if count % 10 == 0:
            print(f'{count} assessment done!')
