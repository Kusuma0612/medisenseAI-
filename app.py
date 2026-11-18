
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, send_file
)

from datetime import datetime
from collections import Counter

import json
import os
import io

from model_service import (
    predict_ensemble,
    get_model_status
)


# --------------------------------------------------
# APPLICATION CONFIGURATION
# --------------------------------------------------

app = Flask(__name__)
app.secret_key = "change-this-local-demo-key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HISTORY_FILE = os.path.join(
    BASE_DIR, "history.json"
)


# --------------------------------------------------
# DISEASE LIBRARY
# --------------------------------------------------

DISEASES = [

    ("Allergy", "An immune response to a substance that is usually harmless."),
    ("Anemia", "A condition involving reduced healthy red blood cells or hemoglobin."),
    ("Anxiety", "A condition involving persistent worry or fear."),
    ("Arthritis", "Conditions affecting joints, often involving pain or stiffness."),
    ("Asthma", "A condition in which airways can become inflamed and narrowed."),
    ("Bronchitis", "Inflammation of the bronchial tubes."),
    ("COVID-19", "An infectious illness caused by SARS-CoV-2."),
    ("Chronic Kidney Disease", "A long-term condition involving reduced kidney function."),
    ("Common Cold", "A common viral infection affecting the upper respiratory tract."),
    ("Dementia", "Conditions affecting memory and cognitive abilities."),
    ("Depression", "A mental health condition affecting mood and daily activities."),
    ("Dermatitis", "Inflammation of the skin."),
    ("Diabetes", "Conditions affecting blood glucose regulation."),
    ("Epilepsy", "A neurological condition involving recurrent seizures."),
    ("Food Poisoning", "Illness caused by contaminated food or drink."),
    ("Gastritis", "Inflammation of the stomach lining."),
    ("Heart Disease", "Conditions affecting the heart."),
    ("Hypertension", "Persistently elevated blood pressure."),
    ("IBS", "A gastrointestinal condition involving recurring abdominal symptoms."),
    ("Influenza", "A contagious respiratory illness caused by influenza viruses."),
    ("Liver Disease", "Conditions affecting the liver."),
    ("Migraine", "A neurological condition that can cause recurring headaches."),
    ("Obesity", "A complex health condition involving excess body fat."),
    ("Parkinson's", "A progressive neurological condition affecting movement."),
    ("Pneumonia", "An infection that inflames air sacs in the lungs."),
    ("Sinusitis", "Inflammation of the tissue lining the sinuses."),
    ("Stroke", "A medical emergency involving interrupted blood flow to the brain."),
    ("Thyroid Disorder", "A condition affecting thyroid hormone function."),
    ("Tuberculosis", "An infectious disease most often affecting the lungs."),
    ("Ulcer", "A sore that develops on an organ or tissue lining.")

]


# --------------------------------------------------
# HISTORY FUNCTIONS
# --------------------------------------------------

def load_history():

    if not os.path.exists(HISTORY_FILE):
        return []

    try:

        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (OSError, json.JSONDecodeError):

        return []


def save_history(rows):

    with open(
        HISTORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            rows,
            file,
            indent=2,
            ensure_ascii=False
        )


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@app.route("/")
def dashboard():

    history_rows = load_history()

    statuses = get_model_status()

    # Check each model independently
    all_available = all(
        item["available"]
        for item in statuses.values()
    )

    model_status = (
        "Connected"
        if all_available
        else "Unavailable"
    )

    return render_template(

        "dashboard.html",

        count=len(history_rows),

        diseases=len(DISEASES),

        model_status=model_status,

        model_statuses=statuses

    )


# --------------------------------------------------
# NEW ANALYSIS
# --------------------------------------------------

@app.route("/analysis", methods=["GET", "POST"])
def analysis():

    if request.method == "POST":

        patient_text = request.form.get(
            "patient_text", ""
        ).strip()

        duration = request.form.get(
            "duration", ""
        ).strip()

        severity = request.form.get(
            "severity", ""
        ).strip()

        age = request.form.get("age", "").strip()

        gender = request.form.get("gender", "").strip()

        height = request.form.get("height", "").strip()

        weight = request.form.get("weight", "").strip()

        symptom_onset = request.form.get(
            "symptom_onset", ""
        ).strip()

        symptom_frequency = request.form.get(
            "symptom_frequency", ""
        ).strip()

        symptom_checklist = request.form.getlist(
            "symptom_checklist"
        )

        additional_symptoms = request.form.get(
            "additional_symptoms", ""
        ).strip()

        symptom_timeline = request.form.get(
            "symptom_timeline", ""
        ).strip()

        medications = request.form.get(
            "medications", ""
        ).strip()

        allergies = request.form.get(
            "allergies", ""
        ).strip()

        health_conditions = request.form.get(
            "health_conditions", ""
        ).strip()

        if len(patient_text) < 10:

            flash(
                "Please enter a more descriptive text "
                "(at least 10 characters).",
                "error"
            )

            return render_template("analysis.html")

        if len(patient_text) > 3000:

            flash(
                "Please keep the main symptom text "
                "under 3,000 characters.",
                "error"
            )

            return render_template("analysis.html")

        model_input_parts = [patient_text]

        if symptom_checklist:

            model_input_parts.append(
                "Selected symptoms: "
                + ", ".join(symptom_checklist)
            )

        if additional_symptoms:

            model_input_parts.append(
                "Additional symptoms: "
                + additional_symptoms
            )

        if symptom_timeline:

            model_input_parts.append(
                "Symptom timeline: "
                + symptom_timeline
            )

        model_input_text = "\n".join(
            model_input_parts
        )

        if len(model_input_text) > 3000:

            flash(
                "The combined symptom description is too long. "
                "Please shorten the additional information.",
                "error"
            )

            return render_template("analysis.html")

        # Three-model Soft Voting
        try:

            result = predict_ensemble(
                model_input_text
            )

        except Exception:

            app.logger.exception(
                "Model prediction failed"
            )

            flash(
                "Model prediction could not be completed. "
                "Please check the model folders and terminal error.",
                "error"
            )

            return render_template("analysis.html")

        record = {

            "id": datetime.now().strftime(
                "%Y%m%d%H%M%S%f"
            ),

            "created": datetime.now().strftime(
                "%d %b %Y, %I:%M %p"
            ),

            "patient_text": patient_text,

            "model_input_text": model_input_text,

            "duration": duration or "Not provided",

            "severity": severity or "Not provided",

            "age": age or "Not provided",

            "gender": gender or "Not provided",

            "height": height or "Not provided",

            "weight": weight or "Not provided",

            "symptom_onset": symptom_onset or "Not provided",

            "symptom_frequency": (
                symptom_frequency or "Not provided"
            ),

            "symptom_checklist": symptom_checklist,

            "additional_symptoms": (
                additional_symptoms or "Not provided"
            ),

            "symptom_timeline": (
                symptom_timeline or "Not provided"
            ),

            "medications": medications or "Not provided",

            "allergies": allergies or "Not provided",

            "health_conditions": (
                health_conditions or "Not provided"
            ),

            "status": "Models connected - prediction generated",

            "result": result

        }

        rows = load_history()

        rows.insert(0, record)

        save_history(rows[:100])

        return render_template(
            "results.html",
            record=record,
            result=result
        )

    return render_template("analysis.html")


# --------------------------------------------------
# PREDICTION HISTORY
# --------------------------------------------------

@app.route("/history")
def history():

    return render_template(
        "history.html",
        rows=load_history()
    )


@app.route(
    "/history/delete/<record_id>",
    methods=["POST"]
)
def delete_history(record_id):

    rows = [

        row for row in load_history()

        if row.get("id") != record_id

    ]

    save_history(rows)

    flash(
        "The selected local record was deleted.",
        "success"
    )

    return redirect(
        url_for("history")
    )


@app.route("/history/clear", methods=["POST"])
def clear_history():

    save_history([])

    flash(
        "Local history was cleared.",
        "success"
    )

    return redirect(
        url_for("history")
    )


# --------------------------------------------------
# MODEL COMPARISON
# --------------------------------------------------

@app.route("/compare")
def compare():

    rows = load_history()

    comparison_rows = []

    for row in rows:

        result = row.get("result", {})

        predictions = result.get(
            "model_predictions", {}
        )

        biobert = predictions.get(
            "BioBERT", {}
        ).get(
            "predicted_disease",
            "Not available"
        )

        pubmedbert = predictions.get(
            "PubMedBERT", {}
        ).get(
            "predicted_disease",
            "Not available"
        )

        deberta = predictions.get(
            "DeBERTa", {}
        ).get(
            "predicted_disease",
            "Not available"
        )

        ensemble = result.get(
            "predicted_disease",
            "Not available"
        )

        model_outputs = [

            value

            for value in [
                biobert,
                pubmedbert,
                deberta
            ]

            if value != "Not available"

        ]

        if len(model_outputs) < 3:

            comment = (
                "Comparison incomplete: one or more model outputs "
                "are missing."
            )

            agreement = "Incomplete"

        else:

            counts = Counter(model_outputs)

            highest_agreement = max(
                counts.values()
            )

            if highest_agreement == 3:

                comment = (
                    "All three models agree on the same predicted class."
                )

                agreement = "3 out of 3 agree"

            elif highest_agreement == 2:

                comment = (
                    "Two models agree, while one model gives "
                    "a different prediction."
                )

                agreement = "2 out of 3 agree"

            else:

                comment = (
                    "All three models produced different predictions."
                )

                agreement = "No agreement"

            if ensemble not in model_outputs:

                comment += (
                    " The ensemble prediction differs from all "
                    "individual model predictions."
                )

            elif (
                counts[ensemble] == highest_agreement
                and highest_agreement < 3
            ):

                comment += (
                    " The ensemble prediction matches a "
                    "majority-supported class."
                )

        comparison_rows.append({

            "date": row.get("created", "N/A"),

            "patient_text": row.get(
                "patient_text", "N/A"
            ),

            "biobert": biobert,

            "pubmedbert": pubmedbert,

            "deberta": deberta,

            "ensemble": ensemble,

            "agreement": agreement,

            "comment": comment

        })

    return render_template(
        "compare.html",
        rows=comparison_rows
    )


# --------------------------------------------------
# AI INTELLIGENCE LAB
# --------------------------------------------------

@app.route(
    "/ai-intelligence-lab",
    methods=["GET", "POST"]
)
def ai_intelligence_lab():

    rows = load_history()

    what_if_result = None

    original_text = ""

    edited_text = ""

    original_result = None

    if request.method == "POST":

        original_text = request.form.get(
            "original_text", ""
        ).strip()

        edited_text = request.form.get(
            "edited_text", ""
        ).strip()

        if len(edited_text) < 10:

            flash(
                "Please enter at least 10 characters "
                "for comparison.",
                "error"
            )

        elif len(edited_text) > 3000:

            flash(
                "Please keep the edited text under "
                "3,000 characters.",
                "error"
            )

        elif original_text and (
            len(original_text) < 10
            or len(original_text) > 3000
        ):

            flash(
                "Original text must contain 10 to 3,000 characters.",
                "error"
            )

        else:

            try:

                what_if_result = predict_ensemble(
                    edited_text
                )

                if original_text:

                    original_result = predict_ensemble(
                        original_text
                    )

            except Exception:

                app.logger.exception(
                    "AI Intelligence Lab prediction failed"
                )

                what_if_result = None

                original_result = None

                flash(
                    "Unable to complete the What-If comparison. "
                    "Please check the terminal for details.",
                    "error"
                )

    return render_template(

        "ai_intelligence_lab.html",

        rows=rows,

        what_if_result=what_if_result,

        original_result=original_result,

        original_text=original_text,

        edited_text=edited_text

    )


# --------------------------------------------------
# DISEASE LIBRARY
# --------------------------------------------------

@app.route("/disease-library")
def disease_library():

    query = request.args.get(
        "q", ""
    ).strip().lower()

    filtered = [

        (name, description)

        for name, description in DISEASES

        if query in name.lower()
        or query in description.lower()

    ]

    return render_template(

        "disease_library.html",

        diseases=filtered,

        query=query

    )


# --------------------------------------------------
# ABOUT
# --------------------------------------------------

@app.route("/about")
def about():

    return render_template("about.html")


# --------------------------------------------------
# HELP
# --------------------------------------------------

@app.route("/help")
def help_page():

    return render_template("help.html")


# --------------------------------------------------
# PRIVACY
# --------------------------------------------------

@app.route("/privacy")
def privacy():

    return render_template("privacy.html")


# --------------------------------------------------
# FEEDBACK
# --------------------------------------------------

@app.route("/feedback", methods=["GET", "POST"])
def feedback():

    if request.method == "POST":

        flash(
            "Thank you. Feedback is recorded as a local prototype confirmation.",
            "success"
        )

        return redirect(
            url_for("feedback")
        )

    return render_template("feedback.html")


# --------------------------------------------------
# REPORTS
# --------------------------------------------------

@app.route("/reports")
def reports():

    return render_template(
        "reports.html",
        rows=load_history()
    )


# --------------------------------------------------
# PDF REPORT EXPORT
# --------------------------------------------------

@app.route("/reports/export/<record_id>")
def export_report(record_id):

    record = next(

        (
            row for row in load_history()

            if row.get("id") == record_id
        ),

        None

    )

    if not record:

        flash(
            "Record not found.",
            "error"
        )

        return redirect(
            url_for("reports")
        )

    try:

        from reportlab.lib.pagesizes import A4

        from reportlab.pdfgen import canvas

    except ImportError:

        flash(
            "PDF export requires ReportLab. "
            "Run: python -m pip install reportlab",
            "error"
        )

        return redirect(
            url_for("reports")
        )

    buffer = io.BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=A4
    )

    pdf.setTitle(
        "MediSense AI Research Session"
    )

    page_width, page_height = A4

    y = page_height - 40

    def write_line(text, bold=False, size=10):

        nonlocal y

        if y < 55:

            pdf.showPage()

            y = page_height - 40

        pdf.setFont(
            "Helvetica-Bold" if bold else "Helvetica",
            size
        )

        pdf.drawString(

            50,

            y,

            str(text).encode(
                "latin-1", "replace"
            ).decode("latin-1")[:105]

        )

        y -= 17

    write_line(
        "MediSense AI - Research Session",
        bold=True,
        size=17
    )

    y -= 10

    write_line(
        "Date: " + str(record.get("created", ""))
    )

    write_line(
        "Status: " + str(record.get("status", ""))
    )

    y -= 8

    write_line(
        "PATIENT INFORMATION",
        bold=True,
        size=12
    )

    for label, key in [

        ("Age", "age"),

        ("Gender", "gender"),

        ("Height (cm)", "height"),

        ("Weight (kg)", "weight"),

        ("Severity", "severity"),

        ("Duration (Days)", "duration"),

        ("Symptom Onset", "symptom_onset"),

        ("Symptom Frequency", "symptom_frequency"),

    ]:

        write_line(
            f"{label}: {record.get(key, 'Not provided')}"
        )

    y -= 8

    write_line(
        "SYMPTOM INFORMATION",
        bold=True,
        size=12
    )

    write_line("Selected Symptoms:")

    checklist = record.get(
        "symptom_checklist", []
    )

    write_line(

        ", ".join(checklist)
        if checklist
        else "Not provided"

    )

    for label, key in [

        ("Additional Symptoms", "additional_symptoms"),

        ("Symptom Timeline", "symptom_timeline"),

        ("Current Medications", "medications"),

        ("Known Allergies", "allergies"),

        ("Existing Health Conditions", "health_conditions"),

    ]:

        write_line(label + ":")

        value = str(
            record.get(key, "Not provided")
        )

        for i in range(0, len(value), 95):

            write_line(
                value[i:i + 95]
            )

    y -= 8

    write_line(
        "PATIENT-GENERATED TEXT",
        bold=True,
        size=12
    )

    patient_text = record.get(
        "patient_text", ""
    )

    for i in range(0, len(patient_text), 95):

        write_line(
            patient_text[i:i + 95]
        )

    y -= 8

    result = record.get("result")

    if result:

        write_line(
            "SOFT VOTING ENSEMBLE RESULT",
            bold=True,
            size=12
        )

        write_line(
            "Ensemble output: "
            + str(result.get("predicted_disease", "N/A"))
        )

        write_line(
            "Model score: "
            + str(result.get("confidence", "N/A"))
            + "%"
        )

        y -= 8

        write_line(
            "INDIVIDUAL MODEL OUTPUTS",
            bold=True,
            size=11
        )

        for model_name, prediction in result.get(
            "model_predictions", {}
        ).items():

            write_line(

                f"{model_name}: "
                f"{prediction.get('predicted_disease', 'N/A')} "
                f"({prediction.get('confidence', 'N/A')}%)"

            )

    y -= 12

    write_line(
        "Academic research prototype only. Not for diagnosis or treatment.",
        bold=True,
        size=9
    )

    write_line(
        "Model scores are not clinically validated probabilities.",
        size=8
    )

    pdf.save()

    buffer.seek(0)

    return send_file(

        buffer,

        as_attachment=True,

        download_name="MediSense_Research_Session.pdf",

        mimetype="application/pdf"

    )


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=False,

        use_reloader=False

    )
