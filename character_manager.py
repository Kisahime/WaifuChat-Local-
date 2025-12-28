import os
import json
import glob
from datetime import datetime

CHARACTERS_DIR = "./characters"

class CharacterManager:
    def __init__(self):
        self.current_character = None
        self.character_config = {}
        
    def list_characters(self):
        """Returns a list of available character names based on folders."""
        if not os.path.exists(CHARACTERS_DIR):
            return []
        
        # Get subdirectories in characters folder
        chars = [d for d in os.listdir(CHARACTERS_DIR) 
                if os.path.isdir(os.path.join(CHARACTERS_DIR, d))]
        return sorted(chars)

    def load_character(self, name):
        """Loads the config for a specific character."""
        config_path = os.path.join(CHARACTERS_DIR, name, "config.json")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config not found for character: {name}")
            
        with open(config_path, "r", encoding="utf-8") as f:
            self.character_config = json.load(f)
            self.current_character = name
            
        return self.character_config

    def save_character(self, name, config_data):
        """Saves or creates a character config."""
        char_dir = os.path.join(CHARACTERS_DIR, name)
        if not os.path.exists(char_dir):
            os.makedirs(char_dir)
            
        # Ensure history dir exists
        history_dir = os.path.join(char_dir, "history")
        if not os.path.exists(history_dir):
            os.makedirs(history_dir)

        config_path = os.path.join(char_dir, "config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
            
        return True

    def list_sessions(self):
        """Lists saved sessions for the current character."""
        if not self.current_character:
            return []
            
        history_dir = os.path.join(CHARACTERS_DIR, self.current_character, "history")
        if not os.path.exists(history_dir):
            return []
            
        files = glob.glob(os.path.join(history_dir, "*.json"))
        # Return filenames sorted by modified time (newest first)
        files.sort(key=os.path.getmtime, reverse=True)
        return [os.path.basename(f) for f in files]

    def save_session(self, history, session_name=None, user_persona=None):
        """Saves the current chat history to a JSON file."""
        if not self.current_character:
            return None
            
        history_dir = os.path.join(CHARACTERS_DIR, self.current_character, "history")
        if not os.path.exists(history_dir):
            os.makedirs(history_dir)
            
        if not session_name:
            # Generate a timestamped name
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            session_name = f"session_{timestamp}.json"
            
        if not session_name.endswith(".json"):
            session_name += ".json"
            
        file_path = os.path.join(history_dir, session_name)
        
        data = {
            "history": history,
            "user_persona": user_persona or {"name": "User", "description": ""}
        }
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            
        return session_name

    def load_session(self, filename):
        """Loads a specific chat history file."""
        if not self.current_character:
            return [], {}
            
        file_path = os.path.join(CHARACTERS_DIR, self.current_character, "history", filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Session file not found: {filename}")
            
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Handle backward compatibility with old saves (list only)
            if isinstance(data, list):
                return data, {"name": "User", "description": ""}
            return data.get("history", []), data.get("user_persona", {"name": "User", "description": ""})

    def get_avatar_for_emotion(self, emotion_text):
        """Returns the avatar emoji/image path for a given emotion text."""
        if not self.character_config or "avatar_emotion_map" not in self.character_config:
            return "👤"
            
        emotion_map = self.character_config["avatar_emotion_map"]
        
        # Simple keyword matching
        found_emotion = "neutral"
        
        # Check if the exact emotion is in the map
        if emotion_text in emotion_map:
            found_emotion = emotion_text
        else:
            # Fuzzy match
            for key in emotion_map.keys():
                if key in emotion_text.lower():
                    found_emotion = key
                    break
        
        result = emotion_map.get(found_emotion, emotion_map.get("neutral", "👤"))
        
        # Check if it's a file path
        if self.current_character and not result.startswith("http") and len(result) > 4 and "." in result:
             # It might be a local file in characters/<name>/avatars/
             potential_path = os.path.join(CHARACTERS_DIR, self.current_character, "avatars", result)
             if os.path.exists(potential_path):
                 return potential_path
                 
        return result

    def save_image(self, name, image_file, filename):
        """Saves an uploaded image to the character's avatars folder."""
        char_dir = os.path.join(CHARACTERS_DIR, name)
        avatars_dir = os.path.join(char_dir, "avatars")
        
        if not os.path.exists(avatars_dir):
            os.makedirs(avatars_dir)
            
        file_path = os.path.join(avatars_dir, filename)
        with open(file_path, "wb") as f:
            f.write(image_file.getbuffer())
            
        return filename

    def get_background_image(self):
        """Returns the background image path if configured."""
        if not self.character_config:
            return None
        
        bg_file = self.character_config.get("background_image")
        if not bg_file:
            return None
            
        if self.current_character:
             potential_path = os.path.join(CHARACTERS_DIR, self.current_character, "avatars", bg_file)
             if os.path.exists(potential_path):
                 return potential_path
        
        return None

    def get_lorebook(self):
        """Returns the lorebook dictionary from the config."""
        if not self.character_config:
            return {}
        return self.character_config.get("lorebook", {})

    def update_lore_entry(self, keyword, content):
        """Adds or updates a lorebook entry."""
        if not self.character_config:
            return False
            
        if "lorebook" not in self.character_config:
            self.character_config["lorebook"] = {}
            
        self.character_config["lorebook"][keyword] = content
        return self.save_character(self.current_character, self.character_config)

    def delete_lore_entry(self, keyword):
        """Deletes a lorebook entry."""
        if not self.character_config or "lorebook" not in self.character_config:
            return False
            
        if keyword in self.character_config["lorebook"]:
            del self.character_config["lorebook"][keyword]
            return self.save_character(self.current_character, self.character_config)
        return False

    def save_diary_entry(self, entry_text):
        """Saves a new diary entry for the current character."""
        if not self.current_character:
            return False
            
        char_dir = os.path.join(CHARACTERS_DIR, self.current_character)
        diary_path = os.path.join(char_dir, "diary.json")
        
        entries = []
        if os.path.exists(diary_path):
            with open(diary_path, "r", encoding="utf-8") as f:
                entries = json.load(f)
                
        new_entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "content": entry_text
        }
        entries.append(new_entry)
        
        with open(diary_path, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)
            
        return True

    def get_recent_diary_entries(self, limit=3):
        """Returns the most recent diary entries formatted for context injection."""
        if not self.current_character:
            return []
            
        char_dir = os.path.join(CHARACTERS_DIR, self.current_character)
        diary_path = os.path.join(char_dir, "diary.json")
        
        if not os.path.exists(diary_path):
            return []
            
        with open(diary_path, "r", encoding="utf-8") as f:
            entries = json.load(f)
            
        # Get last N entries
        recent = entries[-limit:]
        return recent

    def get_all_diary_entries(self):
        """Returns all diary entries."""
        if not self.current_character:
            return []
            
        char_dir = os.path.join(CHARACTERS_DIR, self.current_character)
        diary_path = os.path.join(char_dir, "diary.json")
        
        if not os.path.exists(diary_path):
            return []
            
        with open(diary_path, "r", encoding="utf-8") as f:
            entries = json.load(f)
        
        # Sort by date descending (newest first)
        return sorted(entries, key=lambda x: x['date'], reverse=True)
