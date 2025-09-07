# VibeMus

**🎵 Compose Music with Natural Language | 🤖 LLM-powered Music Generation Interface | 🚀 Lower the Barrier to AI Music Creation**

[![Project License](https://img.shields.io/badge/license-[License]-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)]()



## ✨ Introduction

`VibeMus` is an innovative demo project designed to...  **TODO**

1. **🎯 Intelligent User Profiling:** The LLM engages in natural dialogue with the user to understand their musical preferences (such as genre, mood, tempo, instrument preferences), creative intentions (e.g., "write a song for my cute cat" or "compose a sad folk song"), and skill level (beginner or professional musician), dynamically building a user profile.
2. **🗣️ Natural Language Command Parsing:** Users can describe the music they want using everyday language (e.g., "some relaxing jazz with a sax solo, slower tempo" or "speed up the melody just generated, add drums, make it more intense"). The LLM accurately parses these vague or complex requests.
3. **🔧 Atomic Operation Instruction Generation:** The parsed user intent is transformed by the LLM into a series of precise, executable **atomic operation instructions**. These instructions are low-level commands or parameter combinations that underlying music generation models (such as MusicLM, Riffusion, MAGNeT, or custom models) can directly understand and process.
4. **🎼 Seamless Driving of Music Generation Models:** The generated atomic instructions are sent to one or more backend music generation models for execution, and the resulting music fragments are returned to the user.
5. **⏱️ Iterative Creation:** Users can give feedback on the generated results ("make the drums stronger", "change the chord progression"), the LLM understands the feedback and generates new operation instructions, forming a creative loop.

**Core Idea:** Abstract complex and professional music generation parameters and operations, allowing users to **focus on creative expression** without needing to understand the technical details of underlying models or tedious parameter adjustments. The LLM acts as a music-savvy, tech-savvy "intelligent assistant" and "translator".

## 🖥 Showcase (Screenshots / GIFs / Video)

**TODO**

*  Screenshot
*  Video
*  Audio sample links


## 🚀 Getting Started

### Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/tuteng0915/VibeMus.git
    cd VibeMus
    ```

2. **(Recommended) Create and activate virtual environment:**
    ```bash
    conda create -n vibemus python=3.10
    conda activate vibemus
    ```

3. **Install dependencies:**
    ```bash
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    pip install -r requirements.txt
    pip install transformers==4.51.0
    ```

### Run

```bash
python main.py
```

## Demonstration




## 🔐 Configuration & Secrets

- Required environment variable: set `DASHSCOPE_API_KEY` for Qwen via DashScope.
- Create a local `.env` file (already gitignored) at the project root:
  
  ```bash
  echo DASHSCOPE_API_KEY=your_dashscope_api_key_here > .env
  ```
- The app loads `.env` automatically and prefers the environment variable over any file content; JSON config files (`agent_llm_config.json`, `user_llm_config.json`) keep `api_key` empty by default to avoid committing secrets.
- Never commit real API keys into the repository or screenshots/logs that reveal them.

## 🧰 Environment & Prerequisites

- Python: 3.10+
- OS: Linux / Windows / macOS (Linux/Windows recommended)
- GPU: NVIDIA GPU recommended; default config uses `CUDA 11.8` + `bfloat16` + `torch.compile`.
  - Driver & CUDA: ensure `nvidia-smi` works and CUDA matches your PyTorch build (examples use `cu118`).
  - VRAM: 8 GB minimum recommended; 16 GB+ preferred depending on task length.
- FFmpeg: required by `pydub` and `whisper-timestamped` and must be in PATH.
  - Ubuntu/Debian: `sudo apt-get install -y ffmpeg`
  - macOS (Homebrew): `brew install ffmpeg`
  - Windows (Chocolatey): `choco install ffmpeg`

## 🌍 Environment Variables

- Required:
  - `DASHSCOPE_API_KEY`: API key for Qwen via DashScope.
- Optional (caching/performance):
  - `HF_HOME` or `TRANSFORMERS_CACHE`: Hugging Face cache dir (default `~/.cache/huggingface`).
  - `TORCH_HOME`: PyTorch cache dir (default `~/.cache/torch`).
  - `HTTP_PROXY` / `HTTPS_PROXY`: set if you require a proxy.

How to set:

- `.env` file (recommended): create at project root (gitignored)
  - Example line: `DASHSCOPE_API_KEY=your_dashscope_api_key_here`
- Bash/zsh (Linux/macOS):
  - `export DASHSCOPE_API_KEY=...`
- PowerShell (Windows):
  - `setx DASHSCOPE_API_KEY "your_key_here"`
- CMD (Windows):
  - `setx DASHSCOPE_API_KEY your_key_here`

## 📦 Model Downloads & Caches

On first use, required models/weights will be downloaded automatically. Ensure network access and sufficient disk space:

- Whisper (timestamped) model: `medium` (~1.4 GB), used for transcription with timestamps.
- ACE-Step weights: pulled by `ace_step` pipeline on first invocation, typically multiple GB depending on sub-models and tasks.
- Optional (not used in default main flow): `Qwen/Qwen-Audio-Chat` if enabling `qwen_audio.py`, also multi-GB.

Cache locations:

- Hugging Face: `~/.cache/huggingface` (or as set by `HF_HOME`/`TRANSFORMERS_CACHE`)
- PyTorch: `~/.cache/torch` (or as set by `TORCH_HOME`)
- Whisper: under user cache; also influenced by HF/TRANSFORMERS cache envs

Offline/intranet: pre-download on a connected machine, then copy cache dirs to target and point env vars to the copied paths.

## 🩺 Troubleshooting

- FFmpeg not found: install and ensure it is on PATH (see commands above).
- CUDA/driver mismatch: verify `nvidia-smi` works and PyTorch CUDA build matches your driver (example uses `cu118`).
- Out of VRAM: reduce generation duration, or in `pipeline.py` change `dtype` from `bfloat16` to `float16` and disable `torch_compile` for broader compatibility.
- Missing API key: LLM-backed chat and auto tags/lyrics need `DASHSCOPE_API_KEY`; or manually provide tags/lyrics and click Generate.
