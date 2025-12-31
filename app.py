import streamlit as st
import time
import os
import signal
import sys
import json
from brain import WaifuAI
from character_manager import CharacterManager
from voice_manager import VoiceManager
from vision_manager import VisionManager
from hearing_manager import HearingManager

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
if "voice_mgr" not in st.session_state:
    st.session_state.voice_mgr = VoiceManager()
if "vision_mgr" not in st.session_state:
    st.session_state.vision_mgr = VisionManager()
if "hearing_mgr" not in st.session_state:
    st.session_state.hearing_mgr = HearingManager()
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
if "tts_enabled" not in st.session_state:
    st.session_state.tts_enabled = False

if "user_persona" not in st.session_state:
    st.session_state.user_persona = {"name": "User", "description": ""}

# Background Injection
bg_image = st.session_state.char_mgr.get_background_image()
current_hour = st.session_state.char_mgr.get_time()

# Determine Time Overlay
# Default (Day)
overlay_color = "rgba(0, 0, 0, 0.5)" 

if 5 <= current_hour < 8: # Dawn
    overlay_color = "rgba(255, 200, 150, 0.4)"
elif 8 <= current_hour < 17: # Day
    overlay_color = "rgba(0, 0, 0, 0.3)"
elif 17 <= current_hour < 20: # Sunset
    overlay_color = "rgba(255, 100, 50, 0.3)"
else: # Night
    overlay_color = "rgba(10, 10, 40, 0.85)"

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
            background-image: linear-gradient({overlay_color}, {overlay_color}), url("data:image/png;base64,{bg_base64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            transition: background-image 1s ease-in-out;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    # No image, just use color overlay on default dark theme
    pass

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
                user_name=st.session_state.user_persona["name"],
                lorebook=config.get("lorebook", {}),
                past_events=st.session_state.char_mgr.get_recent_diary_entries(),
                stats=st.session_state.char_mgr.get_stats(),
                location=st.session_state.char_mgr.get_location(),
                current_time_str=f"{st.session_state.char_mgr.get_time()}:00"
            )
            
            # Check for offline progression
            offline_report = st.session_state.char_mgr.process_offline_time()
            if offline_report:
                st.toast(f"While you were gone: {offline_report}", icon="🕰️")
                # Inject as system context so she knows what she did
                st.session_state.messages.append({"role": "system", "content": f"*[System: While the user was away, you {offline_report}]*"})
                
        st.rerun()

    # --- Character Editor ---
    with st.expander("🛠️ Character Editor"):
        mode = st.radio("Mode", ["Edit Current", "Create New", "Import Card"], horizontal=True)
        
        if mode == "Import Card":
            st.info("Import a V2 Character Card (PNG) or JSON.")
            uploaded_card = st.file_uploader("Upload Card", type=["png", "json"])
            if uploaded_card:
                if st.button("Import"):
                    name, error = st.session_state.char_mgr.import_character_card(uploaded_card)
                    if name:
                        st.success(f"Imported {name} successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Import failed: {error}")

        elif mode == "Edit Current":
            if not st.session_state.current_char:
                st.info("Select a character first.")
            else:
                current_config = st.session_state.char_mgr.character_config
                edit_name = st.text_input("Name", value=current_config.get("name", ""), disabled=True)
                edit_desc = st.text_area("Description", value=current_config.get("description", ""), height=100)
                edit_scenario = st.text_area("Scenario", value=current_config.get("scenario", ""), height=80)
                edit_dialogue = st.text_area("Example Dialogue", value=current_config.get("example_dialogue", ""), height=100)
                
                # Simple Avatar Map Editor (JSON text)
                current_map_str = json.dumps(current_config.get("avatar_emotion_map", {}), indent=2, ensure_ascii=False)
                edit_map_str = st.text_area("Avatar Map (JSON)", value=current_map_str, height=150)
                
                # Image Upload
                st.subheader("🖼️ Images & Backgrounds")
                
                # 1. Default Background
                edit_bg = st.text_input("Default Background (Filename)", value=current_config.get("background_image", ""))
                
                # 2. Location Backgrounds
                st.caption("📍 Location Specific Backgrounds")
                loc_map = current_config.get("location_images", {})
                loc_list = ["Home", "Park", "Cafe", "Beach", "School", "Dungeon"]
                
                col_l1, col_l2 = st.columns([2, 1])
                selected_loc_bg = col_l1.selectbox("Select Location", loc_list)
                current_loc_img = loc_map.get(selected_loc_bg, "")
                
                new_loc_img = col_l1.text_input(f"Image for {selected_loc_bg}", value=current_loc_img)
                if col_l2.button("Update Loc"):
                    st.session_state.char_mgr.set_location_image(selected_loc_bg, new_loc_img)
                    st.success(f"Updated {selected_loc_bg}")
                    st.rerun()

                # 3. Uploader
                st.markdown("---")
                uploaded_file = st.file_uploader("Upload New Image", type=["png", "jpg", "jpeg"])
                target_use = st.radio("Auto-assign upload to:", ["None (Just Save)", "Default Background", f"Location: {selected_loc_bg}"], horizontal=True)

                if uploaded_file and st.button("Save Upload"):
                    file_name = uploaded_file.name
                    saved_path = st.session_state.char_mgr.save_image(edit_name, uploaded_file, file_name)
                    st.success(f"Saved to {saved_path}")
                    
                    if target_use.startswith("Location"):
                        st.session_state.char_mgr.set_location_image(selected_loc_bg, file_name)
                        st.success(f"Set as background for {selected_loc_bg}")
                        st.rerun()
                    elif target_use == "Default Background":
                        # We can't update the text input variable directly in this run, 
                        # but we can update the config if we save. 
                        # For now, let's just show the name.
                        st.info(f"File saved. Enter '{file_name}' in the Default Background field above.")

                if st.button("Save All Changes"):
                    try:
                        new_map = json.loads(edit_map_str)
                        new_config = {
                            "name": edit_name,
                            "description": edit_desc,
                            "scenario": edit_scenario,
                            "example_dialogue": edit_dialogue,
                            "avatar_emotion_map": new_map,
                            "background_image": edit_bg,
                            "lorebook": current_config.get("lorebook", {})
                        }
                        st.session_state.char_mgr.save_character(edit_name, new_config)
                        st.success(f"Updated {edit_name}!")
                        
                        # Reload to apply immediately
                        st.session_state.char_mgr.load_character(edit_name)
                        if st.session_state.waifu:
                             st.session_state.waifu.set_persona(
                                 edit_name, 
                                 edit_desc, 
                                 edit_scenario, 
                                 edit_dialogue,
                                 user_name=st.session_state.user_persona["name"],
                                 lorebook=new_config.get("lorebook", {}),
                                 past_events=st.session_state.char_mgr.get_recent_diary_entries(),
                                 stats=st.session_state.char_mgr.get_stats(),
                                 location=st.session_state.char_mgr.get_location(),
                                 current_time_str=f"{st.session_state.char_mgr.get_time()}:00"
                             )
                        st.rerun()
                    except json.JSONDecodeError:
                        st.error("Invalid JSON in Avatar Map")
                
                # --- Lorebook Editor ---
                st.divider()
                st.subheader("📖 World Info (Lorebook)")
                st.info("Keywords trigger the AI to remember specific details.")
                
                # Add New Entry
                col_key, col_content, col_add = st.columns([1, 2, 0.5])
                new_lore_key = col_key.text_input("New Keyword", placeholder="e.g. Excalibur")
                new_lore_content = col_content.text_input("Description", placeholder="A sword of light...")
                if col_add.button("➕"):
                    if new_lore_key and new_lore_content:
                        st.session_state.char_mgr.update_lore_entry(new_lore_key, new_lore_content)
                        st.success(f"Added '{new_lore_key}'")
                        time.sleep(1)
                        st.rerun()

                # List Entries
                lorebook = current_config.get("lorebook", {})
                if lorebook:
                    for key, content in lorebook.items():
                        c1, c2, c3 = st.columns([1, 2, 0.5])
                        c1.text(key)
                        c2.text(content)
                        if c3.button("🗑️", key=f"del_lore_{key}"):
                            st.session_state.char_mgr.delete_lore_entry(key)
                            st.rerun()
                else:
                    st.caption("No lore entries yet.")
            
                # --- Diary (Editable) ---
                st.divider()
                st.subheader("📔 Diary Memories")
                diary_entries = st.session_state.char_mgr.get_all_diary_entries()
                
                if diary_entries:
                    for i, entry in enumerate(diary_entries):
                        with st.expander(f"{entry['date']}"):
                            # We use a form to avoid instant reloads on typing
                            with st.form(key=f"diary_edit_{i}"):
                                new_content = st.text_area("Content", value=entry['content'], height=100)
                                c_del, c_save = st.columns([1, 1])
                                delete = c_del.form_submit_button("Delete Entry")
                                save = c_save.form_submit_button("Update Entry")
                                
                                if delete:
                                    # Remove this entry
                                    diary_entries.pop(i)
                                    st.session_state.char_mgr.save_diary(diary_entries)
                                    st.success("Deleted!")
                                    time.sleep(1)
                                    st.rerun()
                                    
                                if save:
                                    # Update content
                                    entry['content'] = new_content
                                    # Diary entries is a reference to the list, so this updates it
                                    st.session_state.char_mgr.save_diary(diary_entries)
                                    st.success("Updated!")
                                    time.sleep(1)
                                    st.rerun()
                else:
                    st.caption("No diary entries yet.")
                    
                # --- Export ---
                st.divider()
                st.subheader("📦 Export")
                if st.button("Export Character Package"):
                    zip_path = st.session_state.char_mgr.export_character(edit_name)
                    if zip_path:
                        with open(zip_path, "rb") as fp:
                             btn = st.download_button(
                                 label="Download ZIP",
                                 data=fp,
                                 file_name=zip_path,
                                 mime="application/zip"
                             )
                        st.success(f"Ready to download {zip_path}")
                    else:
                        st.error("Export failed.")
        
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

    # --- Diary Actions ---
    st.divider()
    st.subheader("📔 Diary & Dreams")
    if st.button("End Day (Sleep)"):
        if st.session_state.waifu and st.session_state.messages:
            with st.spinner("Writing diary and dreaming..."):
                # 1. Write Diary
                entry = st.session_state.waifu.generate_diary_entry(
                    st.session_state.current_char, 
                    st.session_state.user_persona["name"]
                )
                if entry:
                    st.session_state.char_mgr.save_diary_entry(entry)
                    st.success("Diary entry written.")
                    
                    # 2. Dream
                    dream = st.session_state.waifu.generate_dream(
                        st.session_state.current_char,
                        entry
                    )
                    st.session_state.char_mgr.save_dream(dream)
                    st.info(f"Dreamt: {dream}")
                    
                    # 3. Restore Energy
                    st.session_state.char_mgr.update_stats(energy_delta=100)
                    st.success("Energy fully restored.")
                    
                else:
                    st.error("Could not generate diary (history empty?)")
        else:
            st.warning("Start a conversation first.")
            
    # Dream Journal
    with st.expander("🌙 Dream Journal"):
        dreams = st.session_state.char_mgr.get_all_dreams()
        if dreams:
            for d in dreams:
                st.markdown(f"**{d['date']}**: {d['content']}")
        else:
            st.caption("No dreams yet.")

    # --- Generation Settings ---
    st.divider()
    st.subheader("🧠 Brain Params")
    temp = st.slider("Temperature (Creativity)", 0.1, 1.5, 1.1)
    rep_pen = st.slider("Repetition Penalty", 1.0, 1.5, 1.1)
    min_p = st.slider("Min-P", 0.0, 1.0, 0.05)
    top_k = st.slider("Top-K", 0, 100, 40)
    
    with st.expander("🧠 Brain Scan (Debug)"):
        if st.session_state.waifu and st.session_state.waifu.last_prompt:
            st.text_area("Last Raw Prompt", value=st.session_state.waifu.last_prompt, height=300)
        else:
            st.caption("No prompt generated yet.")
    
    st.divider()
    st.subheader("🔊 Audio")
    st.session_state.tts_enabled = st.checkbox("Enable Voice (TTS)", value=st.session_state.tts_enabled)
    
    if st.session_state.tts_enabled:
        # Voice Settings
        voices = st.session_state.voice_mgr.VOICES
        voice_names = list(voices.keys())
        default_voice_idx = 0
        
        # Select Box
        selected_voice_name = st.selectbox("Voice", voice_names, index=default_voice_idx)
        st.session_state.tts_voice = voices[selected_voice_name]
        
        # Pitch and Rate
        col_p, col_r = st.columns(2)
        with col_p:
            pitch_val = st.slider("Pitch (Hz)", -50, 50, 0, step=5)
            st.session_state.tts_pitch = f"{pitch_val:+d}Hz"
        with col_r:
            rate_val = st.slider("Speed (%)", -50, 50, 0, step=10)
            st.session_state.tts_rate = f"{rate_val:+d}%"
    else:
        # Defaults if disabled to avoid errors
        st.session_state.tts_voice = "en-US-AriaNeural"
        st.session_state.tts_pitch = "+0Hz"
        st.session_state.tts_rate = "+0%"
        
    # --- Status & Living World (v1.3) ---
    st.divider()
    st.subheader("💗 Status")
    
    # Get stats
    current_stats = st.session_state.char_mgr.get_stats()
    
    # Affection Bar
    st.write("Affection")
    st.progress(current_stats.get("affection", 0) / 100.0)
    
    # Energy Bar
    st.write("Energy")
    st.progress(current_stats.get("energy", 100) / 100.0)
    
    # Gifts
    st.caption("🎁 Give Gift")
    col_g1, col_g2 = st.columns([2, 1])
    gift_map = {
        "Coffee ☕": {"aff": 1, "nrg": 5, "msg": "You gave her a warm cup of coffee."},
        "Flower 🌸": {"aff": 3, "nrg": 0, "msg": "You gave her a beautiful flower."},
        "Sweet Bun 🥐": {"aff": 2, "nrg": 3, "msg": "You shared a sweet treat."},
        "Shiny Rock 🪨": {"aff": -1, "nrg": 0, "msg": "You gave her... a rock?"}
    }
    selected_gift = col_g1.selectbox("Item", list(gift_map.keys()), label_visibility="collapsed")
    if col_g2.button("Give"):
        effect = gift_map[selected_gift]
        st.session_state.char_mgr.update_stats(effect["aff"], effect["nrg"])
        st.session_state.messages.append({"role": "system", "content": f"*{effect['msg']}*"})
        st.success(f"Gave {selected_gift}")
        time.sleep(1)
        st.rerun()
    
    # Location
    st.subheader("🗺️ Location")
    current_loc = st.session_state.char_mgr.get_location()
    
    locations = ["Home", "Park", "Cafe", "Beach", "School", "Dungeon"]
    new_loc = st.selectbox("Travel to:", locations, index=locations.index(current_loc) if current_loc in locations else 0)
    
    if new_loc != current_loc:
        st.session_state.char_mgr.set_location(new_loc)
        # Add a system message about travel
        st.session_state.messages.append({"role": "system", "content": f"*You traveled to the {new_loc}.*"})
        st.rerun()
        
    # Time Control
    st.subheader("🕰️ Time")
    
    current_time_int = st.session_state.char_mgr.get_time()
    
    # Format nicely (08:00 AM)
    am_pm = "AM" if current_time_int < 12 else "PM"
    disp_hour = current_time_int if current_time_int <= 12 else current_time_int - 12
    if disp_hour == 0: disp_hour = 12
    
    st.write(f"**Clock: {disp_hour}:00 {am_pm}**")
    
    if st.button("Wait 1 Hour (+Energy)"):
        # Advance time
        new_time = (current_time_int + 1) % 24
        st.session_state.char_mgr.set_time(new_time)
        
        # Restore energy
        st.session_state.char_mgr.update_stats(energy_delta=10)
        st.success("Time passes...")
        time.sleep(0.5)
        st.rerun()
    
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
                        config["example_dialogue"],
                        user_name=st.session_state.user_persona["name"],
                        lorebook=config.get("lorebook", {}),
                        past_events=st.session_state.char_mgr.get_recent_diary_entries(),
                        stats=st.session_state.char_mgr.get_stats(),
                        location=st.session_state.char_mgr.get_location(),
                        current_time_str=f"{st.session_state.char_mgr.get_time()}:00"
                    )
                    
                    # Check for offline progression (Initial Load)
                    offline_report = st.session_state.char_mgr.process_offline_time()
                    if offline_report:
                        st.toast(f"While you were gone: {offline_report}", icon="🕰️")
                        # Inject as system context
                        st.session_state.messages.append({"role": "system", "content": f"*[System: While the user was away, you {offline_report}]*"})
                        
                    st.success("Connected!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to load model: {e}")
        else:
            st.warning("Please download the model first using download_model.py")
            st.stop()

    if "editing_msg" not in st.session_state:
        st.session_state.editing_msg = None # {index: int, content: str}
    if "should_continue" not in st.session_state:
        st.session_state.should_continue = False

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
                    
                    # Audio Playback (if saved in session state or just generated)
                    if "audio" in message:
                        import base64
                        # Decode base64 to bytes for st.audio
                        try:
                            audio_bytes = base64.b64decode(message["audio"])
                            st.audio(audio_bytes, format="audio/mp3")
                        except Exception:
                            # Fallback if it was somehow stored raw or corrupted
                            pass
                    
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
    
    # Audio Input (Hearing)
    audio_val = st.audio_input("🎤 Speak to her")
    
    # Logic to handle audio input
    # We need to ensure we only transcribe NEW audio. 
    # st.audio_input returns the buffer.
    
    if "last_audio_id" not in st.session_state:
        st.session_state.last_audio_id = None
        
    if audio_val:
        # Use the buffer ID or similar as a unique tracker? 
        # Or just the object identity if it changes?
        # Streamlit re-creates the object on new recording.
        
        if audio_val != st.session_state.last_audio_id:
            with st.spinner("Listening..."):
                transcribed_text = st.session_state.hearing_mgr.transcribe(audio_val)
                if transcribed_text:
                    # Treat as user input
                    # We inject it into the chat logic below by setting a temporary variable
                    # that overrides the text input
                    st.session_state.audio_transcription = transcribed_text
                    st.session_state.last_audio_id = audio_val
                    st.rerun()
    
    # Image Input (Vision)
    with st.expander("📷 Show her something (Send Image)"):
        uploaded_vision_image = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"], key="vision_uploader")
        if uploaded_vision_image and st.button("Send Image"):
            with st.spinner("Analyzing image..."):
                from PIL import Image
                image = Image.open(uploaded_vision_image)
                
                # 1. Get Caption
                caption = st.session_state.vision_mgr.caption_image(image)
                
                # 2. Add to chat as user message with special formatting
                user_msg_content = f"[User showed an image: {caption}]"
                
                # 3. Append to history
                st.session_state.messages.append({"role": "user", "content": user_msg_content})
                
                # 4. Display immediately (we can't easily show the image inside the chat bubble in this loop, 
                # but we can show the text representation. 
                # Ideally, we'd store the image data in the message to render it, 
                # but for now text is enough for the AI.)
                
                # Let's try to store a small thumbnail or base64 if we want to render it later.
                # For now, let's just trigger the response.
                st.success(f"Sent: {caption}")
                st.session_state.should_regenerate = False # Ensure we don't regen previous
                # Rerun to show the new message and trigger AI
                st.rerun()

    # Continue Button (centered below chat)
    col_cont, _ = st.columns([1, 4])
    with col_cont:
        if st.button("🗣️ Let her speak"):
            st.session_state.should_continue = True
            st.rerun()

    if "audio_transcription" in st.session_state and st.session_state.audio_transcription:
        # Override user input with transcription
        user_input = st.session_state.audio_transcription
        # Clear it so we don't loop
        del st.session_state.audio_transcription
    else:
        user_input = st.chat_input("Say something...")
    
    if user_input or st.session_state.should_regenerate or st.session_state.should_continue or (st.session_state.messages and st.session_state.messages[-1]["content"].startswith("[User showed an image:")):
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
        
        # Handle Continue
        elif st.session_state.should_continue:
            # We treat this as a system push
            # But we need to trick the 'user' input logic or just skip to generation
            # Actually, the logic below expects a user message to be appended if we are not regenerating.
            # So we append a system note disguised as user role for the prompt? 
            # Or better: We append a system message, and then the AI responds to the history.
            
            user_input = "(The user listens intently...)"
            # Note: We used to append this to messages, but the logic below 
            # `if user_input or ...` enters this block.
            
            # If we just appended it in the button click, we wouldn't need this block.
            # But the button click just sets the flag and reruns.
            
            st.session_state.messages.append({"role": "system", "content": user_input})
            with st.chat_message("system"):
                st.markdown(f"*{user_input}*")
                
        elif st.session_state.messages and st.session_state.messages[-1]["content"].startswith("[User showed an image:"):
             # Image was just sent, so we don't need to append anything new.
             # Just set user_input to the image caption for context if needed, 
             # but the loop below uses history anyway.
             user_input = st.session_state.messages[-1]["content"]
             pass
                
        else:
            # Normal user input (Text)
            # Only append if it wasn't an image send (which appends its own message)
            # Wait, if we sent an image, `user_input` (chat_input) is likely None.
            # So we only enter here if `user_input` is NOT None.
            
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

        # Reset flags
        st.session_state.should_regenerate = False
        st.session_state.should_continue = False

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
            final_thought, final_speech, final_mood = st.session_state.waifu.get_last_thought_and_response()
            
            # Analyze Sentiment & Update Stats
            aff_delta, en_delta = st.session_state.waifu.analyze_sentiment(user_input)
            new_stats = st.session_state.char_mgr.update_stats(aff_delta, en_delta)
            
            # Update Emotion based on Model Output
            if final_mood and final_mood != "neutral":
                 st.session_state.current_emotion = final_mood
                 
            response_placeholder.markdown(final_speech)
            
            # Audio Generation
            audio_b64 = None
            if st.session_state.tts_enabled:
                with st.spinner("Generating Voice..."):
                    # Use final_speech (stripped of thoughts)
                    audio_b64 = st.session_state.voice_mgr.get_audio_base64(
                        final_speech,
                        voice=st.session_state.get("tts_voice", "en-US-AriaNeural"),
                        pitch=st.session_state.get("tts_pitch", "+0Hz"),
                        rate=st.session_state.get("tts_rate", "+0%")
                    )
                    if audio_b64:
                        import base64
                        # Decode base64 to bytes for st.audio
                        try:
                            audio_bytes = base64.b64decode(audio_b64)
                            st.audio(audio_bytes, format="audio/mp3")
                        except Exception:
                            pass
            
            msg_data = {"role": "assistant", "content": full_response}
            if audio_b64:
                msg_data["audio"] = audio_b64
                
            st.session_state.messages.append(msg_data)
            st.rerun() # Rerun to update the avatar in the left column
