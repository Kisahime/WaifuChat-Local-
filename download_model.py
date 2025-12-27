import os
from huggingface_hub import hf_hub_download

# Configuration
REPO_ID = "bartowski/L3-8B-Stheno-v3.2-GGUF"
FILENAME = "L3-8B-Stheno-v3.2-Q4_K_M.gguf"
LOCAL_DIR = "./models"

def download_model():
    print(f"Downloading {FILENAME} from {REPO_ID}...")
    
    if not os.path.exists(LOCAL_DIR):
        os.makedirs(LOCAL_DIR)
        
    try:
        model_path = hf_hub_download(
            repo_id=REPO_ID,
            filename=FILENAME,
            local_dir=LOCAL_DIR,
            local_dir_use_symlinks=False
        )
        print(f"\nSuccess! Model downloaded to: {model_path}")
        print("You can now run the app.")
    except Exception as e:
        print(f"\nError downloading model: {e}")

if __name__ == "__main__":
    download_model()
