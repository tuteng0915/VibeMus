"""Tools for control group 2 (experiment)."""

import json5
from qwen_agent.tools.base import BaseTool, register_tool
from pydub import AudioSegment

# wsp_model = wsp.load_model("medium")
all_tools = [
    'preference',
    'param_setter',
    'transcriptor',
    'repaint_song',
    'extend_song',
    'edit_song',
    'clip_song',
]

@register_tool('preference')
class GetPreference(BaseTool):
    description = 'getting the user preference'
    def call(self, params, **kwargs) -> str:
        """Return user's preference text (experiment)."""
        pref = kwargs['var_dict']['preference']
        if not pref or pref.isspace():
            return 'the user has not given their preferences yet.'
        return pref

@register_tool('param_setter')
class SetParam(BaseTool):
    description = 'setting a parameter of the song, including the tags and the lyrics'
    parameters = [{
        'name': 'name',
        'type': 'string',
        'description': 'the name of the parameter, either "tags" or "lyrics"',
        'required': True
    },{
        'name': 'value',
        'type': 'string',
        'description': 'the value of the parameter',
        'required': True
    }]

    def call(self, params, **kwargs) -> str:
        """Set `tags` or `lyrics` (experiment)."""
        obj = json5.loads(params)
        kwargs['var_dict'][obj['name']] = obj['value']
        return f'Successfully set the parameter {obj["name"]}'

@register_tool('transcriptor')
class Transcriptor(BaseTool):
    description = 'returns the current lyrics and current song file\'s transcription with time spots of the beginning and ending of each word, marked as <|start_time|>word<|end_time|>'
    parameters = []

    def call(self, params, **kwargs) -> str:
        '''
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
        '''
        return 'this tool is currently not available'

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
        '''
        obj = json5.loads(params)
        start = obj['start']
        end = obj['end']
        var_dict = kwargs['var_dict']
        curr_path = var_dict['path']
        lyrics = var_dict['lyrics']
        tags = var_dict['tags']
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
        '''
        return 'this tool is currently not available'

@register_tool('edit_song')
class SongEdit(BaseTool):
    description = 'AI song editing service, apply localized lyric changes or full-blown melody/style (tags) changes.'
    parameters = []

    def call(self, params, **kwargs):
        '''
        var_dict = kwargs['var_dict']
        curr_path = var_dict['path']
        lyrics = var_dict['lyrics']
        length = AudioSegment.from_file(curr_path).duration_seconds
        tags = var_dict['tags']
        edit_out = pipe(
            task='edit',
            src_audio_path=curr_path,
            edit_target_lyrics=lyrics,
            edit_target_prompt=tags,
            audio_duration=length,
        )
        var_dict['path'] = edit_out[0]
        return 'Successfully edited.'
        '''
        return 'this tool is currently not available'

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
        '''
        var_dict = kwargs['var_dict']
        obj = json5.loads(params)
        curr_path = var_dict['path']
        lyrics = var_dict['lyrics']
        tags = var_dict['tags']
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
        '''
        return 'this tool is currently not available'

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
