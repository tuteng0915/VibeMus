"""ACE-Step quick test: generate and extend audio examples."""

from pipeline import pipe
#from qwen_audio import ask_qwen_audio
with open('./example_lyrics.txt') as f:
    lyrics = f.read()

with open('./example_tags.txt') as f:
    tags = f.read()
'''
result = pipe(
    format='wav',
    audio_duration=32,
    prompt=tags,
    lyrics=lyrics,
)

filepath = result[0]
'''
filepath = './outputs/output_20250802145351_0.wav'  # example output path
'''
text = "please generate tags of the song, as many as possible."

print(ask_qwen_audio(filepath, text))
'''
result = pipe(
    task='extend',
    audio_duration=49.0,
    prompt=tags,
    lyrics=lyrics,
    repaint_start=0,
    repaint_end=49.0,
    src_audio_path=filepath
)


