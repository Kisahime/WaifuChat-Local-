import torch
import whisper
import os
import numpy as np

class HearingManager:
    def __init__(self):
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def load_model(self):
        """Lazy loads the Whisper model."""
        if self.model is None:
            print(f"Loading Hearing Model (Whisper Base) on {self.device}...")
            try:
                # 'base' is a good balance for real-time CPU/GPU
                self.model = whisper.load_model("base", device=self.device)
                print("Hearing Model Loaded.")
            except Exception as e:
                print(f"Error loading hearing model: {e}")
                return False
        return True

    def transcribe(self, audio_file_obj):
        """
        Transcribes audio from a file-like object (wav/mp3).
        Args:
            audio_file_obj: The file object from st.audio_input
        Returns:
            str: The transcribed text.
        """
        if self.model is None:
            success = self.load_model()
            if not success:
                return "Error: Could not load hearing model."
        
        try:
            # Whisper expects a path or a numpy array. 
            # Since we have a file-like object from Streamlit, we might need to save it temp
            # or use a library to decode it to numpy.
            # Writing to a temp file is the safest/easiest cross-platform way for Whisper.
            
            temp_filename = "temp_input_audio.wav"
            with open(temp_filename, "wb") as f:
                f.write(audio_file_obj.read())
                
            # Transcribe
            result = self.model.transcribe(temp_filename)
            text = result["text"].strip()
            
            # Cleanup
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
                
            return text
            
        except Exception as e:
            print(f"Transcription error: {e}")
            return f"Error: {str(e)}"
