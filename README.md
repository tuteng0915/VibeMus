# VibeMus

**🎵 Compose Music with Natural Language | 🤖 LLM-powered Music Generation Interface | 🚀 Lower the Barrier to AI Music Creation**

[![Project License](https://img.shields.io/badge/license-[License]-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)]()



## ✨ Introduction

`VibeMus` is an innovative demo project designed to...

1. **🎯 Intelligent User Profiling:** The LLM engages in natural dialogue with the user to understand their musical preferences (such as genre, mood, tempo, instrument preferences), creative intentions (e.g., "write a song for my cute cat" or "compose a sad folk song"), and skill level (beginner or professional musician), dynamically building a user profile.
2. **🗣️ Natural Language Command Parsing:** Users can describe the music they want using everyday language (e.g., "some relaxing jazz with a sax solo, slower tempo" or "speed up the melody just generated, add drums, make it more intense"). The LLM accurately parses these vague or complex requests.
3. **🔧 Atomic Operation Instruction Generation:** The parsed user intent is transformed by the LLM into a series of precise, executable **atomic operation instructions**. These instructions are low-level commands or parameter combinations that underlying music generation models (such as MusicLM, Riffusion, MAGNeT, or custom models) can directly understand and process.
4. **⏱️ Iterative Creation:** Users can give feedback on the generated results ("make the drums stronger", "change the chord progression"), the LLM understands the feedback and generates new operation instructions, forming a creative loop.

**Core Idea:** Abstract complex and professional music generation parameters and operations, allowing users to **focus on creative expression** without needing to understand the technical details of underlying models or tedious parameter adjustments. The LLM acts as a music-savvy, tech-savvy "intelligent assistant" and "translator".

## 🧩 Running Modes

- **Gradio UI (default):** `python main.py` launches the full chat interface. Every time you hit **Generate** or the assistant produces new audio, the take is automatically copied into `history/` and becomes selectable via the History dropdown.
- **Backend-only API:** `python backend_server.py` (or `uvicorn backend_server:app --host 0.0.0.0 --port 8000`) exposes a FastAPI service for headless deployments. Key endpoints:
  - `POST /api/chat` – mirrors the chat workflow; send `{message, history, preference, lyrics, tags, path}` and get the assistant reply plus updated song state.
  - `POST /api/generate` – generate audio directly from `{lyrics, tags, length}`.
  - `GET /api/history` / `GET /api/history/{id}` / `GET /api/history/{id}/audio` – enumerate or download past takes; everything shares the same storage as the UI History panel.
- **Unified History panel:** The UI and backend now share a single History list (prefilled with the demo songs). Each take is auto-titled by the assistant (title + timestamp), and you can reload the full state (lyrics, tags, audio), view the chat transcript that produced it, and keep iterating from any saved point.
- **Outputs integration:** All audio files (demos, previously generated outputs, and new takes) are copied into `history/audio/` along with links to their `_input_params.json`, so the History panel fully owns the artifacts it previews and restores.

## 🖥 Showcase (Screenshots / GIFs / Video)

### Example 1

[Click to listen to the generated song](/selections/bmerqe.wav)

dialog:

```
User : 
I need a song that starts with an old man in a hospital bed, and then a woman comes in singing "Do you remember" with a marching band. It should have flashbacks and be like Florence and the Machine.
Agent : 
Sure, I can help with that. Let's break down the elements you've mentioned to create a fitting song.

1. **Starting Scene**: An old man in a hospital bed.
2. **Entry and Singing**: A woman enters singing "Do you remember" accompanied by a marching band.
3. **Flashbacks**: The song should evoke a sense of nostalgia or memory recall.
4. **Style**: Resembling Florence and the Machine.

First, let's set some tags that align with your vision, particularly focusing on creating a soundscape that is evocative and rich, akin to Florence and the Machine, but also incorporating elements of a marching band for that powerful entrance.

I will now gather more specific preferences and then set the initial tags and lyrics structure.


the user has not given their preferences yet.
It seems we need to define some more specific details about the style and mood you're aiming for. Florence and the Machine are known for their powerful, ethereal sound with strong vocal performances and a rich orchestration.

Do you have any preferences on:
- The theme or emotion of the song (e.g., melancholic, uplifting, bittersweet)?
- Specific instruments besides the marching band elements?
- Any particular tempo or key?

Let me know how you'd like to proceed.
User : 
I think the song should feel bittersweet, with a powerful and ethereal sound. Maybe include some piano and strings along with the marching band. The tempo can be moderate, not too fast or slow.
Agent : 

Successfully set the parameter tags
Great! I've set the tags for your song to reflect a bittersweet, powerful, and ethereal sound with piano, strings, marching band elements, and a moderate tempo inspired by Florence and the Machine.

Now, let's draft the initial lyrics structure. Here’s what we can start with:

- **[Verse]**: Setting the scene with the old man in the hospital bed.
- **[Chorus]**: The woman enters singing "Do you remember," evoking flashbacks.
- **[Bridge]**: A flashback sequence capturing key moments or emotions.

Let me know if there's anything specific you'd like included in these sections or any other changes before finalizing the lyrics draft.


Successfully set the parameter lyrics
The lyrics have been set with your specified themes and imagery. Here's the draft:

- **[Verse]**:  
  In the quiet room where shadows play,  
  An old man lies, his hair turned gray.  
  Memories flicker, like lights that fade,  
  Within the walls where time has stayed.  

- **[Chorus]**:  
  Do you remember, the days gone by?  
  When dreams were young and spirits high.  
  With every note, her voice takes flight,  
  A marching band ignites the night.  

- **[Bridge]**:  
  Flashbacks dance, of laughter sweet,  
  Of battles fought and hearts that beat.  
  Through fields of gold, through stormy weather,  
  Moments cherished, binding us forever.  

Please review this draft and let me know if there are any changes or additions you'd like to make.

Once you're ready, press the "generate" button to manually create the song.
User : 
The lyrics look good, but can we add something about dancing on a hillside in the bridge? Other than that, I think it's perfect.
Agent : 

Successfully set the parameter lyrics
I've updated the lyrics to include "Dancing on a hillside under skies so wide" in the bridge section. Here's the revised version:

- **[Verse]**:  
  In the quiet room where shadows play,  
  An old man lies, his hair turned gray.  
  Memories flicker, like lights that fade,  
  Within the walls where time has stayed.  

- **[Chorus]**:  
  Do you remember, the days gone by?  
  When dreams were young and spirits high.  
  With every note, her voice takes flight,  
  A marching band ignites the night.  

- **[Bridge]**:  
  Flashbacks dance, of laughter sweet,  
  Of battles fought and hearts that beat.  
  Dancing on a hillside under skies so wide,  
  Through fields of gold, through stormy weather,  
  Moments cherished, binding us forever.  

The lyrics now capture the additional imagery you requested.

Once you're ready, press the "generate" button to manually create the song.
User : 

Successfully halted.
I think the song is perfect now. I'll press the "generate" button to create it. Thank you!
```

### Example 2

[Click to listen to the generated song](/selections/pd1qwq.wav)

dialog:

```
User : 
I'm thinking of a mellow pop or R&B song, something that could be from the 90s to today. Can we start with that vibe?
Agent : 
Sure, I can help with that. Let's set the tags for a mellow pop/R&B song with a 90s to today vibe. I'll go ahead and set those parameters now.



Successfully set the parameter tags
Great! We've set the tags for a mellow pop or R&B song with a 90s to contemporary vibe. Now, let's work on some lyrics. Do you have any specific themes or topics in mind for the song? For example, love, nostalgia, heartbreak, or perhaps something more upbeat like celebration or empowerment?
User : 
The theme should be reflective, maybe about missing someone or something. Could we get a chorus that starts with "The one I'm missing is you"?
Agent : 
Certainly! We'll create a reflective theme around missing someone, with the chorus starting as you've suggested. Let's draft some initial lyrics for the song.



Successfully set the parameter lyrics
We've crafted some reflective lyrics with a chorus that starts with "The one I'm missing is you." Here's what we have so far:

```
[chorus]
The one I'm missing is you
In every moment, in all I do
I feel your absence anew
Wishing you were here, too

[verse]
Walking down these lonely streets
Memories linger where we used to meet
Every corner holds a trace of you
A silhouette against the sky so blue

[bridge]
Time moves on, but it doesn't heal
The void remains, an open seal
Hoping someday our paths will cross again
Until then, my heart won't settle or bend
```

When you're ready, press the "generate" button to manually generate the song. Let me know if there are any other changes or additions you'd like to make before then!
User : 
This is a good start, but can we add some backing vocals? Maybe soft harmonies or repeating "yeah, yeah, yeah, yeah" in the background during the chorus?
Agent : 

Successfully set the parameter tags
I've updated the tags to include backing vocals with soft harmonies and a "yeah, yeah, yeah, yeah" background during the chorus. 

Now that we have the tags and lyrics set, when you're ready, press the "generate" button to manually generate the song. Would you like to make any more adjustments before generating?
User : 
That sounds perfect. Can we also include an instrument like a xylophone or marimba for a unique touch?
Agent : 

Successfully set the parameter tags
I've added the xylophone and marimba to our tags to give the song a unique instrumental touch. 

We're all set with the lyrics and updated tags for your reflective pop/R&B song. Go ahead and press the "generate" button whenever you're ready to create the song. If you think of anything else, feel free to let me know!
User : 

Successfully halted.
I think we're all set. Let's generate the song with these elements. Thank you for your help!
```

### Example 3

[Click to listen to the generated song](/selections/pqhby2.wav)

dialog:

```
User : 
I'd like to create an epic metal song with orchestral elements and intense parts. Can we start working on that?
Agent : 
Sure, I can help with that. To make sure I understand your preferences correctly, could you please specify any particular themes or emotions you want the song to convey? Also, do you have a preference for the tempo or any specific instruments you'd like to feature?

Let's also check your general preferences to ensure we align with your tastes.


the user has not given their preferences yet.
Since I don't have your specific preferences on file, could you provide some additional details? For instance, do you prefer a faster or slower tempo in your epic metal songs? Are there any specific instruments or vocal styles you enjoy?

Once I have a clearer picture, I'll generate the tags and lyrics for your epic metal song with orchestral elements.
User : 
The song should paint a picture of a snowy forest, solitude, and contrast. It needs to start emotional and build up to an explosive climax. And yes, faster tempo with powerful drums and soaring strings would be great.
Agent : 

Successfully set the parameter tags
Great! I've set the tags for your epic metal song to include orchestral elements, a fast tempo, powerful drums, soaring strings, and themes of a snowy forest, solitude, contrast, emotional depth, and an explosive climax.

Now, let's work on the lyrics. I'll create a structure with verses, choruses, and a bridge to build up the story and emotion.


Successfully set the parameter lyrics
I've crafted the lyrics for your epic metal song. Here's a preview:

[verse]
In the heart of winter's embrace,
A lone wolf howls, lost in space.
Snowflakes fall, silent and cold,
Solitude's tale, never told.

[chorus]
Rise from the ashes, soar so high,
Beneath the stormy sky.
Feel the thunder, hear the cry,
Of battles we cannot deny.

[verse]
Contrasts collide in frosty air,
Shadows dance without a care.
Whispers of warmth in icy veins,
A fleeting moment, love remains.

[chorus]
Rise from the ashes, soar so high,
Beneath the stormy sky.
Feel the thunder, hear the cry,
Of battles we cannot deny.

[bridge]
The calm before the storm arrives,
Silent whispers break the ties.
Explosions echo through the night,
As dawn breaks, we stand united.

[chorus]
Rise from the ashes, soar so high,
Beneath the stormy sky.
Feel the thunder, hear the cry,
Of battles we cannot deny.

Please press the "generate" button to create the song with these settings. If you need any adjustments or further customization, let me know!
User : 
The lyrics are good, but I also want clean vocals at the start and powerful metal screaming towards the climax. Can we add that?
Agent : 

Successfully set the parameter tags
I've updated the tags to include clean vocals at the start and powerful metal screaming towards the climax. This will enhance the emotional build-up and explosive energy of the song.

With these adjustments, your song is ready to be generated. Please press the "generate" button to create the song with the new settings. If you have any more requests or need further changes, feel free to let me know!
User : 

Successfully halted.
I think we're ready to generate the song now. Let's create this epic metal masterpiece!
```

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
