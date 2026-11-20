"""
CLIP Model Integration
AI Image Captioning System
"""

import os
import torch
from PIL import Image
from functools import lru_cache
from transformers import CLIPProcessor, CLIPModel


# Hugging Face pretrained model
MODEL_NAME = "openai/clip-vit-base-patch32"


# Candidate captions for image matching
CANDIDATE_CAPTIONS = [
    "A person standing outdoors.",
    "A person sitting on a chair.",
    "A person walking on a road.",
    "A group of people standing together.",
    "A dog playing in a garden.",
    "A cat sitting on a sofa.",
    "A bird sitting on a tree.",
    "A horse running in a field.",
    "A car parked on a road.",
    "A motorcycle on the street.",
    "A bus travelling on a road.",
    "An airplane flying in the sky.",
    "A beautiful landscape with mountains.",
    "A river flowing through a forest.",
    "A beach with blue ocean water.",
    "A sunset over the mountains.",
    "A city with tall buildings.",
    "A house surrounded by trees.",
    "A beautiful flower in a garden.",
    "A tree in a green forest.",
    "A plate of delicious food.",
    "A person eating food.",
    "A computer on a desk.",
    "A mobile phone on a table.",
    "A laptop placed on a desk.",
    "A book lying on a table.",
    "A football match on a field.",
    "A person riding a bicycle.",
    "A train travelling on railway tracks.",
    "A colorful painting on a wall.",
]


# Select available processing device
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# Load model only once with caching
@lru_cache(maxsize=1)
def load_clip_model():
    """
    Loads OpenAI CLIP model and processor.
    Cached in memory for optimal inference performance.
    Prioritizes locally cached files for offline operation.
    """
    print(f"Loading CLIP model '{MODEL_NAME}' on {DEVICE}...")

    try:
        # Load directly from local huggingface cache without network check
        processor = CLIPProcessor.from_pretrained(MODEL_NAME, local_files_only=True)
        model = CLIPModel.from_pretrained(MODEL_NAME, local_files_only=True)
    except Exception as e:
        print(f"Local files only load failed ({e}), attempting standard load...")
        processor = CLIPProcessor.from_pretrained(MODEL_NAME)
        model = CLIPModel.from_pretrained(MODEL_NAME)

    model.to(DEVICE)
    model.eval()

    print("CLIP model loaded successfully!")
    print("Processing device:", DEVICE)

    return model, processor


# Generate image caption
def generate_caption(image_path, custom_candidates=None, top_k=5):
    """
    Generates best matching caption for given image path or PIL Image.
    Returns:
        dict: {
            "caption": str,
            "confidence": float,
            "top_matches": list of dicts with {"caption": str, "confidence": float},
            "device": str
        }
    """
    # Load CLIP model
    model, processor = load_clip_model()

    # Determine candidate caption pool
    candidates = CANDIDATE_CAPTIONS
    if custom_candidates:
        if isinstance(custom_candidates, str):
            custom_list = [line.strip() for line in custom_candidates.splitlines() if line.strip()]
        elif isinstance(custom_candidates, (list, tuple)):
            custom_list = [str(c).strip() for c in custom_candidates if str(c).strip()]
        else:
            custom_list = []

        if len(custom_list) > 0:
            candidates = custom_list

    # Read uploaded image
    if isinstance(image_path, Image.Image):
        image = image_path.convert("RGB")
    else:
        with Image.open(image_path) as uploaded_image:
            image = uploaded_image.convert("RGB")

    # Prepare image and candidate captions
    inputs = processor(
        text=candidates,
        images=image,
        return_tensors="pt",
        padding=True
    )

    # Move inputs to selected device
    inputs = {
        key: value.to(DEVICE)
        for key, value in inputs.items()
    }

    # Calculate image-text similarity
    with torch.inference_mode():
        outputs = model(**inputs)
        probabilities = outputs.logits_per_image.softmax(dim=1)[0]

    # Find top-k matching captions
    k = min(top_k, len(candidates))
    top_probs, top_indices = torch.topk(probabilities, k=k)

    top_matches = []
    for prob, idx in zip(top_probs, top_indices):
        idx_val = idx.item()
        confidence = round(prob.item() * 100, 2)
        top_matches.append({
            "caption": candidates[idx_val],
            "confidence": confidence
        })

    best_caption = top_matches[0]["caption"]
    best_confidence = top_matches[0]["confidence"]

    print(f"Generated Caption: '{best_caption}' (Confidence: {best_confidence}%)")

    # Return prediction results
    return {
        "caption": best_caption,
        "confidence": best_confidence,
        "top_matches": top_matches,
        "device": str(DEVICE),
        "total_candidates": len(candidates)
    }
