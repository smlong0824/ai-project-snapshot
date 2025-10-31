"""Base model - Optimized for Zen 3 CPU + Ampere GPU"""
import logging
import os
from abc import ABC, abstractmethod
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

logger = logging.getLogger(__name__)

class BaseModel(ABC):
    def __init__(self, model_name: str, device: str, quantization: str = None):
        self.model_name = model_name
        self.device = device
        self.quantization = quantization
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
    
    def load(self) -> bool:
        try:
            logger.info(f"Loading {self.model_name} on {self.device} with {self.quantization} quantization...")
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name, 
                trust_remote_code=True,
                use_fast=True  # Use fast tokenizer
            )
            
            model_kwargs = {
                "trust_remote_code": True,
                "low_cpu_mem_usage": True,
            }
            
            # Quantization config
            if self.quantization == "8bit":
                quantization_config = BitsAndBytesConfig(
                    load_in_8bit=True,
                    llm_int8_enable_fp32_cpu_offload=True
                )
                model_kwargs["quantization_config"] = quantization_config
                model_kwargs["device_map"] = {"": self.device}
                
            elif self.quantization == "4bit":
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,  # Double quantization for memory
                    bnb_4bit_quant_type="nf4"  # NormalFloat4 for better accuracy
                )
                model_kwargs["quantization_config"] = quantization_config
                model_kwargs["device_map"] = "auto"
                
                # Flash Attention 2 for GPU
                    
            else:
                model_kwargs["torch_dtype"] = torch.float32 if self.device == "cpu" else torch.float16
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_kwargs
            )
            
            # PyTorch 2.0 compilation for speed (optional)
            # Set environment variable NOVA_DISABLE_TORCH_COMPILE=1 to disable
            if hasattr(torch, 'compile') and not os.getenv("NOVA_DISABLE_TORCH_COMPILE"):
                try:
                    logger.info("Applying torch.compile() optimization...")
                    self.model = torch.compile(self.model, mode="reduce-overhead")
                except Exception as _e:
                    logger.warning(f"torch.compile() failed or is unsupported: {_e}")
            
            if not self.quantization and self.device == "cpu":
                self.model = self.model.to("cpu")
            
            self.is_loaded = True
            logger.info(f"✓ Loaded {self.model_name} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load {self.model_name}: {e}")
            return False
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        pass
    
    def unload(self):
        if self.model:
            del self.model
            del self.tokenizer
            torch.cuda.empty_cache()
            self.is_loaded = False
