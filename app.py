import streamlit as st
import time
import os
import signal
import sys
import json
from brain import WaifuAI
from character_manager import CharacterManager

# Suppress Windows Error 6 on Ctrl+C
def signal_handler(sig, frame):
    sys.exit(0)

try:
    signal.signal(signal.SIGINT, signal_handler)
except ValueError:
    # Streamlit runs in a secondary thread, so we can't always catch signals.
    # This is fine, we just ignore it.
    pass

# Page Config
st.set_page_config(page_title="WaifuChat Local", page_icon="💖", layout="wide")

# Custom CSS for chat and thoughts
st.markdown("""
<style>
    /* Import Google Font: Nunito (Rounded & Friendly) */
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Nunito', sans-serif;
    }

    /* Main App Background (Dark Mode Default) */
    .stApp {
        background-color: #1a1a2e;
        color: #e0e0e0;
    }

    /* --- Chat Bubbles --- */
    /* We target Streamlit's chat message container */
    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
    }

    /* User Message Bubble */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        flex-direction: row-reverse;
        text-align: right;
    }
    
    /* Avatar Container Styling */
    .stChatMessage .stChatMessageAvatar {
        background-color: #16213e;
        border: 2px solid #0f3460;
    }

    /* Message Content Styling */
    div[data-testid="stChatMessageContent"] {
        background: rgba(22, 33, 62, 0.8);
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: transform 0.2s;
    }
    
    div[data-testid="stChatMessageContent"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
    }

    /* Waifu Specific Glow (Purple/Pink) */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) div[data-testid="stChatMessageContent"] {
        border-left: 4px solid #e94560;
        background: linear-gradient(135deg, rgba(233, 69, 96, 0.1), rgba(22, 33, 62, 0.8));
    }

    /* User Specific Glow (Blue/Cyan) */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) div[data-testid="stChatMessageContent"] {
        border-right: 4px solid #0f3460;
        background: linear-gradient(135deg, rgba(15, 52, 96, 0.8), rgba(22, 33, 62, 0.8));
    }

    /* --- Thoughts Styling --- */
    .thought-bubble {
        font-size: 0.9em;
        color: #aaa;
        font-style: italic;
        border-left: 2px solid #e94560;
        padding-left: 10px;
        margin-bottom: 8px;
        background-color: rgba(0,0,0,0.2);
        padding: 8px;
        border-radius: 0 8px 8px 0;
    }

    /* --- Avatar (Left Column) --- */
    .avatar-container {
        font-size: 50px;
        text-align: center;
        margin-bottom: 10px;
    }
    .big-avatar img {
        width: 220px;
        height: 220px;
        object-fit: cover;
        border-radius: 20px;
        border: 3px solid #e94560;
        box-shadow: 0 0 15px rgba(233, 69, 96, 0.4);
        transition: all 0.3s ease;
    }
    .big-avatar img:hover {
        transform: scale(1.05);
        box-shadow: 0 0 25px rgba(233, 69, 96, 0.6);
    }
    .big-avatar {
        font-size: 150px;
        display: block;
        margin: 0 auto;
        text-align: center;
        filter: drop-shadow(0 0 10px rgba(233, 69, 96, 0.3));
    }

    /* --- Sidebar Styling --- */
    section[data-testid="stSidebar"] {
        background-color: rgba(26, 26, 46, 0.95);
        border-right: 1px solid #16213e;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #0f3460;
        color: white;
        border-radius: 8px;
        border: none;
        transition: background 0.3s;
    }
    .stButton button:hover {
        background-color: #e94560;
        color: white;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #e94560 !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# Model Path
MODEL_PATH = "./models/L3-8B-Stheno-v3.2-Q4_K_M.gguf"

# Initialize Session State
if "waifu" not in st.session_state:
    st.session_state.waifu = None
if "char_mgr" not in st.session_state:
    st.session_state.char_mgr = CharacterManager()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_char" not in st.session_state:
    st.session_state.current_char = None
if "current_emotion" not in st.session_state:
    st.session_state.current_emotion = "neutral"
if "editor_mode" not in st.session_state:
    st.session_state.editor_mode = "edit" # 'edit' or 'create'
if "should_regenerate" not in st.session_state:
    st.session_state.should_regenerate = False

if "user_persona" not in st.session_state:
    st.session_state.user_persona = {"name": "User", "description": ""}

# Background Injection
bg_image = st.session_state.char_mgr.get_background_image()
if bg_image:
    # Convert local path to a format we can display (base64 is safest for local files in streamlit)
    import base64
    def get_base64_of_bin_file(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()

    bg_base64 = get_base64_of_bin_file(bg_image)
    
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url("data:image/png;base64,{bg_base64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Sidebar - Settings
with st.sidebar:
    st.title("⚙️ Waifu Settings")
    
    # --- User Persona ---
    with st.expander("👤 User Persona"):
        st.session_state.user_persona["name"] = st.text_input("Your Name", value=st.session_state.user_persona["name"])
        st.session_state.user_persona["description"] = st.text_area("Your Description", value=st.session_state.user_persona["description"], placeholder="e.g. A wandering knight...")
    
    # --- Character Selection ---
    st.subheader("�‍♀️ Character")
    available_chars = st.session_state.char_mgr.list_characters()
    
    # Default to Stheno if available, else first one
    default_index = 0
    if "Stheno" in available_chars:
        default_index = available_chars.index("Stheno")
        
    selected_char = st.selectbox(
        "Choose your companion:", 
        available_chars, 
        index=default_index if st.session_state.current_char is None else available_chars.index(st.session_state.current_char)
    )

    # Load Character Logic
    if selected_char != st.session_state.current_char:
        # Load new character config
        config = st.session_state.char_mgr.load_character(selected_char)
        st.session_state.current_char = selected_char
        st.session_state.messages = [] # Clear chat on switch
        st.session_state.current_emotion = "neutral"
        
        # Update AI Brain if loaded
        if st.session_state.waifu:
            st.session_state.waifu.clear_history()
            st.session_state.waifu.set_persona(
                config["name"], 
                config["description"], 
                config["scenario"], 
                config["example_dialogue"],
                user_name=st.session_state.user_persona["name"]
            )
        st.rerun()

    # --- Character Editor ---
    with st.expander("🛠️ Character Editor"):
        mode = st.radio("Mode", ["Edit Current", "Create New"], horizontal=True)
        
        if mode == "Edit Current":
            if st.session_state.current_char:
                current_config = st.session_state.char_mgr.character_config
                edit_name = st.text_input("Name", value=current_config.get("name", ""), disabled=True)
                edit_desc = st.text_area("Description", value=current_config.get("description", ""), height=100)
                edit_scenario = st.text_area("Scenario", value=current_config.get("scenario", ""), height=80)
                edit_dialogue = st.text_area("Example Dialogue", value=current_config.get("example_dialogue", ""), height=100)
                
                # Simple Avatar Map Editor (JSON text)
                current_map_str = json.dumps(current_config.get("avatar_emotion_map", {}), indent=2, ensure_ascii=False)
                edit_map_str = st.text_area("Avatar Map (JSON)", value=current_map_str, height=150)
                
                # Image Upload
                st.subheader("🖼️ Upload Images")
                uploaded_file = st.file_uploader("Upload Avatar or Background", type=["png", "jpg", "jpeg"])
                if uploaded_file:
                    file_name = uploaded_file.name
                    saved_path = st.session_state.char_mgr.save_image(edit_name, uploaded_file, file_name)
                    st.success(f"Saved to {saved_path}")
                    st.info("Copy this filename into your Avatar Map JSON above!")
                
                edit_bg = st.text_input("Background Image (Filename in avatars folder)", value=current_config.get("background_image", ""))

                if st.button("Save Changes"):
                    try:
                        new_map = json.loads(edit_map_str)
                        new_config = {
                            "name": edit_name,
                            "description": edit_desc,
                            "scenario": edit_scenario,
                            "example_dialogue": edit_dialogue,
                            "avatar_emotion_map": new_map,
                            "background_image": edit_bg
                        }
                        st.session_state.char_mgr.save_character(edit_name, new_config)
                        st.success(f"Updated {edit_name}!")
                        
                        # Reload to apply immediately
                        st.session_state.char_mgr.load_character(edit_name)
                        if st.session_state.waifu:
                             st.session_state.waifu.set_persona(edit_name, edit_desc, edit_scenario, edit_dialogue)
                        st.rerun()
                    except json.JSONDecodeError:
                        st.error("Invalid JSON in Avatar Map")
            else:
                st.info("Select a character first.")
                
        else: # Create New
            new_char_name = st.text_input("New Character Name")
            new_desc = st.text_area("Description", placeholder="She is a...", height=100)
            new_scenario = st.text_area("Scenario", placeholder="You meet her at...", height=80)
            new_dialogue = st.text_area("Example Dialogue", placeholder="User: Hi\nChar: Hello!", height=100)
            
            default_map = {
                "neutral": "😐",
                "happy": "😊",
                "sad": "😢",
                "angry": "😠"
            }
            new_map_str = st.text_area("Avatar Map (JSON)", value=json.dumps(default_map, indent=2), height=150)
            
            if st.button("Create Character"):
                if new_char_name and new_desc:
                    try:
                        new_map = json.loads(new_map_str)
                        new_config = {
                            "name": new_char_name,
                            "description": new_desc,
                            "scenario": new_scenario,
                            "example_dialogue": new_dialogue,
                            "avatar_emotion_map": new_map
                        }
                        st.session_state.char_mgr.save_character(new_char_name, new_config)
                        st.success(f"Created {new_char_name}!")
                        time.sleep(1)
                        st.rerun()
                    except json.JSONDecodeError:
                        st.error("Invalid JSON in Avatar Map")
                else:
                    st.error("Name and Description are required.")
    
    # --- Session Management ---
    st.divider()
    st.subheader("💾 Memory")
    
    # Save
    new_save_name = st.text_input("Save Name (Optional)", placeholder="My Chat 1")
    if st.button("Save Current Session"):
        if st.session_state.messages:
            filename = st.session_state.char_mgr.save_session(
                st.session_state.messages, 
                new_save_name if new_save_name else None,
                st.session_state.user_persona
            )
            st.success(f"Saved to {filename}")
        else:
            st.warning("Nothing to save yet.")
            
    # Load
    saved_sessions = st.session_state.char_mgr.list_sessions()
    if saved_sessions:
        session_to_load = st.selectbox("Load Session", saved_sessions)
        if st.button("Load"):
            loaded_msgs, loaded_user = st.session_state.char_mgr.load_session(session_to_load)
            st.session_state.messages = loaded_msgs
            st.session_state.user_persona = loaded_user
            st.session_state.waifu.history = loaded_msgs
            st.success("Session Loaded!")
            st.rerun()
    else:
        st.info("No saved sessions for this character.")

    # --- Generation Settings ---
    st.divider()
    st.subheader("🧠 Brain Params")
    temp = st.slider("Temperature (Creativity)", 0.1, 1.5, 1.1)
    rep_pen = st.slider("Repetition Penalty", 1.0, 1.5, 1.1)
    min_p = st.slider("Min-P", 0.0, 1.0, 0.05)
    top_k = st.slider("Top-K", 0, 100, 40)
    
    # Clear Chat
    if st.button("Reset Chat"):
        st.session_state.messages = []
        st.session_state.waifu.clear_history()
        st.rerun()

# Main Layout
col1, col2 = st.columns([1, 3])

# Left Column: Avatar
with col1:
    # Get current avatar based on emotion
    avatar_result = st.session_state.char_mgr.get_avatar_for_emotion(st.session_state.current_emotion)
    
    if os.path.exists(avatar_result) and (avatar_result.endswith(".png") or avatar_result.endswith(".jpg") or avatar_result.endswith(".jpeg")):
        # It's an image file
        st.image(avatar_result, width=300)
    else:
        # It's an emoji
        st.markdown(f'<div class="big-avatar">{avatar_result}</div>', unsafe_allow_html=True)
        
    st.markdown(f"<h3 style='text-align: center;'>{st.session_state.current_char}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #888;'>Current Mood: {st.session_state.current_emotion}</p>", unsafe_allow_html=True)

# Right Column: Chat
with col2:
    # Initialize AI if not ready
    if st.session_state.waifu is None:
        if os.path.exists(MODEL_PATH):
            with st.spinner("Loading AI Brain (this takes a moment)..."):
                try:
                    st.session_state.waifu = WaifuAI(MODEL_PATH)
                    # Load initial character
                    config = st.session_state.char_mgr.load_character(selected_char)
                    st.session_state.waifu.set_persona(
                        config["name"], 
                        config["description"], 
                        config["scenario"], 
                        config["example_dialogue"]
                    )
                    st.success("Connected!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to load model: {e}")
        else:
            st.warning("Please download the model first using download_model.py")
            st.stop()

    if "editing_msg" not in st.session_state:
        st.session_state.editing_msg = None # {index: int, content: str}

    # Display Chat History
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            if st.session_state.editing_msg and st.session_state.editing_msg["index"] == i:
                # Edit Mode
                new_content = st.text_area("Edit Message", value=st.session_state.editing_msg["content"], key=f"edit_area_{i}")
                col_save, col_cancel = st.columns([1, 1])
                if col_save.button("Save", key=f"save_{i}"):
                    st.session_state.messages[i]["content"] = new_content
                    # If it was an AI message, we might want to strip thoughts if editing speech only?
                    # For simplicity, we overwrite the whole content.
                    st.session_state.waifu.edit_message(i, new_content)
                    st.session_state.editing_msg = None
                    st.rerun()
                if col_cancel.button("Cancel", key=f"cancel_{i}"):
                    st.session_state.editing_msg = None
                    st.rerun()
            else:
                # View Mode
                if message["role"] == "assistant":
                    # Check for thoughts
                    content = message["content"]
                    thought = None
                    speech = content
                    
                    if "<thought>" in content and "</thought>" in content:
                        start = content.find("<thought>") + len("<thought>")
                        end = content.find("</thought>")
                        thought = content[start:end].strip()
                        speech = content[end+len("</thought>"):].strip()
                    
                    if thought:
                        with st.expander("💭 Inner Thoughts"):
                            st.markdown(f"*{thought}*")
                    st.markdown(speech)
                    
                    # Edit / Regenerate Tools
                    col_tools1, col_tools2, col_tools3 = st.columns([1, 1, 8])
                    with col_tools1:
                        if i == len(st.session_state.messages) - 1: # Only last message
                            if st.button("🔄", key=f"regen_{i}", help="Regenerate Last Response"):
                                st.session_state.messages.pop()
                                st.session_state.waifu.regenerate_last()
                                st.session_state.should_regenerate = True
                                st.rerun()
                    with col_tools2:
                         if st.button("✏️", key=f"edit_btn_{i}", help="Edit Message"):
                             st.session_state.editing_msg = {"index": i, "content": message["content"]}
                             st.rerun()

                else:
                    # User Message
                    st.markdown(message["content"])
                    col_user_edit, _ = st.columns([1, 9])
                    with col_user_edit:
                         if st.button("✏️", key=f"edit_user_{i}", help="Edit Message"):
                             st.session_state.editing_msg = {"index": i, "content": message["content"]}
                             st.rerun()

    # Chat Input Logic
    user_input = st.chat_input("Say something...")
    
    if user_input or st.session_state.should_regenerate:
        # Handle Regeneration
        if st.session_state.should_regenerate:
            # Get the last user message
            if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                user_input = st.session_state.messages[-1]["content"]
                # We don't append it again because it's already in history
            else:
                st.error("Cannot regenerate: No user message found to respond to.")
                st.session_state.should_regenerate = False
                st.stop()
        else:
            # Normal user input
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

        # Reset flag
        st.session_state.should_regenerate = False

        # Generate response
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            thought_placeholder = st.empty()
            
            full_response = ""
            is_thinking = False
            
            # Generator
            for chunk in st.session_state.waifu.generate_response(
                user_input, 
                temperature=temp,
                repetition_penalty=rep_pen,
                min_p=min_p,
                top_k=top_k
            ):
                full_response += chunk
                
                # Real-time thought parsing
                if "<thought>" in full_response and not is_thinking:
                    is_thinking = True
                    thought_placeholder.markdown("💭 *Thinking...*")
                
                if "</thought>" in full_response and is_thinking:
                    is_thinking = False
                    # Extract thought
                    start = full_response.find("<thought>") + len("<thought>")
                    end = full_response.find("</thought>")
                    thought_content = full_response[start:end].strip()
                    
                    # Update Emotion State
                    # Simple heuristic: Check thought for emotion keywords
                    emotion_found = False
                    config = st.session_state.char_mgr.character_config
                    if "avatar_emotion_map" in config:
                        for emotion_key in config["avatar_emotion_map"]:
                            if emotion_key in thought_content.lower():
                                st.session_state.current_emotion = emotion_key
                                emotion_found = True
                                break
                    if not emotion_found:
                        st.session_state.current_emotion = "neutral"
                    
                    thought_placeholder.empty()
                    with thought_placeholder.expander("💭 Inner Thoughts", expanded=True):
                        st.markdown(f"*{thought_content}*")
                
                # Display speech
                if not is_thinking and "</thought>" in full_response:
                     speech_part = full_response.split("</thought>")[-1]
                     response_placeholder.markdown(speech_part + "▌")
                elif not is_thinking and "<thought>" not in full_response:
                     response_placeholder.markdown(full_response + "▌")

            # Final cleanup
            final_thought, final_speech = st.session_state.waifu.get_last_thought_and_response()
            response_placeholder.markdown(final_speech)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.rerun() # Rerun to update the avatar in the left column
