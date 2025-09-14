import os
from pipeline import pipe

selections = [
    'bmerqe.txt',
    'pd1qwq.txt',
    'pqhby2.txt',
]

DEMO_DIALOG_DIR = os.path.join('experiments', 'demo', 'test_data', 'dialogs')
DEMO_LT_DIR = os.path.join('experiments', 'demo', 'test_data', 'lyrics_and_tags')

for i, sel in enumerate(selections):
    tags = []
    lyrics = []
    curr = tags
    with open(os.path.join(DEMO_LT_DIR, sel)) as f:
        for line in f:
            l = line.strip()
            if l == 'Tags :':
                continue
            if l == 'Lyrics :':
                curr = lyrics
                continue
            curr.append(line)
    result = pipe(
        format='wav',
        audio_duration=60,
        prompt='\n'.join(tags),
        lyrics='\n'.join(lyrics),
    )

    filepath = result[0]
    
    print(i, filepath)