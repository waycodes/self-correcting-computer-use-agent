"""SFT training script skeleton with LoRA config."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class LoRAConfig:
    """LoRA configuration for efficient fine-tuning."""

    r: int = 8  # LoRA rank
    alpha: int = 16  # LoRA alpha
    dropout: float = 0.1
    target_modules: list[str] = field(
        default_factory=lambda: ["q_proj", "v_proj"]
    )


@dataclass
class SFTConfig:
    """Configuration for SFT training."""

    model_name: str = "Qwen/Qwen2-VL-2B-Instruct"
    dataset_path: Path = Path("data/sft_dataset.jsonl")
    output_dir: Path = Path("checkpoints/sft")
    lora: LoRAConfig = field(default_factory=LoRAConfig)

    # Training hyperparameters
    batch_size: int = 4
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-4
    num_epochs: int = 3
    warmup_ratio: float = 0.1
    max_length: int = 2048

    # Checkpointing
    save_steps: int = 500
    eval_steps: int = 100
    logging_steps: int = 10


class SFTTrainer:
    """SFT trainer skeleton (actual training requires HF transformers)."""

    def __init__(self, config: SFTConfig) -> None:
        """Initialize trainer."""
        self.config = config
        self.model: Any = None
        self.tokenizer: Any = None

    def setup(self) -> None:
        """Setup model and tokenizer (stub)."""
        # In real implementation:
        # - Load base model
        # - Apply LoRA adapters
        # - Setup tokenizer
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

    def train(self) -> dict[str, Any]:
        """Run training (stub)."""
        # In real implementation:
        # - Load dataset
        # - Create data collator
        # - Setup Trainer
        # - Run training loop
        return {
            "status": "stub",
            "message": "Training requires HuggingFace transformers + PEFT",
            "config": {
                "model": self.config.model_name,
                "lora_r": self.config.lora.r,
                "epochs": self.config.num_epochs,
            },
        }

    def save_checkpoint(self, step: int) -> Path:
        """Save checkpoint (stub)."""
        checkpoint_dir = self.config.output_dir / f"checkpoint-{step}"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        return checkpoint_dir

    def load_checkpoint(self, checkpoint_dir: Path) -> None:
        """Load checkpoint (stub)."""
        pass


def create_default_config() -> SFTConfig:
    """Create default SFT configuration."""
    return SFTConfig()
