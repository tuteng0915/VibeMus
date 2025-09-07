"""Minimal Whisper-timestamped transcribe smoke test."""

import whisper_timestamped as wsp

model = wsp.load_model("medium")

result = wsp.transcribe(model, "./outputs/output_20250802150944_0.wav")  # example path

print(result)
