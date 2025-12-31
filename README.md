# WaifuChat Local 💖

A locally hosted, privacy-focused, uncensored roleplay chat application. Run powerful AI waifus directly on your NVIDIA GPU with a modern, visual-novel style interface.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![GPU](https://img.shields.io/badge/GPU-NVIDIA%208GB%2B-green)
![Model](https://img.shields.io/badge/Model-Llama3%208B%20Stheno-purple)

## ✨ Features

*   **100% Offline & Private**: No data leaves your computer.
*   **Uncensored Roleplay**: Powered by the **L3-8B-Stheno-v3.2** model, designed for creative and complex storytelling without refusals.
*   **Immersive Visuals**:
    *   **Custom Avatars**: Upload your own character images (Neutral, Happy, Angry, etc.).
    *   **Dynamic Backgrounds**: Set unique wallpapers for each character.
    *   **Glassmorphism UI**: A sleek, neon-styled interface.
*   **Multi-Character System**:
    *   Create and edit unlimited characters via the built-in Editor.
    *   Switch between them instantly.
*   **Roleplay Tools**:
    *   **User Persona**: Define your own name and appearance so the AI knows who you are.
    *   **Regenerate (Reroll)**: Don't like a reply? Reroll it instantly.
    *   **Edit Messages**: Fix typos or steer the story by editing any message (yours or hers).
*   **Infinite Chat**: Automatic context sliding lets you chat forever without crashing.
*   **Persistent Memory**: Save and load your chat sessions at any time.

## 🌟 New Features (Update 1.1)
The app has been upgraded with advanced roleplay features to make your characters feel truly alive!

### 🎭 Dynamic Expressions
Characters now react visually to the conversation!
*   **Mood Awareness**: The AI automatically detects if it's happy, sad, angry, or blushing.
*   **Sprite Switching**: The avatar changes instantly to match the mood (e.g., smiling when complimented, frowning when insulted).
*   **Customizable**: Map your own image files to specific emotions in the Character Editor.

### 📔 "Living Memory" Diary
Solve the "goldfish memory" problem with the new Diary System.
*   **Episodic Memory**: The AI writes diary entries about your adventures from *its* perspective.
*   **Context Injection**: Recent diary entries are automatically fed into new chat sessions, so the character **remembers what you did yesterday**.
*   **End of Day**: Click "End Day & Write Diary" to generate a summary of your session.

### 📖 Lorebook (World Info)
Build a deep, consistent world.
*   **Keyword Triggering**: Define keywords (e.g., "The Crystal Kingdom", "Excalibur").
*   **Smart Injection**: When you mention a keyword, the app secretly injects the description into the AI's mind.
*   **No Confusion**: Keeps the AI on track with complex lore without using up all its memory.

## 🔊 Update 1.2: Voice & Compatibility
*   **Text-to-Speech (TTS)**: The waifu now speaks to you!
    *   **High Quality**: Uses natural-sounding Neural voices (like Aria, Guy, Jenny).
    *   **Customizable**: Adjust the **Pitch** (Hz) and **Speed** (%) to create unique voices for each character.
*   **Character Card Import**:
    *   Easily import characters from other sites (Chub.ai, SillyTavern) by dragging and dropping **V2 Character Cards (PNG)** or JSON files.

## 🌍 Update 1.3: The Living World
The app is now a lightweight Life Sim!
*   **Status System**:
    *   **Affection**: Being nice increases affection, insults decrease it.
    *   **Energy**: Talking drains energy. If it hits 0, they might get tired.
*   **Locations**:
    *   Travel to different places (Park, Cafe, Beach, etc.).
    *   The AI knows where you are and changes the context of the conversation.
*   **Time & Routine**:
    *   Real-time clock awareness.
    *   **"Wait 1 Hour"**: Button to advance time and restore Energy.

## 🎨 Update 1.4: The Immersion Update
Focusing on visuals and atmosphere to pull you deeper into the world.
*   **Dynamic Backgrounds**:
    *   Map different images to different locations (e.g., a cozy room for "Home", a sunny park for "Park").
    *   Backgrounds switch instantly when you travel.
*   **True Time System**:
    *   A 24-hour clock tracks the day (00:00 - 23:00).
    *   **Day/Night Cycle**: The app's visual atmosphere changes automatically based on the time (Morning glow, Day clear, Sunset orange, Night dark).
*   **Enhanced Editor**:
    *   New tools to easily upload and assign backgrounds to specific locations.

## 💾 Update 1.5: The "Memory & Management" Update
Refining the user experience with better tools to manage your AI's data.
*   **Diary Editor**:
    *   You can now **Edit** or **Delete** specific diary entries to fix incorrect memories.
*   **Character Export**:
    *   Easily back up your character (including images and memories) to a ZIP file for safekeeping or sharing.
*   **"Brain Scan" Debugger**:
    *   A new tool for power users to see exactly what the AI is "thinking" (the raw prompt sent to the model).
*   **New Interactions**:
    *   **Give Gifts**: Give items like Coffee or Flowers to boost affection.
    *   **"Let Her Speak"**: A button to let the AI continue talking without you interrupting.

## 👁️ Update 2.0 (Phase 1): Sight
The first step towards a fully multimodal AI.
*   **Visual Perception**:
    *   **"Show her something"**: Upload an image in the chat.
    *   **Image Captioning**: The app uses the BLIP AI model to "see" the image and convert it into a description (e.g., "User showed an image: a small cat sleeping on a laptop").
    *   **Reaction**: The character reacts to what she sees in character!

## 👂 Update 2.0 (Phase 2): Hearing
Now you can talk to her directly!
*   **Voice Input**:
    *   Uses **OpenAI Whisper** (Local Base Model) for high-accuracy speech-to-text.
    *   Click the microphone icon 🎤, record your message, and it will be transcribed instantly.
    *   Works completely offline.

## 🌙 Update 2.0 (Phase 3): The Inner World
The AI now has a subconscious.
*   **Dream System**:
    *   When you click **"End Day (Sleep)"**, the AI reflects on the day's diary entry and generates a dream.
    *   Dreams are abstract, emotional, and sometimes surreal.
    *   **Dream Journal**: Read her past dreams in the "Memory" sidebar.

## 🕰️ Update 2.0 (Phase 4): Autonomous Life
She lives her own life when you're not around.
*   **Offline Simulation**:
    *   The app calculates how much time has passed since you last chatted.
    *   **Activities**: She might read a book, clean her room, sleep, or practice cooking while you are away.
    *   **Stat Changes**: Being away too long might drain her energy (if she stayed up waiting) or restore it (if she slept).
*   **Welcome Back**: When you log in, you'll see a toast notification telling you what she did, and she will know it too!

---

## 🚀 Installation (Windows)

### Prerequisites
1.  **NVIDIA GPU**: You need a card with at least **6GB VRAM** (8GB recommended).
2.  **CUDA Toolkit**: Install the [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-downloads) to enable GPU acceleration.
3.  **Python**: Install [Python 3.10 or newer](https://www.python.org/downloads/).
    *   *Important*: Check the box **"Add Python to PATH"** during installation.

### Quick Start
1.  Double-click **`install.bat`**.
    *   This will create a virtual environment, install all dependencies (configured for NVIDIA GPUs), and download the 5GB AI model.
2.  Once finished, double-click **`run.bat`** to start the app.

---

## 📖 User Guide

### 1. Creating a Character
*   Open the sidebar and expand **"🛠️ Character Editor"**.
*   Select **"Create New"**.
*   Fill in the Name, Description, and Scenario.
*   **Upload Images**:
    *   Upload an Avatar image. Copy the filename it gives you into the JSON map (e.g., `"happy": "my_image.png"`).
    *   Upload a Background image and paste the filename into the "Background Image" field.
*   **Add World Info**: Use the Lorebook section to add important keywords and their descriptions.
*   Click **"Create Character"**.

### 2. Chatting
*   Type your message in the bottom box.
*   **Regenerate**: Click the **🔄** button to redo the last AI response.
*   **Edit**: Click the **✏️** pencil icon next to any message to change the text.
*   **End Day**: When you're done, scroll down to the "Diary" section and click "End Day & Write Diary" to save the memory.

### 3. Saving & Loading
*   Go to the **"💾 Memory"** section in the sidebar.
*   Type a name and click **"Save Current Session"**.
*   To resume later, select a file from the list and click **"Load"**.

---

## 🛠️ Troubleshooting

**"CUDA not found" / Slow Generation:**
*   Ensure you installed the NVIDIA CUDA Toolkit.
*   Re-run `install.bat` to force-reinstall the GPU-optimized libraries.

**"Context Limit Exceeded":**
*   The app automatically handles this by trimming old messages. You shouldn't see this error.

**App crashes on startup:**
*   Make sure you have enough free RAM (System Memory) and VRAM. The model requires about 5.5GB VRAM.

---

## 📂 Project Structure
*   `app.py`: Main UI logic (Streamlit).
*   `brain.py`: AI inference engine (Llama-cpp).
*   `character_manager.py`: Handles saving/loading characters and chats.
*   `characters/`: Folder containing all your waifu data and images.
*   `models/`: Where the GGUF model file lives.

## License
MIT License. Feel free to modify and share!
