
import os
import logging
from functools import lru_cache

import torch
import torch.nn.functional as F

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification
)


# --------------------------------------------------
# PATH CONFIGURATION
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

MODEL_PATHS = {
    "BioBERT": os.path.join(
        MODELS_DIR, "BioBERT_final", "BioBERT_final"
    ),
    "PubMedBERT": os.path.join(
        MODELS_DIR, "PubMedBERT_final", "PubMedBERT_final"
    ),
    "DeBERTa": os.path.join(
        MODELS_DIR, "DeBERTa_final", "DeBERTa_final"
    ),
}

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

logging.basicConfig(level=logging.INFO)


# --------------------------------------------------
# LABEL MAPPING
# --------------------------------------------------

def get_labels(config):

    mapping = config.id2label

    return [
        mapping.get(i, mapping.get(str(i), f"Class {i}"))
        for i in range(config.num_labels)
    ]


# --------------------------------------------------
# LOAD INDIVIDUAL MODELS
# --------------------------------------------------

@lru_cache(maxsize=3)
def load_single_model(name):

    if name not in MODEL_PATHS:
        raise ValueError(f"Unknown model: {name}")

    path = MODEL_PATHS[name]

    if not os.path.isdir(path):
        raise FileNotFoundError(
            f"{name} model folder not found: {path}"
        )

    logging.info("Loading %s from %s", name, path)

    tokenizer = AutoTokenizer.from_pretrained(
        path,
        local_files_only=True
    )

    model = AutoModelForSequenceClassification.from_pretrained(
        path,
        local_files_only=True,
        use_safetensors=True
    )

    model.to(DEVICE)
    model.eval()

    labels = get_labels(model.config)

    logging.info(
        "%s loaded successfully with %s labels",
        name,
        len(labels)
    )

    return {
        "tokenizer": tokenizer,
        "model": model,
        "labels": labels
    }


# --------------------------------------------------
# LOAD ALL THREE MODELS
# --------------------------------------------------

@lru_cache(maxsize=1)
def load_models():

    loaded = {}

    for name in MODEL_PATHS:
        loaded[name] = load_single_model(name)

    reference_labels = loaded["BioBERT"]["labels"]

    for name, item in loaded.items():

        if item["labels"] != reference_labels:
            raise ValueError(
                f"Class-label order mismatch in {name}. "
                "All three models must use the same labels "
                "in the same order."
            )

    if len(reference_labels) != 22:
        raise ValueError(
            f"Expected 22 disease labels, "
            f"but the models contain {len(reference_labels)}."
        )

    return loaded


# --------------------------------------------------
# MODEL STATUS
# --------------------------------------------------

def get_model_status():

    statuses = {}

    # First, check each model independently
    for name in MODEL_PATHS:

        try:
            item = load_single_model(name)

            statuses[name] = {
                "available": True,
                "message": (
                    f"Loaded successfully "
                    f"({len(item['labels'])} labels)"
                )
            }

        except Exception as e:

            logging.exception(
                "%s model loading failed", name
            )

            statuses[name] = {
                "available": False,
                "message": str(e)
            }

    # Then validate whether all three can work together
    if all(
        status["available"]
        for status in statuses.values()
    ):

        try:
            load_models()

            logging.info(
                "All three models are ready for Soft Voting."
            )

        except Exception as e:

            logging.exception(
                "Ensemble validation failed"
            )

            for name in statuses:
                statuses[name] = {
                    "available": False,
                    "message": f"Ensemble validation failed: {e}"
                }

    return statuses


# --------------------------------------------------
# THREE-MODEL SOFT VOTING
# --------------------------------------------------

def predict_ensemble(patient_text):

    patient_text = patient_text.strip()

    if not patient_text:
        raise ValueError("Please enter symptom text.")

    models = load_models()

    predictions = {}
    probability_vectors = []

    for name, item in models.items():

        tokenizer = item["tokenizer"]
        model = item["model"]

        inputs = tokenizer(
            patient_text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        )

        inputs = {
            key: value.to(DEVICE)
            for key, value in inputs.items()
        }

        with torch.no_grad():

            outputs = model(**inputs)

            probabilities = F.softmax(
                outputs.logits,
                dim=-1
            )[0]

        probability_vectors.append(probabilities)

        predicted_index = int(
            torch.argmax(probabilities).item()
        )

        predictions[name] = {
            "predicted_disease": (
                item["labels"][predicted_index]
            ),

            "confidence": round(
                float(probabilities[predicted_index].item()) * 100,
                2
            )
        }

    # Average the probability vectors
    ensemble_probabilities = torch.stack(
        probability_vectors
    ).mean(dim=0)

    best_index = int(
        torch.argmax(ensemble_probabilities).item()
    )

    labels = models["BioBERT"]["labels"]

    # Top five predictions
    top_indices = torch.argsort(
        ensemble_probabilities,
        descending=True
    )[:5]

    top_predictions = [

        {
            "disease": labels[int(index)],

            "score": round(
                float(ensemble_probabilities[index].item()) * 100,
                2
            )
        }

        for index in top_indices
    ]

    return {

        "predicted_disease": labels[best_index],

        "confidence": round(
            float(ensemble_probabilities[best_index].item()) * 100,
            2
        ),

        "model_predictions": predictions,

        "top_predictions": top_predictions,

        "ensemble_method": "Soft Voting",

        "number_of_models": len(models),

        "disease_categories": len(labels)

    }


