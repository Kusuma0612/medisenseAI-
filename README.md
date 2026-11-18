# MediSense AI

**Ensemble Transformer Framework for Disease Classification from Patient-Generated Text**

MediSense AI is an academic research prototype that uses transformer-based NLP models to explore disease classification from patient-generated symptom descriptions.

## Features

- Flask-based web application
- Patient-generated text input
- BioBERT, PubMedBERT and DeBERTa transformer models
- Soft-voting ensemble framework
- Dashboard and research session management
- Disease information library
- Prediction history and reports

## Technology Stack

- Python
- Flask
- HTML, CSS and JavaScript
- PyTorch
- Hugging Face Transformers

## Project Structure

- `app.py` – Flask application
- `model_service.py` – Model loading and prediction services
- `evaluate_ensemble.py` – Model evaluation
- `templates/` – HTML pages
- `static/` – CSS and JavaScript files
- `requirements.txt` – Python dependencies

## Run Locally

```bash
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000/` in your browser.

## Important Notes

- This is an academic research prototype, not a medical diagnostic tool.
- Predictions must not replace professional medical advice.
- Use synthetic or de-identified patient text only.
- Trained model weights and datasets are excluded from this Git repository.

## Future Scope

- Integration and validation of trained transformer models
- Regional language support
- Explainable AI
- Further evaluation using appropriate datasets
