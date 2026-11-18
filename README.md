# MediSense AI – User Features Package

This is a **new user-interface and workflow package** for the MediSense AI academic research prototype.

## Important
- This ZIP does **not** contain BioBERT, PubMedBERT, DeBERTa weights, tokenizers, or trained model code.
- It does **not** generate disease predictions yet. The analysis page records a local research session and clearly shows **Models not connected**.
- No accuracy, confidence score, or model output is fabricated.
- It is not a medical diagnostic or treatment tool.
- User-entered text is stored locally in `history.json` in plain text. Use synthetic/de-identified text only.

## Included user features
1. Dashboard overview
2. Guided symptom text entry, duration and self-reported severity
3. Input validation and character counter
4. Prediction-pending screen for model integration
5. Local history with individual delete and clear-all
6. Research-session comparison selection (records only; no prediction comparison until models are connected)
7. Searchable educational disease library
8. PDF export of submitted research session (not a diagnostic report)
9. Feedback page
10. Help, privacy and about pages
11. Responsive layout and navigation

## Run on Windows / VS Code
Open this extracted folder in VS Code, then in Terminal:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000/`.

If PowerShell blocks virtual-environment activation, you can skip activation and run:

```powershell
python -m pip install -r requirements.txt
python app.py
```

## Next model integration
After you verify the pages and workflows, integrate the three local trained models. Their folder structure and `config.json` label mappings must be inspected first. Keep the existing original project and model folders backed up.
