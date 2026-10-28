# Nova — Your Local AI Assistant 🤖

**Nova is a Python-powered AI assistant designed to run locally on everyday computers, including machines with limited hardware resources.**

The project aims to make local AI more accessible by allowing users to run language models on their own computers without depending on a constant internet connection.

Nova includes voice-command functionality powered by **Faster-Whisper** and supports local inference using GGUF language models.

Nova is actively being developed, with ongoing work focused on improving performance, reliability, and the overall user experience.

## 🚀 Features

- **Local AI inference:** Run supported language models directly on your computer.
- **Voice commands:** Interact with Nova using speech recognition powered by Faster-Whisper.
- **Offline capability:** Use Nova without an internet connection once the required dependencies and models are installed.
- **Model selection:** Choose which supported model Nova should run.
- **Cross-platform goal:** Designed for use on Linux and Windows.
- **Python-based architecture:** Built primarily with Python.

## 🖥️ Testing Nova on Limited Hardware

I'm currently upgrading Nova and testing its performance on my own *potato PC* — a Lenovo ThinkPad P14s Gen 1.

This is my personal testing machine, not a hardware requirement for the project.

My goal is to discover how far local AI can be pushed on everyday computers without relying on expensive GPUs or cloud-based inference.

**A quick heads-up: Nova can be slow on limited hardware.**

Larger language models require significant memory and computational resources. When the GPU cannot handle the workload efficiently, inference may rely heavily on the CPU and system RAM.

This can result in slower response times, particularly when running larger models.

Your experience will depend on your hardware, the model you choose, its quantization, and your configuration.

I'll share more updates as I test different models, optimize performance, and improve Nova.

## 🧠 Models and Intelligence

**Nova does not come with a language model bundled in the repository.** You need to download your own compatible model before using the assistant.

I'm currently experimenting with different models to determine which ones offer a good balance between intelligence, speed, and memory usage on limited hardware.

The model you choose has a direct impact on Nova's capabilities. Different models can produce different results, response times, and levels of reasoning.

A larger model is not automatically the best option for every machine. Smaller, quantized models may be more practical when RAM and processing power are limited.

Nova currently uses GGUF model files, and you should select a model that is compatible with the application's loading configuration.

## ⚠️ Hallucinations and Reliability

One of the main challenges I'm currently working on is reducing AI hallucinations.

Because Nova is designed to operate offline, it cannot always check its answers against current external sources. Like other language models, it may generate incorrect information or confidently present a guess as a fact.

My goal is to improve how Nova communicates uncertainty so users can better distinguish between:

- **Model-generated answers:** Information generated from the model's learned patterns.
- **Uncertain answers:** Responses where the model may be guessing or lacks sufficient information.
- **Externally verified information:** Information checked against reliable sources when online verification becomes available.

I want Nova to acknowledge uncertainty rather than present every response as unquestionably true.

Online search and external fact verification are areas of development. Even with online search, answers will still require reliable sources and appropriate verification.

## 🛠️ Installation and Setup

Clone the repository and navigate to the project directory:

```bash
git clone YOUR_REPOSITORY_URL
cd YOUR_REPOSITORY_DIRECTORY
```

Replace the placeholders with your actual repository URL and directory name.

Create and activate a virtual environment if you use one, then install the project's required dependencies.

### 1. Install the CPU version of llama-cpp-python

Nova is intended to support systems without powerful GPUs. For a CPU-based setup, install the CPU-compatible package:

```bash
pip install llama-cpp-python --only-binary=:all: \
  --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

This requests a prebuilt CPU-compatible wheel. If no compatible wheel exists for your Python version and platform, installation may fail. See the [llama-cpp-python documentation](https://llama-cpp-python.readthedocs.io/en/latest/) for alternatives.

### 2. Install the Hugging Face CLI

The Hugging Face CLI allows you to download compatible models directly into Nova's model directory.

```bash
pip install -U huggingface_hub
```

### 3. Download a GGUF model

Find a compatible GGUF model repository on [Hugging Face](https://huggingface.co/models).

From the root of the Nova project, run:

```bash
hf download OWNER/MODEL_NAME --include "*.gguf" --local-dir ./models
```

Replace `OWNER/MODEL_NAME` with the actual Hugging Face repository ID.

This downloads matching GGUF files into the project's `models/` directory. If the repository contains multiple large GGUF files, consider downloading only the specific file you intend to use.

**Important:** Downloading a model repository does not automatically mean Nova will select the correct file. Make sure the model's filename and configuration match what Nova expects.

For additional download options, see the [Hugging Face CLI documentation](https://huggingface.co/docs/huggingface_hub/en/guides/cli).

## ▶️ Running Nova

Once the dependencies are installed and a compatible model is downloaded, you can launch Nova.

### 1. List available models

```bash
python -m nova --list
```

This displays the models Nova makes available for selection.

### 2. Select a model

```bash
python -m nova --model "MODEL_NAME"
```

Replace `MODEL_NAME` with the exact model identifier shown by Nova.

**This command selects the model Nova will run; it is separate from the Hugging Face command used to download model files.**

### 3. Start Nova

```bash
python -m nova
```

Nova will run using the selected model, provided that the required model files and dependencies are available.

## 🎙️ Voice Commands

Nova includes voice-command functionality powered by Faster-Whisper.

Speech recognition allows spoken input to be converted into text for processing by the assistant.

Voice functionality may require additional dependencies and configuration. Consult the project's dependency files and implementation for the exact setup requirements.

## 🔧 Development Roadmap

Nova is still a work in progress. Current development priorities include:

- [ ] Reducing hallucinations and improving answer reliability.
- [ ] Helping users distinguish between facts, uncertainty, and guesses.
- [ ] Improving inference speed on CPU-based and memory-constrained systems.
- [ ] Testing different GGUF models and quantization levels.
- [ ] Exploring online search and external fact verification.
- [ ] Improving voice recognition and the overall interaction experience.
- [ ] Improving compatibility across Linux and Windows.

## 🤝 Feedback and Contributions

Nova is an ongoing experiment in making local AI more practical on everyday hardware.

If you try Nova on your machine, I'd love to hear about your experience. Feedback on response speed, memory consumption, model compatibility, hallucinations, and voice recognition is especially useful.

I'm building Nova to explore what a local AI assistant can do with limited resources — and how much better it can become through continuous experimentation and improvement.

**Thanks for checking out Nova!**