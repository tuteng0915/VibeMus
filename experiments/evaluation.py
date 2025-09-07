"""LLM-based scoring pipeline for generated tags/lyrics vs. requirements.

Spawns an Assistant with a `score` tool and computes per-aspect scores.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from qwen_agent.agents.assistant import Assistant
from qwen_agent.tools.base import BaseTool, register_tool
import json
import json5

llm_config = {
    "model": "qwen-max-latest",
    "model_type": "qwen_dashscope",
    "api_key": ""  # NOTE: prefer setting via environment for security
}

prompt = '''Your are a song evalutating agent, your job is to score a pair of data (the lyrics and the tags) and to check how much they fit a certain requirement. There are five aspects for scoring the data:

- Genre: check how the tags and lyrics fit the genre required in the requirement;
- Time Period: check how the flavor of tags and lyrics fit the corresponding time period;
- Story/Lyric Description: check if the requirement about lyrics (e.g. the story) is satisfied;
- Vocals: check if the tags fits the corresponding vocal requirement;
- Composition: check if the lyric structure fits the composition requirement.

Score all aspect above that appears in the requirement, and don't score those aspects that didn't appear in the requirement. For each aspect, you should score the pair of data zero to ten points, the more the data fits the aspect, the more you should score.

You should use the "score" tool to score the data.
'''

@register_tool("score")
class Score(BaseTool):
    description = "The tool for scoring, input an integer and an aspect to score the piece of data according to the corresponding aspect."
    parameters = [{
        "name": "score",
        "type": "number",
        "description": "The score for the piece of data.",
        "required": True,
    },{
        "name": "aspect",
        "type": "string",
        "description": 'The aspect of scoring, one of the following: "Genre", "Time Period", "Story/Lyric Description", "Vocals" "Composition"',
        "required": True,
    }]
    
    def call(self, params, **kwargs):
        """Record a numeric score for a given aspect in var_dict."""
        obj = json5.loads(params)
        kwargs['var_dict'][obj['aspect']] = int(obj['score'])
        return 'Score successfully set.'

agent = Assistant(
    ["score"],
    llm_config,
    prompt
)

def score_data(data: dict, answer: str) -> tuple[int, str]:
    """Run one scoring session and return collected aspect scores."""
    var_dict = {}
    _ = agent.run_nonstream([{
        'role': 'user',
        'content': f'Requirement: \n{data['raw_text']}\n{answer}'
    }], var_dict=var_dict)
    count = 0
    score = 0
    ret = {}
    for i, j in var_dict.items():
        if i not in label_scores:
            print(f'unexpected aspect {i} appeared')
            continue
        ret[i] = j
        count += 1
        score += j
    if count > 0:
        avg = score / count
        ret['Average'] = avg
        print(f'{data['id']} get an Avg. score of {avg}')
        return ret, data['id']
    print(f'{data['id']} somehow has no score available')
    return {}, data['id']

with open("data.jsonl") as f:
    all_data = [json.loads(i) for i in f]

with open('result.json') as f:
    result = json.load(f)

groups = [
    'demo',
    'control group 1',
    'control group 2',
]

for curr_group in groups:
    count = 0
    label_scores = {
        "Genre",
        "Time Period",
        "Story/Lyric Description",
        "Vocals",
        "Composition",
    }

    scores = {}
    with ThreadPoolExecutor(8) as executor:
        futures = []
        for i in all_data:
            if result.get(i['id'], 0) < 25:
                continue
            path = f'{curr_group}/test_data/lyrics_and_tags/{i['id']}.txt'
            if not os.path.exists(path):
                print(f'{path} was not generated')
                continue
            try:
                with open(path, encoding='utf-8') as f:
                    answer = f.read()
            except UnicodeDecodeError:
                with open(path) as f:
                    answer = f.read()
            futures.append(executor.submit(score_data, i, answer))
        for future in as_completed(futures):
            score, d_id = future.result()
            scores[d_id] = score
            count += 1
            if count % 10 == 0:
                with open(f'score of {curr_group}.json', 'w') as f:
                    json.dump(scores, f)
        with open(f'score of {curr_group}.json', 'w') as f:
            json.dump(scores, f)
        # label_score = {i: sum(j)/len(j) for i, j in label_scores.items() if len(j) > 0}
