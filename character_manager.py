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

    def update_stats(self, affection_delta=0, energy_delta=0):
        """Updates character stats."""
        if not self.character_config:
            return
            
        if "stats" not in self.character_config:
            self.character_config["stats"] = {"affection": 0, "energy": 100}
            
        stats = self.character_config["stats"]
        stats["affection"] = max(0, min(100, stats.get("affection", 0) + affection_delta))
        stats["energy"] = max(0, min(100, stats.get("energy", 100) + energy_delta))
        
        self.save_character(self.current_character, self.character_config)
        return stats

    def get_stats(self):
        if not self.character_config:
            return {"affection": 0, "energy": 100}
        return self.character_config.get("stats", {"affection": 0, "energy": 100})

    def set_location(self, location_name):
        if not self.character_config:
            return
        self.character_config["current_location"] = location_name
        self.save_character(self.current_character, self.character_config)
        
    def get_location(self):
        if not self.character_config:
            return "Home"
        return self.character_config.get("current_location", "Home")

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

    def import_character_card(self, file_obj):
        """Imports a V2 Character Card (PNG) or JSON."""
        from PIL import Image
        import base64
        
        filename = file_obj.name
        content = file_obj.read()
        
        card_data = None
        
        # 1. Try JSON import
        if filename.endswith(".json"):
            try:
                data = json.loads(content)
                # Check if it's V2 spec (data inside 'data' or 'spec' or flat)
                if "data" in data:
                    card_data = data["data"]
                else:
                    card_data = data
            except:
                pass
                
        # 2. Try PNG import (V2 Spec uses tEXt chunk 'chara')
        elif filename.endswith(".png"):
            try:
                img = Image.open(file_obj)
                img.load() # Load metadata
                
                # Check for V2 'chara' chunk
                if "chara" in img.info:
                    # It's base64 encoded string
                    raw_data = base64.b64decode(img.info["chara"]).decode("utf-8")
                    data = json.loads(raw_data)
                    if "data" in data:
                        card_data = data["data"]
                    else:
                        card_data = data
                        
                # Check for V1 'ccv3' or similar (TavernAI) - simplistic fallback
                # ... skipping complex V1 parsing for now, focusing on V2
            except Exception as e:
                print(f"Error parsing PNG: {e}")
                pass
                
        if not card_data:
            return None, "Could not parse character card."
            
        # Map to WaifuChat format
        # V2 Spec: name, description, personality, scenario, first_mes, mes_example
        
        new_name = card_data.get("name", "Unknown")
        # Combine personality and description for our single 'description' field
        desc = card_data.get("description", "")
        pers = card_data.get("personality", "")
        full_desc = f"{desc}\n\nPersonality: {pers}".strip()
        
        scenario = card_data.get("scenario", "")
        # dialogue examples
        dialogue = card_data.get("mes_example", "")
        
        # Save Avatar Image
        # If imported from PNG, save that PNG
        # If JSON, we don't have an image, use default
        
        char_dir = os.path.join(CHARACTERS_DIR, new_name)
        if not os.path.exists(char_dir):
            os.makedirs(char_dir)
            
        avatars_dir = os.path.join(char_dir, "avatars")
        if not os.path.exists(avatars_dir):
            os.makedirs(avatars_dir)
            
        avatar_filename = "neutral.png"
        
        if filename.endswith(".png"):
            # Save the original card as the avatar
            # Reset file pointer
            file_obj.seek(0)
            with open(os.path.join(avatars_dir, avatar_filename), "wb") as f:
                f.write(file_obj.read())
        else:
            # No image provided
            avatar_filename = "👤" 
            
        # Create Config
        config = {
            "name": new_name,
            "description": full_desc,
            "scenario": scenario,
            "example_dialogue": dialogue,
            "avatar_emotion_map": {
                "neutral": avatar_filename
            }
        }
        
        self.save_character(new_name, config)
        return new_name, None
