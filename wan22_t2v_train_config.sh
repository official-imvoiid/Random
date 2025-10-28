# =================================================================
#     Optimized Configuration for Wan 2.2 LoRA Training
# =================================================================
# This configuration is optimized for powerful GPUs (A40/H100)
# and includes all crucial parameters for dual-model training.

# --- Model & Task Specification ---
# Specifies the Wan 2.2 model architecture. Use 't2v-A14B' for the 14B T2V model.
TASK="t2v-A14B"

# --- Core LoRA Parameters ---
# Rank (dimension) of the LoRA. 32 is a good balance.
LORA_RANK=32
# Alpha is often set to the same value as Rank for stable training.
LORA_ALPHA=32

# --- Training Schedule ---
# Total number of epochs. Aim for a total of 2000-4000 steps.
MAX_EPOCHS=100
# Save a checkpoint every N epochs.
SAVE_EVERY=2

# --- Optimizer Settings ---
# Learning rate. 8e-5 is rather slow and considerate training. A simple character Lora might only need 2e-4 or so (faster, less accurate).
LEARNING_RATE=2e-4
# Dynamically adjusts the learning rate during training. 'polynomial' is the stable default.
LR_SCHEDULER="polynomial"
# Optimizer algorithm. 'adamw' is the stable default.
OPTIMIZER_TYPE="adamw"

# --- Performance & Memory Optimization (Crucial for 14B models) ---
# Use 'fp16' as required by the base model.
MIXED_PRECISION="fp16"
# ESSENTIAL for training on <48GB VRAM.
FP8_BASE=true
# Gradient Accumulation Steps. Simulates a larger batch size to save VRAM.
GRADIENT_ACCUMULATION_STEPS=4
# Number of CPU threads for data loading.
MAX_DATA_LOADER_N_WORKERS=4

# --- Dataset Paths ---
IMAGE_DATASET_DIR="/workspace/image_dataset_here"
VIDEO_DATASET_DIR="/workspace/video_dataset_here"
CAPTION_EXT=".txt"

# --- Resolution Settings ---
# 512,512 is a safe default. Higher resolutions like 768,768 can be used on powerful GPUs.
RESOLUTION_LIST="823, 1216"

# --- IMAGE ONLY Settings ---
IMAGE_NUM_REPEATS=4
IMAGE_BATCH_SIZE=1 

# --- VIDEO ONLY Settings --- example: You have 10 Images and 5 Videos - 2 Video Repeats can balance that
VIDEO_NUM_REPEATS=1
TARGET_FRAMES="1, 49"

# --- Output Metadata ---
AUTHOR="voiid"

# =================================================================
#     Wan 2.2 DUAL-LORA SPECIFIC SETTINGS
# =================================================================
# --- Configuration for HIGH-NOISE LoRA ---
TITLE_HIGH="NameHere_HighNoise"
SEED_HIGH=42
MIN_TIMESTEP_HIGH=875
MAX_TIMESTEP_HIGH=1000

# --- Configuration for LOW-NOISE LoRA ---
TITLE_LOW="NameHere_LowNoise"
SEED_LOW=43
MIN_TIMESTEP_LOW=0
MAX_TIMESTEP_LOW=875
