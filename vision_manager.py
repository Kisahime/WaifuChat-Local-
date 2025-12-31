import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

class VisionManager:
    def __init__(self):
        self.processor = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def load_model(self):
        """Lazy loads the BLIP model to save VRAM when not in use."""
        if self.model is None:
            print(f"Loading Vision Model (BLIP Large) on {self.device}...")
            try:
                # Upgraded to 'large' model for better detail
                self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
                self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large").to(self.device)
                print("Vision Model Loaded.")
            except Exception as e:
                print(f"Error loading vision model: {e}")
                return False
        return True

    def caption_image(self, image):
        """
        Generates a caption for the given PIL Image.
        Args:
            image (PIL.Image): The image to process.
        Returns:
            str: The generated caption.
        """
        if self.model is None:
            success = self.load_model()
            if not success:
                return "Error: Could not load vision model."
            
        # Preprocess
        # conditional generation: passing "a photography of" helps guide the model
        text = "a detailed description of" 
        inputs = self.processor(image, text, return_tensors="pt").to(self.device)
        
        # Generate with better parameters for detail
        out = self.model.generate(
            **inputs, 
            max_new_tokens=100,
            min_length=20,
            num_beams=5,  # Beam search for better quality
            repetition_penalty=1.2
        )
        
        # Decode
        caption = self.processor.decode(out[0], skip_special_tokens=True)
        return caption
