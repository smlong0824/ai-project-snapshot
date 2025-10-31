"""SmolVLM2 - Vision model"""
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from PIL import Image
import torch
from .base_model import BaseModel

logger = logging.getLogger(__name__)

class SmolVLM2(BaseModel):
    """SmolVLM2 - Vision and multimodal tool"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config["name"], config["device"], config["quantization"])
        self.processor = None
    
    def load(self) -> bool:
        try:
            from transformers import AutoProcessor
            if not super().load():
                return False
            self.processor = AutoProcessor.from_pretrained(self.model_name, trust_remote_code=True)
            return True
        except Exception as e:
            logger.error(f"Failed to load SmolVLM2: {e}")
            return False
    
    def generate(self, prompt: str, image_path: Optional[str] = None, **kwargs) -> str:
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        try:
            image = None
            if image_path and Path(image_path).exists():
                image = Image.open(image_path).convert("RGB")
            
            inputs = self.processor(text=prompt, images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.inference_mode():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=kwargs.get("max_new_tokens", 512),
                    do_sample=True,
                    temperature=0.7,
                    pad_token_id=self.processor.tokenizer.eos_token_id
                )
            
            response = self.processor.decode(outputs[0], skip_special_tokens=True)
            return response.strip()
        except Exception as e:
            logger.error(f"SmolVLM2 generation error: {e}")
            return f"Error: {str(e)}"
