from flask import Flask, render_template, request

from matcher import check_symptoms

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/check", methods=["POST"])
def check():
    user_text = request.form.get("symptoms", "").strip()

    if not user_text:
        return render_template("index.html", error="Please describe how you're feeling.")

    result = check_symptoms(user_text)
    return render_template(
        "results.html",
        user_text=user_text,
        extracted_symptoms=result["extracted_symptoms"],
        matches=result["matches"],
        highest_urgency=result["highest_urgency"],
        highest_urgency_label=result["highest_urgency_label"],
    )


@app.route("/api/check", methods=["POST"])
def api_check():
    data = request.get_json(silent=True) or {}
    user_text = (data.get("symptoms") or "").strip()

    if not user_text:
        return {"error": "Field 'symptoms' is required."}, 400

    result = check_symptoms(user_text)
    return {
        "extracted_symptoms": result["extracted_symptoms"],
        "highest_urgency": result["highest_urgency"],
        "matches": [
            {
                "disease": m.disease.name,
                "score": round(m.score, 2),
                "matched_symptoms": m.matched_symptoms,
                "urgency": m.disease.urgency,
                "advice": m.disease.advice,
            }
            for m in result["matches"]
        ],
    }


if __name__ == "__main__":
    app.run(debug=True)