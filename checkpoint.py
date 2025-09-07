"""Utility script to pre-download ACE-Step checkpoints via HF Hub."""

from huggingface_hub import snapshot_download

checkpoint_dir = snapshot_download("ACE-Step/ACE-Step-v1-3.5B")

print(f"Checkpoints downloaded to: {checkpoint_dir}")
