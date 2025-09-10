from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from turtle import reset
from qwen_agent.agents.assistant import Assistant
from qwen_agent.tools.base import BaseTool, register_tool
import json
import json5
from dotenv import load_dotenv

load_dotenv()
with open('user_llm_config.json') as f:
    llm_config = json5.load(f)

# Prefer environment variable over file to avoid hardcoding secrets
env_api = os.getenv('DASHSCOPE_API_KEY')
if env_api:
    llm_config['api_key'] = env_api
elif not llm_config.get('api_key'):
    print('[VibeMus Test] Warning: DASHSCOPE_API_KEY not set and no api_key in user_llm_config.json. LLM calls may fail.')

prompt = '''Your are a data assessing agent, your job is to assess a user-agent dialog according to a given requirement. The agent in the dialog is a song generating agent, and the user in the dialog is to use the agent to generate a song that fits the requirement. Your goal is to determine how many different points of the requirement are mentioned in the dialog. Specifically you should:

1. split the requirement in to different simple points of need, those points eventually add up to the whole requirement;
2. determine whether each point has occurred in the dialog.

the user input will be in the following format:

- the first user input will be the requirement, after that you should split the requirement in to different points, each represented with a keyword or short phrase. For each keyword / short phrase, invoke the "record_keyword" tool to record it.
- each of the following input will be a pair of user input and agent response. For each point that is mentioned in this round of dialog, invoke the "record_occurrence" tool with the corresponding keyword mentioned in step 1 to record it.
'''

@register_tool("record_keyword")
class RecordKeyword(BaseTool):
    description = "The tool for keyword recording."
    parameters = [{
        "name": "keyword",
        "type": "string",
        "description": 'The keyword / short phrase for the point of need',
        "required": True,
    }]
    
    def call(self, params, **kwargs):
        obj = json5.loads(params)
        var_dict = kwargs['var_dict']
        if var_dict['round'] > 0:
            return 'when assessing the dialog, you don\'t need to record any keywords.'
        new_kw = obj['keyword']
        if new_kw in var_dict['occurrence']:
            return f'keyword "{new_kw}" already recorded.'
        var_dict['keywords'].append(new_kw)
        var_dict['occurrence'][new_kw] = -1
        return f'keyword {new_kw} successfully recorded.'

@register_tool("record_occurrence")
class RecordKeyword(BaseTool):
    description = "The tool for point occurrence recording."
    parameters = [{
        "name": "keyword",
        "type": "string",
        "description": 'The keyword / short phrase for the occurred point of need',
        "required": True,
    }]
    
    def call(self, params, **kwargs):
        obj = json5.loads(params)
        var_dict = kwargs['var_dict']
        rnd = var_dict['round']
        if rnd == 0:
            return 'when displaying the requirement, you shouldn\'t use this tool.'
        new_kw = obj['keyword']
        if new_kw not in var_dict['occurrence']:
            return f'keyword "{new_kw}" not recorded. All the keywords recorded are "'\
                + '", "'.join(var_dict['keywords']) + '".'
        if var_dict['occurrence'][new_kw] == -1:
            var_dict['occurrence'][new_kw] = rnd
        return f'occurrence of the requirement {new_kw} successfully recorded.'

agent = Assistant(
    ["record_keyword", "record_occurrence"],
    llm_config,
    prompt
)

def score_data(data: dict, dialog: str) -> tuple[dict, str]:
    print(f'assessment began for {data['id']}')
    var_dict = {
        "keywords": [],
        "occurrence": {},
        'round': 0,
    }
    lst = []
    curr = []
    flag = False
    for line in dialog.split('\n'):
        if line == 'User : ':
            if flag:
                lst.append('\n'.join(curr))
                curr = []
            else:
                flag = True
        curr.append(line)
    lst.append('\n'.join(curr))
    history = [{
        'role': 'user',
        'content': f'Requirement: \n{data['raw_text']}'
    }]
    response = agent.run_nonstream(history, var_dict=var_dict)
    history.extend(response)
    for pair in lst:
        var_dict['round'] += 1
        history.append({
            'role': 'user',
            'content': pair,
        })
        response = agent.run_nonstream(history, var_dict=var_dict)
        history.extend(response)
    return var_dict['occurrence'], data['id']

with open("data.jsonl") as f:
    all_data = [json.loads(i) for i in f]

with open('result.json') as f:
    result = json.load(f)

curr_group = 'demo'


occurred_total = 0
count = 0
result_diff = [0 for _ in range(11)]

with ThreadPoolExecutor(8) as executor:
    futures = []
    for i in all_data:
        if result.get(i['id'], 0) < 25:
            continue
        path = f'{curr_group}/test_data/dialogs/{i['id']}.txt'
        if not os.path.exists(path):
            print(f'{path} was not generated')
            continue
        try:
            with open(path, encoding='utf-8') as f:
                dialog = f.read()
        except UnicodeDecodeError:
            with open(path) as f:
                dialog = f.read()
        futures.append(executor.submit(score_data, i, dialog))
    for future in as_completed(futures):
        curr, d_id = future.result()
        for v in curr.values():
            occurred_total += 1
            if v == -1:
                continue
            result_diff[v] += 1
        count += 1
        if count % 10 == 0:
            print(f'{count} assessments done.')
            with open(f'dialog eval of {curr_group}.json', 'w') as f:
                json.dump({
                    'total': occurred_total,
                    'diff': result_diff,
                }, f)
    with open(f'dialog eval of {curr_group}.json', 'w') as f:
        print(f'all assessments done.')
        json.dump({
            'total': occurred_total,
            'diff': result_diff,
        }, f)
#'''