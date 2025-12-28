import edge_tts
import asyncio
import os
import tempfile

class VoiceManager:
    def __init__(self):
        self.output_file = "temp_audio.mp3"
        # Pre-defined list of high quality voices
        self.VOICES = {
            "Aria (Female)": "en-US-AriaNeural",
            "Guy (Male)": "en-US-GuyNeural",
            "Jenny (Female)": "en-US-JennyNeural",
            "Ana (Child Female)": "en-US-AnaNeural",
            "Christopher (Male)": "en-US-ChristopherNeural",
            "Eric (Male)": "en-US-EricNeural",
            "Michelle (Female)": "en-US-MichelleNeural",
            "Roger (Male)": "en-US-RogerNeural",
        }
        
    async def generate_audio(self, text, output_path, voice="en-US-AriaNeural", pitch="+0Hz", rate="+0%"):
        """Generates audio from text using edge-tts."""
        if not text:
            return False
            
        try:
            communicate = edge_tts.Communicate(text, voice, pitch=pitch, rate=rate)
            await communicate.save(output_path)
            return True
        except Exception as e:
            print(f"TTS Error: {e}")
            return False

    def get_audio_base64(self, text, voice="en-US-AriaNeural", pitch="+0Hz", rate="+0%"):
        """Synchronous wrapper to get base64 audio for Streamlit."""
        import base64
        
        # Streamlit runs in a loop, so we need a new loop for async if not present
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        # Use a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            temp_path = fp.name
            
        success = loop.run_until_complete(self.generate_audio(text, temp_path, voice, pitch, rate))
        
        if success and os.path.exists(temp_path):
            with open(temp_path, "rb") as f:
                data = f.read()
            os.remove(temp_path)
            return base64.b64encode(data).decode()
        
        return None
