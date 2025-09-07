"""ACE-Step pipeline bootstrap.

Creates a global `pipe` used by the UI and tools for music generation
and localized edits. Adjust device/dtype for your hardware as needed.
"""

from acestep.pipeline_ace_step import ACEStepPipeline

pipe = ACEStepPipeline(
    device_id=0,          # GPU device index
    dtype="bfloat16",     # prefer bf16 on recent GPUs
    torch_compile=True,   # enable PyTorch compile for speed
)
