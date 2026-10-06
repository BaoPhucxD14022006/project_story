import os
from dotenv import load_dotenv

load_dotenv()

class NVIDIA_Model:
    URL : str = "https://integrate.api.nvidia.com/v1"
    LLM_MODEL : str = "google/diffusiongemma-26b-a4b-it"
    SATEFY_MODEL : str = "google/diffusiongemma-26b-a4b-it"

class API_KEY:
    NVIDIA : str = os.getenv("NVIDIA_API_KEY")