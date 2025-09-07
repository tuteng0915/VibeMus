"""VibeMus Gradio UI

Chat-driven interface for song creation/editing and a demo preview panel.
"""

import gradio as gr
from pipeline import pipe
# from qwen_audio import ask_qwen_audio
from assistant import assistant
import os

# Constants
# Directory containing curated example dialogs for quick preview in UI
DEMO_DIALOG_DIR = os.path.join('experiments', 'demo', 'test_data', 'dialogs')

def run(message, history, prof, aout, lyr, tg, pth):
    """Chat handler bridging UI and Assistant tools.

    Builds var_dict from UI states, appends user message, streams
    Assistant responses, and returns updated UI states.
    """
    var_dict = {
        'preference': prof,
        'lyrics': lyr,
        'tags': tg,
        'path': pth,
    }
    copy = history.copy()
    copy.append({
        'role': 'user',
        'content': message
    })
    for response in assistant.run(messages=copy, var_dict=var_dict):
        ...
    new_lyr = var_dict['lyrics']
    new_tg = var_dict['tags']
    new_aout = var_dict['path']
    return response, new_lyr, new_tg, (new_aout if new_aout != '' else 'blank.wav'), new_aout

with gr.Blocks() as demo:
    gr.Markdown("""
    <h1 style='text-align: center; margin-top: 0;'>VibeMus</h1>
    """)
    path_name = gr.State('')
    with gr.Row():
        with gr.Column(scale=3):
            lyrics = gr.TextArea(label="lyrics", scale=2, max_lines=100, interactive=True)
            tags = gr.Textbox(label="tags", interactive=True)
            generate_btn = gr.Button("Generate")
            length = gr.Slider(30, 300, step=1, label='length', interactive=True)
            audio_output = gr.Audio(label="audio output", interactive=False)
            with gr.Accordion(label="user preference", open=False):
                audio_input = gr.Audio(sources='upload', label="input preference")
                profile = gr.TextArea(label="profile", interactive=True)
                update_btn = gr.Button("Update Profile")
        with gr.Column(scale=5):
            # chatbot = gr.Textbox(label="chatbot")
            chatbot = gr.ChatInterface(
                run,
                type='messages',
                additional_inputs=[profile, audio_output, lyrics, tags, path_name],
                additional_outputs=[lyrics, tags, audio_output, path_name],
                fill_height=True
            )

            with gr.Accordion(label="Demo", open=False):
                # Pick a few curated example dialogs from the demo folder
                example_files = [
                    '6ab6c3.txt',
                    '7drj58.txt',
                    '8eelke.txt',
                    '73s98e.txt',
                    'd69w40.txt',
                ]
                def _existing_examples():
                    return [f for f in example_files if os.path.exists(os.path.join(DEMO_DIALOG_DIR, f))]

                demo_choice = gr.Dropdown(label='Select example dialog', choices=_existing_examples(), interactive=True)
                load_demo_btn = gr.Button('Load Example')
                demo_view = gr.TextArea(label='Example preview', value='', interactive=False, lines=18)

                @load_demo_btn.click(inputs=[demo_choice], outputs=[demo_view])
                def load_demo(selected):
                    if not selected:
                        return 'No example selected.'
                    path = os.path.join(DEMO_DIALOG_DIR, selected)
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            return f.read()
                    except Exception as e:
                        return f'Failed to load example: {e}'

    @generate_btn.click(inputs=[lyrics, tags, length], outputs=[audio_output, path_name])
    def generate_music(lyr, tg, lth):
        """Run ACE-Step pipeline to synthesize audio from tags/lyrics."""
        outputs = pipe(
            format='wav',
            audio_duration=lth,
            prompt=tg,
            lyrics=lyr,
        )
        # print(outputs)
        return outputs[0], outputs[0]

    @update_btn.click(inputs=[audio_input, chatbot, lyrics, tags, profile], outputs=profile)
    def baz(audio, chat, lyr, tg, old_profile):
        """Placeholder for preference extraction from audio/chat (future)."""
        return "placeholder"

    # gr.Markdown("# Test")

demo.launch(share=True, server_name='0.0.0.0')

