from flask import Flask, render_template, request, send_file, session
from datetime import timedelta
import pickle
from reportlab.pdfgen import canvas

app = Flask(__name__)

app.secret_key = "copbot_secret"

# Session timeout
app.permanent_session_lifetime = timedelta(minutes=1)

# Load ML model
model = pickle.load(open("complaint_model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

latest_fir = ""

# English Questions
english_questions = [

    "What is your full name?",

    "What is your mobile number?",

    "What is your address?",

    "Describe your complaint in detail.",

    "Where did the incident happen?",

    "When did the incident happen?",

    "Do you know the suspect?",

    "Was there any witness present?",

    "Did you lose money or valuables?",

    "Do you have any evidence images or documents?"

]

# Tamil Questions
tamil_questions = [

    "உங்கள் முழுப்பெயர் என்ன?",

    "உங்கள் மொபைல் எண் என்ன?",

    "உங்கள் முகவரி என்ன?",

    "உங்கள் புகாரை விவரமாக கூறுங்கள்.",

    "சம்பவம் எங்கு நடந்தது?",

    "சம்பவம் எப்போது நடந்தது?",

    "சந்தேக நபரை நீங்கள் அறிவீர்களா?",

    "சாட்சி யாராவது இருந்தார்களா?",

    "பணம் அல்லது பொருள் இழப்பு ஏற்பட்டதா?",

    "உங்களிடம் ஆதார புகைப்படங்கள் உள்ளதா?"

]

@app.route("/", methods=["GET", "POST"])
def home():

    global latest_fir

    # Reset session on refresh
    if request.method == "GET":

        session.clear()

    # Initialize session
    if "step" not in session:

        session["step"] = 0

        session["answers"] = []

        session["chat_history"] = []

    if "language" not in session:

        session["language"] = "english"

    prediction = ""

    fir_text = ""

    # Select question language
    questions = english_questions

    if session["language"] == "tamil":

        questions = tamil_questions

    # Handle POST
    if request.method == "POST":

        # Language selection
        if "language" in request.form:

            session["language"] = request.form["language"]

            session["step"] = 0

            session["answers"] = []

            session["chat_history"] = []

            questions = english_questions

            if session["language"] == "tamil":

                questions = tamil_questions

            return render_template(
                "index.html",
                current_question=questions[0],
                chat_history=[],
                prediction="",
                fir_text=""
            )

        # User input
        user_input = request.form.get("complaint")

        if not user_input:

            return render_template(
                "index.html",
                current_question=questions[session["step"]],
                chat_history=session["chat_history"]
            )

        lower_input = user_input.lower()

        # Greeting handling
        if lower_input in ["hi", "hello", "hey"]:

            return render_template(
                "index.html",
                current_question="Hello Officer 👮 Please continue FIR registration.",
                chat_history=session["chat_history"]
            )

        # Thank you handling
        if "thanks" in lower_input:

            return render_template(
                "index.html",
                current_question="You're welcome Officer ✅",
                chat_history=session["chat_history"]
            )

        # Mobile validation
        if session["step"] == 1:

            if not user_input.isdigit() or len(user_input) != 10:

                return render_template(
                    "index.html",
                    current_question="❌ Please enter a valid 10-digit mobile number.",
                    chat_history=session["chat_history"]
                )

        # Store chat
        current_question = questions[session["step"]]

        session["chat_history"].append({

            "question": current_question,

            "answer": user_input

        })

        session["answers"].append(user_input)

        session["step"] += 1

        # FIR generation
        if session["step"] >= len(questions):

            complaint = session["answers"][3]

            complaint_vector = vectorizer.transform([complaint])

            prediction = model.predict(complaint_vector)[0]

            # Smart rules
            if "hack" in complaint.lower() or "bank" in complaint.lower():

                prediction = "Cybercrime"

            elif "stolen" in complaint.lower() or "missing" in complaint.lower():

                prediction = "Theft"

            elif "attack" in complaint.lower() or "assault" in complaint.lower():

                prediction = "Assault"

            else:

                prediction = "General Complaint"

            # FIR Text
            fir_text = f"""
==============================
        FIR REPORT
==============================

Complainant Name:
{session["answers"][0]}

Mobile Number:
{session["answers"][1]}

Address:
{session["answers"][2]}

Complaint Details:
{session["answers"][3]}

Incident Location:
{session["answers"][4]}

Incident Time:
{session["answers"][5]}

Suspect Information:
{session["answers"][6]}

Witness Details:
{session["answers"][7]}

Financial / Property Loss:
{session["answers"][8]}

Evidence Submitted:
{session["answers"][9]}

Predicted Crime Category:
{prediction}

Status:
Complaint Registered Successfully ✅

Generated By:
CopBot AI FIR Drafting Assistant
"""

            latest_fir = fir_text

            chat_history = session["chat_history"]

            session.clear()

            return render_template(
                "index.html",
                prediction=prediction,
                fir_text=fir_text,
                current_question="Conversation Completed ✅",
                chat_history=chat_history
            )

    # Current Question
    current_question = questions[session["step"]]

    return render_template(
        "index.html",
        current_question=current_question,
        prediction=prediction,
        fir_text=fir_text,
        chat_history=session["chat_history"]
    )

# PDF Download
@app.route("/download")
def download_pdf():

    pdf_file = "FIR_Report.pdf"

    c = canvas.Canvas(pdf_file)

    c.setFont("Helvetica-Bold", 18)

    c.drawString(150, 800, "AI GENERATED FIR REPORT")

    c.setFont("Helvetica", 12)

    y = 760

    for line in latest_fir.split("\n"):

        c.drawString(80, y, line)

        y -= 20

    c.save()

    return send_file(pdf_file, as_attachment=True)

# Run App
if __name__ == "__main__":

    app.run(debug=True)