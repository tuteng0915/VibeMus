"""VibeMus Gradio UI

Chat-driven interface for song creation/editing, with a shared History panel.
"""

import gradio as gr

from assistant import assistant
from history import (
    ensure_history_storage,
    find_history_entry_by_display,
    log_audio_snapshot,
    read_history_entries,
    seed_default_demo_history,
    seed_outputs_history,
)
from pipeline import pipe
# from qwen_audio import ask_qwen_audio


def _history_dropdown_state(selected=None):
    entries = list(reversed(read_history_entries()))
    choices = [entry['display'] for entry in entries]
    value = None
    if selected and selected in choices:
        value = selected
    elif choices:
        value = choices[0]
    return choices, value


def _history_dropdown_update(selected=None):
    choices, value = _history_dropdown_state(selected)
    return gr.update(choices=choices, value=value), value


def _history_summary_text():
    entries = list(reversed(read_history_entries()))
    if not entries:
        return "_No saved takes yet. Generate your first song to see it here._"
    return "Select any saved take below to preview it, inspect the chat, or restore the session."


def _history_summary_update():
    return gr.update(value=_history_summary_text())


def _history_preview_text(selected_display=None):
    entries = list(reversed(read_history_entries()))
    if not entries:
        return "_No saved takes yet. Generate your first song to see it here._"
    target = None
    if selected_display:
        for entry in entries:
            if entry['display'] == selected_display:
                target = entry
                break
    if not target:
        target = entries[0]
    title = target.get('song_title') or target.get('nickname') or target.get('label') or 'entry'
    duration = target.get('duration')
    prompt_line = target.get('tags', '').splitlines()
    prompt_line = prompt_line[0] if prompt_line else target.get('tags', '')
    lyric_preview = target.get('lyrics', '').splitlines()
    lyric_preview = '\n'.join(lyric_preview[:4])
    meta = target.get('metadata', {})
    meta_bits = []
    if duration:
        meta_bits.append(f"{int(duration)}s")
    if meta.get('source') == 'demo':
        meta_bits.append('demo')
    if meta.get('input_params_path'):
        meta_bits.append(meta['input_params_path'])
    meta_str = ', '.join(meta_bits)
    lines = [f"**{title}** ({target['timestamp']})"]
    if prompt_line:
        lines.append(f"Tags: {prompt_line}")
    if lyric_preview:
        lines.append("Lyrics preview:\n```\n" + lyric_preview + "\n```")
    if meta_str:
        lines.append(f"*{meta_str}*")
    chat_history = target.get('chat_history') or []
    if chat_history:
        snippet = []
        for msg in chat_history[-4:]:
            role = 'User' if msg.get('role') == 'user' else 'Agent'
            content = msg.get('content', '')
            if isinstance(content, list):
                content = '\n'.join(
                    c if isinstance(c, str) else str(c)
                    for c in content
                )
            content = str(content).strip()
            if content:
                snippet.append(f"{role}: {content}")
        if snippet:
            lines.append("Conversation excerpt:\n```\n" + "\n---\n".join(snippet) + "\n```")
    return '\n\n'.join(lines)


def _history_preview_update(selected_display=None):
    return gr.update(value=_history_preview_text(selected_display))


def _history_chatlog_text(selected_display=None):
    entries = list(reversed(read_history_entries()))
    if not entries:
        return "_No chat history stored._"
    target = None
    if selected_display:
        for entry in entries:
            if entry['display'] == selected_display:
                target = entry
                break
    if not target:
        target = entries[0]
    chat_history = target.get('chat_history') or []
    if not chat_history:
        return "_No chat history stored._"
    lines = []
    for msg in chat_history:
        role = 'User' if msg.get('role') == 'user' else 'Agent'
        content = msg.get('content', '')
        if isinstance(content, list):
            content = '\n'.join(
                c if isinstance(c, str) else str(c)
                for c in content
            )
        lines.append(f"{role}: {str(content).strip()}")
    return '\n\n'.join(lines)


def _history_chatlog_update(selected_display=None):
    return gr.update(value=_history_chatlog_text(selected_display))


def _derive_song_title(candidate, lyrics, tags):
    if candidate and candidate.strip():
        return candidate.strip()
    for line in lyrics.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped[:80]
    tag_tokens = [t.strip() for t in tags.split(',') if t.strip()]
    if tag_tokens:
        return f"{tag_tokens[0].title()} Vibe"
    return "Untitled Vibe"


ensure_history_storage()
seed_default_demo_history()
seed_outputs_history()


def run(message, history, prof, aout, lyr, tg, pth, current_title, history_selection, chat_history_state):
    """Chat handler bridging UI and Assistant tools.

    Builds var_dict from UI states, appends user message, streams
    Assistant responses, and returns updated UI states.
    """
    var_dict = {
        'preference': prof,
        'lyrics': lyr,
        'tags': tg,
        'path': pth,
        'title': current_title,
    }
    copy = history.copy()
    user_message = {
        'role': 'user',
        'content': message
    }
    copy.append(user_message)
    response = assistant.run_nonstream(messages=copy, var_dict=var_dict)
    new_lyr = var_dict['lyrics']
    new_tg = var_dict['tags']
    new_aout = var_dict['path']
    new_title = _derive_song_title(var_dict.get('title', ''), new_lyr, new_tg)
    var_dict['title'] = new_title
    dropdown_update = None
    summary_update = None
    title_update = gr.update(value=new_title)
    hist_sel = history_selection or None
    full_history = copy + [{
        'role': 'assistant',
        'content': response
    }]
    if new_aout and new_aout not in ('', 'blank.wav') and new_aout != pth:
        entry = log_audio_snapshot(new_aout, new_lyr, new_tg, song_title=new_title, chat_history=full_history)
        if entry:
            dropdown_update, hist_sel = _history_dropdown_update(entry['display'])
            summary_update = _history_summary_update()
    if dropdown_update is None:
        dropdown_update, hist_sel = _history_dropdown_update(hist_sel)
    if summary_update is None and dropdown_update is not None:
        summary_update = _history_summary_update()
    preview_update = _history_preview_update(hist_sel)
    chatlog_update = _history_chatlog_update(hist_sel)
    return (
        response,
        new_lyr,
        new_tg,
        (new_aout if new_aout != '' else 'blank.wav'),
        new_aout,
        dropdown_update,
        summary_update,
        title_update,
        hist_sel or '',
        preview_update,
        chatlog_update,
        full_history,
    )

custom_css = """
#chat-panel {order: 1;}
#history-panel {order: 2;}
"""

with gr.Blocks(css=custom_css) as demo:
    gr.Markdown("""
    <h1 style='text-align: center; margin-top: 0;'>VibeMus</h1>
    """)
    path_name = gr.State('')
    init_choices, init_value = _history_dropdown_state()
    history_selection_state = gr.State(init_value or '')
    chat_history_state = gr.State([])
    with gr.Row():
        with gr.Column(scale=3):
            lyrics = gr.TextArea(label="lyrics", scale=2, max_lines=100, interactive=True)
            tags = gr.Textbox(label="tags", interactive=True)
            song_title = gr.Textbox(label="Song title", interactive=False, value="")
            generate_btn = gr.Button("Generate")
            length = gr.Slider(30, 300, value=90, step=30, label='length', interactive=True)
            audio_output = gr.Audio(label="audio output", interactive=False)
            with gr.Accordion(label="user preference", open=False):
                audio_input = gr.Audio(sources='upload', label="input preference")
                profile = gr.TextArea(label="profile", interactive=True)
                update_btn = gr.Button("Update Profile")
        with gr.Column(scale=5):
            with gr.Accordion(label="History", open=False, elem_id="history-panel"):
                history_summary = gr.Markdown(value=_history_summary_text(), elem_id="history-summary")
                history_dropdown = gr.Dropdown(
                    label="Saved takes",
                    choices=init_choices,
                    value=init_value,
                    interactive=True,
                )
                history_preview = gr.Markdown(value=_history_preview_text(init_value))
                history_chatlog = gr.TextArea(
                    label="Chat history",
                    value=_history_chatlog_text(init_value),
                    interactive=False,
                    lines=8,
                )
                restore_history_btn = gr.Button("Restore Selected Entry")
            with gr.Column(elem_id="chat-panel"):
                chatbot = gr.ChatInterface(
                    run,
                    type='messages',
                    additional_inputs=[profile, audio_output, lyrics, tags, path_name, song_title, history_selection_state, chat_history_state],
                    additional_outputs=[lyrics, tags, audio_output, path_name, history_dropdown, history_summary, song_title, history_selection_state, history_preview, history_chatlog, chat_history_state],
                    fill_height=True,
                )

    @generate_btn.click(
        inputs=[lyrics, tags, length, song_title, history_selection_state, chat_history_state],
        outputs=[audio_output, path_name, history_dropdown, history_summary, song_title, history_selection_state, history_preview, history_chatlog, chat_history_state],
    )
    def generate_music(lyr, tg, lth, current_title, history_selection, chat_history):
        """Run ACE-Step pipeline to synthesize audio from tags/lyrics."""
        outputs = pipe(
            format='wav',
            audio_duration=lth,
            prompt=tg,
            lyrics=lyr,
        )
        title_text = _derive_song_title(current_title, lyr, tg)
        entry = log_audio_snapshot(outputs[0], lyr, tg, duration=lth, song_title=title_text, chat_history=chat_history or [])
        dropdown_update, hist_sel = _history_dropdown_update(entry['display'] if entry else history_selection)
        summary_update = _history_summary_update()
        title_update = gr.update(value=title_text)
        preview_update = _history_preview_update(hist_sel)
        chatlog_update = _history_chatlog_update(hist_sel)
        return outputs[0], outputs[0], dropdown_update, summary_update, title_update, hist_sel or '', preview_update, chatlog_update, chat_history or []

    @history_dropdown.change(inputs=[history_dropdown], outputs=[history_selection_state, history_preview, history_chatlog])
    def on_history_select(selected):
        if not selected:
            return '', _history_preview_update(), _history_chatlog_update()
        return selected, _history_preview_update(selected), _history_chatlog_update(selected)

    @restore_history_btn.click(inputs=[history_dropdown], outputs=[lyrics, tags, audio_output, path_name, song_title, chat_history_state])
    def load_history(selected):
        """Load lyrics/tags/audio from a saved history entry."""
        if not selected:
            return gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update()
        entry = find_history_entry_by_display(selected)
        if not entry:
            return gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update()
        audio_path = entry['audio_path']
        return (
            entry['lyrics'],
            entry['tags'],
            audio_path,
            audio_path,
            gr.update(value=entry.get('song_title', '')),
            entry.get('chat_history', []),
        )

    @update_btn.click(inputs=[audio_input, chatbot, lyrics, tags, profile], outputs=profile)
    def baz(audio, chat, lyr, tg, old_profile):
        """Placeholder for preference extraction from audio/chat (future)."""
        return "placeholder"

    # gr.Markdown("# Test")

demo.launch(server_name='0.0.0.0',
            server_port=7860,
            share=False)
