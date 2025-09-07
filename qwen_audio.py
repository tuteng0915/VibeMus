"""Optional Qwen Audio-Chat helper.

Provides a simple wrapper `ask_qwen_audio` to query Qwen with audio+text.
Not used by default in the main UI.
"""

from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation import GenerationConfig
import torch

tokenizer = AutoTokenizer.from_pretrained(
    "Qwen/Qwen-Audio-Chat",
    trust_remote_code=True,
)

model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen-Audio-Chat",
    device_map="cuda",
    trust_remote_code=True,
)

def ask_qwen_audio(audio, text):
    """Ask Qwen Audio-Chat with an audio path/bytes and a text prompt."""
    query = tokenizer.from_list_format([
        {'audio': audio},
        {'text': text},
    ])

    response, history = model.chat(tokenizer, query=query, history=None)
    return response
