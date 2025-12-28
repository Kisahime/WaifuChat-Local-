import os
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

class WaifuAI:
    def __init__(self, model_path, context_size=8192, n_gpu_layers=-1):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}. Please run download_model.py first.")
        
        if Llama is None:
            raise ImportError("llama_cpp library not installed.")

        print(f"Loading model from {model_path}...")
        self.llm = Llama(
            model_path=model_path,
            n_ctx=context_size,
            n_gpu_layers=n_gpu_layers, # -1 means all layers to GPU
            verbose=False
        )
        self.history = []
        self.system_prompt = ""
        self.lorebook = {}

    def set_persona(self, name, description, scenario, example_dialogue, user_name="User", lorebook=None, past_events=None):
        self.lorebook = lorebook or {}
        
        # Format past events (diary entries)
        past_events_text = ""
        if past_events:
            past_events_text = "\n### Past Events (Diary)\n"
            for entry in past_events:
                past_events_text += f"- [{entry['date']}] {entry['content']}\n"
        
        # Inject current time
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        
        self.system_prompt = f"""You are an expert actor that can fully immerse yourself into any role given. You do not break character for any reason.
Currently your role is {name}, which is described in detail below.
As {name}, continue the exchange with {user_name}.
Current Date/Time: {current_time}

### Character Description
{description}

### Scenario
{scenario}
{past_events_text}
### Instructions
1. Analyze the user's input ({user_name}) and your current emotional state.
2. Output your internal thoughts in <thought> tags.
3. Respond to {user_name} in character.
4. At the VERY END of your response, on a new line, output your current mood in brackets, e.g., [Mood: Happy] or [Mood: Angry].

### Example Dialogue
{example_dialogue}
"""

    def generate_diary_entry(self, character_name, user_name):
        """Generates a diary entry based on the current history."""
        if not self.history:
            return None
            
        # Create a summary prompt
        prompt = "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
        prompt += f"You are {character_name}. Write a short diary entry (3-5 sentences) summarizing the recent conversation with {user_name}. Write in the first person. Do not use <thought> tags. Focus on what you felt and what happened.<|eot_id|>"
        
        # Add recent history (last 10 messages max to save tokens)
        recent_history = self.history[-10:]
        for msg in recent_history:
             role = "user" if msg["role"] == "user" else "assistant"
             # Strip thoughts for the summary prompt to reduce noise
             content = msg['content']
             if "<thought>" in content:
                 content = content.split("</thought>")[-1]
             prompt += f"<|start_header_id|>{role}<|end_header_id|>\n\n{content}<|eot_id|>"
             
        prompt += f"<|start_header_id|>user<|end_header_id|>\n\nWrite your diary entry now.<|eot_id|>"
        prompt += "<|start_header_id|>assistant<|end_header_id|>\n\n"
        
        # Generate
        output = self.llm(
            prompt,
            max_tokens=300,
            stop=["<|eot_id|>"],
            temperature=0.7
        )
        
        return output['choices'][0]['text'].strip()

    def _get_active_lore(self, user_input):
        """Scans input and recent history for lorebook keywords."""
        if not self.lorebook:
            return ""
            
        # Context to scan: User input + last 2 messages
        scan_text = user_input.lower()
        for msg in self.history[-2:]:
            scan_text += " " + msg['content'].lower()
            
        relevant_entries = []
        for keyword, content in self.lorebook.items():
            if keyword.lower() in scan_text:
                relevant_entries.append(f"{keyword}: {content}")
                
        if not relevant_entries:
            return ""
            
        return "\n".join(relevant_entries)

    def _trim_history(self, max_tokens=6000):
        """Trims history to fit within context window, keeping recent messages."""
        # Simple heuristic: 1 token ~= 4 chars. 
        # This is a rough estimation to avoid expensive tokenization on every turn.
        current_est_tokens = sum(len(m['content']) for m in self.history) / 3
        
        while current_est_tokens > max_tokens and len(self.history) > 2:
            # Remove the oldest pair of messages (User + AI)
            self.history.pop(0) 
            if self.history and self.history[0]['role'] == 'assistant':
                 self.history.pop(0) # Ensure we start with user
            current_est_tokens = sum(len(m['content']) for m in self.history) / 3

    def generate_response(self, user_input, temperature=0.9, top_p=0.95, min_p=0.05, repetition_penalty=1.1, top_k=40):
        # Trim history before generating
        self._trim_history()
        
        # Check for Lorebook entries
        active_lore = self._get_active_lore(user_input)
        current_system_prompt = self.system_prompt
        
        if active_lore:
            current_system_prompt += f"\n\n### Relevant World Info\n{active_lore}"
        
        # Construct the prompt using Llama 3 format
        prompt = "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
        prompt += current_system_prompt + "<|eot_id|>"
        
        for msg in self.history:
            role = "user" if msg["role"] == "user" else "assistant"
            prompt += f"<|start_header_id|>{role}<|end_header_id|>\n\n{msg['content']}<|eot_id|>"
            
        prompt += f"<|start_header_id|>user<|end_header_id|>\n\n{user_input}<|eot_id|>"
        prompt += "<|start_header_id|>assistant<|end_header_id|>\n\n"

        # Stream the response
        stream = self.llm(
            prompt,
            max_tokens=512,
            stop=["<|eot_id|>", "User:"],
            stream=True,
            temperature=temperature,
            top_p=top_p,
            min_p=min_p,
            repeat_penalty=repetition_penalty,
            top_k=top_k
        )
        
        full_response = ""
        for output in stream:
            chunk = output['choices'][0]['text']
            full_response += chunk
            yield chunk
            
        # Update history with the full response (thoughts + speech)
        self.history.append({"role": "user", "content": user_input})
        self.history.append({"role": "assistant", "content": full_response})

    def regenerate_last(self):
        """Removes the last assistant message so it can be regenerated."""
        if self.history and self.history[-1]['role'] == 'assistant':
            self.history.pop()
            return True
        return False
        
    def edit_message(self, index, new_content):
        """Edits a message at a specific index."""
        if 0 <= index < len(self.history):
            self.history[index]['content'] = new_content
            return True
        return False

    def get_last_thought_and_response(self):
        """Helper to parse the last message into thought, speech, and mood."""
        if not self.history:
            return None, None, "neutral"
            
        last_msg = self.history[-1]['content']
        thought = ""
        mood = "neutral"
        speech = last_msg
        
        # Extract Thought
        if "<thought>" in last_msg and "</thought>" in last_msg:
            start = last_msg.find("<thought>") + len("<thought>")
            end = last_msg.find("</thought>")
            thought = last_msg[start:end].strip()
            speech = last_msg[end+len("</thought>"):].strip()
            
        # Extract Mood (e.g., [Mood: Happy])
        import re
        mood_match = re.search(r'\[Mood:\s*([a-zA-Z0-9_\s]+)\]', speech, re.IGNORECASE)
        if mood_match:
            mood = mood_match.group(1).strip().lower()
            # Remove the mood tag from speech so user doesn't see it
            speech = speech.replace(mood_match.group(0), "").strip()
            
        return thought, speech, mood

    def clear_history(self):
        self.history = []
