"""SmolLM3 - CPU Optimized for Ryzen 9 5950X"""
import logging
import torch
from typing import Dict, Any
from .base_model import BaseModel

logger = logging.getLogger(__name__)

class SmolLM3(BaseModel):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config["name"], config["device"], config["quantization"])
        self.max_length = 2048
        self.temperature = 0.7
        self.system_prompt = """You are Nova, a helpful AI assistant. Be concise and clear."""
    
    def generate(self, prompt: str, **kwargs) -> str:
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        try:
            full_prompt = f"{self.system_prompt}\n\nUser: {prompt}\nAssistant:"
            
            inputs = self.tokenizer(
                full_prompt, 
                return_tensors="pt", 
                truncation=True, 
                max_length=self.max_length
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Optimized generation settings for CPU
            with torch.inference_mode():  # Faster than no_grad
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=kwargs.get("max_new_tokens", 150),
                    temperature=kwargs.get("temperature", 0.8),
                    do_sample=True,
                    top_p=0.9,
                    top_k=50,
                    repetition_penalty=1.1,  # Prevent loops
                    num_beams=1,  # Greedy for speed
                    early_stopping=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    use_cache=True  # KV cache enabled
                )
            
            response = self.tokenizer.decode(
                outputs[0][inputs["input_ids"].shape[1]:], 
                skip_special_tokens=True
            )
            return response.strip()
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return f"Error: {str(e)}"
