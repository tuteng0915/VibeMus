"""Tool implementations for VibeMus Assistant.

Defines tool functions the Assistant can call to read preferences,
set parameters, transcribe audio, and perform repaint/edit/extend/clip.
"""

import json5
import logging
from qwen_agent.tools.base import BaseTool, register_tool
from pipeline import pipe
import whisper_timestamped as wsp
from pydub import AudioSegment

logger = logging.getLogger(__name__)

wsp_model = wsp.load_model("medium")  # loaded once; used by transcriptor
all_tools = [
    'preference',
    'param_setter',
    'transcriptor',
    'repaint_song',
    'extend_song',
    'edit_song',
    'clip_song',
]

def _textify(value):
    """Best-effort convert UI/tool inputs into a plain string."""
    if value is None:
        return ''
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple, set)):
        parts = [part for part in (_textify(v).strip() for v in value) if part]
        return '\n'.join(parts)
    if isinstance(value, dict):
        try:
            return json5.dumps(value, ensure_ascii=False)
        except Exception:
            return str(value)
    return str(value)


def _ensure_plaintext(value, field_name='value'):
    text = _textify(value)
    if not isinstance(text, str):
        try:
            text = str(text)
        except Exception:
            logger.warning("Failed to stringify %s (type=%s); defaulting to empty string", field_name, type(value).__name__)
            text = ''
    return text


@register_tool('preference')
class GetPreference(BaseTool):
    description = 'getting the user preference'
    def call(self, params, **kwargs) -> str:
        """Return user's preference text provided in UI state."""
        pref = kwargs['var_dict']['preference']
        if not pref or pref.isspace():
            return 'the user has not given their preferences yet.'
        return pref

@register_tool('param_setter')
class SetParam(BaseTool):
    description = 'setting a parameter of the song, including the tags, the lyrics, or the title'
    parameters = [{
        'name': 'name',
        'type': 'string',
        'description': 'the name of the parameter, either "tags", "lyrics", or "title"',
        'required': True
    },{
        'name': 'value',
        'type': 'string',
        'description': 'the value of the parameter',
        'required': True
    }]

    def call(self, params, **kwargs) -> str:
        """Set `tags` or `lyrics` field in var_dict."""
        obj = json5.loads(params)
        kwargs['var_dict'][obj['name']] = _ensure_plaintext(obj['value'], obj['name'])
        return f'Successfully set the parameter {obj["name"]}'

@register_tool('transcriptor')
class Transcriptor(BaseTool):
    description = 'returns the current lyrics and current song file\'s transcription with time spots of the beginning and ending of each word, marked as <|start_time|>word<|end_time|>'
    parameters = []

    def call(self, params, **kwargs) -> str:
        """Transcribe current audio file and return timestamps + lyrics."""
        result = wsp.transcribe(wsp_model, kwargs['var_dict']['path'])
        return '### Lyrics\n\n'\
            + kwargs['var_dict']['lyrics']\
            + '\n### Transcription with timestamps\n\n'\
            + '\n'.join(
                ''.join(
                    f'<|{i["start"]}|>{i["text"]}<|{i["end"]}|>'
                    for i in j['words']
                )
                for j in result['segments']
            )

@register_tool('repaint_song')
class SongRepaint(BaseTool):
    description = 'AI song repainting service, input the repainting duration to retake the desired part'
    parameters = [{
        'name': 'start',
        'type': 'number',
        'description': 'the beginning time spot of the repainting, in seconds',
        'required': True,
    },{
        'name': 'end',
        'type': 'number',
        'description': 'the ending time spot of the repainting, in seconds',
        'required': True,
    }]

    def call(self, params: str, **kwargs) -> str:
        """Repaint a segment [start, end] using current tags/lyrics."""
        obj = json5.loads(params)
        start = obj['start']
        end = obj['end']
        var_dict = kwargs['var_dict']
        curr_path = var_dict['path']
        lyrics = _ensure_plaintext(var_dict.get('lyrics'), 'lyrics')
        tags = _ensure_plaintext(var_dict.get('tags'), 'tags')
        repaint_out = pipe(
            task='repaint',
            src_audio_path=curr_path,
            repaint_start=start,
            repaint_end=end,
            lyrics=lyrics,
            prompt=tags,
        )
        var_dict['path'] = repaint_out[0]
        return 'Successfully repainted.'

@register_tool('edit_song')
class SongEdit(BaseTool):
    description = 'AI song editing service, apply localized lyric changes or full-blown melody/style (tags) changes.'
    parameters = []

    def call(self, params, **kwargs):
        """Full-track edit using current tags/lyrics at same duration."""
        var_dict = kwargs['var_dict']
        curr_path = var_dict['path']
        if curr_path == '' or curr_path == 'blank.wav':
            return 'The song is not generated yet, so this tool is currently not available.'
        lyrics = _ensure_plaintext(var_dict.get('lyrics'), 'lyrics')
        length = AudioSegment.from_file(curr_path).duration_seconds
        tags = _ensure_plaintext(var_dict.get('tags'), 'tags')
        try:
            edit_out = pipe(
                task='edit',
                src_audio_path=curr_path,
                edit_target_lyrics=lyrics,
                edit_target_prompt=tags,
                audio_duration=length,
            )
        except ValueError as exc:
            logger.error("edit_song received unsupported text payloads (lyrics_type=%s, tags_type=%s)", type(lyrics).__name__, type(tags).__name__)
            return f'edit failed: {exc}'
        var_dict['path'] = edit_out[0]
        return 'Successfully edited.'

@register_tool('extend_song')
class SongExtend(BaseTool):
    description = 'AI song extending service, can extend the song at either the front or the back, or both'
    parameters = [{
        'name': 'front',
        'type': 'number',
        'description': 'amount of time added at the front, in seconds, 0 if no extention at the front',
        'required': True,
    },{
        'name': 'back',
        'type': 'number',
        'description': 'amout of time added at the back, in seconds, 0 if no extention at the back',
        'required': True,
    }]

    def call(self, params, **kwargs):
        """Extend audio by adding time to front/back; asserts limits."""
        var_dict = kwargs['var_dict']
        obj = json5.loads(params)
        curr_path = var_dict['path']
        lyrics = _ensure_plaintext(var_dict.get('lyrics'), 'lyrics')
        tags = _ensure_plaintext(var_dict.get('tags'), 'tags')
        length = AudioSegment.from_file(curr_path).duration_seconds
        try:
            extend_out = pipe(
                task='extend',
                src_audio_path=curr_path,
                repaint_start=int(-obj['front']),
                repaint_end=int(length+obj['back']),
                lyrics=lyrics,
                audio_duration=int(length+obj['back'])+int(obj['front']),
                prompt=tags,
            )
        except AssertionError as e:
            return 'extention failed, the extention length can\'t be longer than the length of the song itself'
        var_dict['path'] = extend_out[0]
        return 'Successfully extended.'

@register_tool('clip_song')
class SongClip(BaseTool):
    description = 'song clipping service, input the beginning and ending timespot to clip the song'
    parameters = [{
        'name': 'begin',
        'type': 'number',
        'description': 'beginning of the clipping, in seconds',
        'required': True,
    },{
        'name': 'end',
        'type': 'number',
        'description': 'ending of the clipping, in seconds',
        'required': True,
    }]

    def call(self, params, **kwargs):
        """Clip current audio to [begin, end] seconds and update path."""
        var_dict = kwargs['var_dict']
        obj = json5.loads(params)
        curr_path = var_dict['path']
        clipped_path = curr_path.rsplit('.')[0]+'_clipped'+'.wav'
        AudioSegment.from_file(
            curr_path
        )[int(obj['begin'] * 1000):int(obj['end'] * 1000)].export(
            clipped_path
        )
        var_dict['path'] = clipped_path
        return 'Successfully clipped.'
