import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Replace this function with your trained sentiment model later.
def predict_sentiment(review: str) -> dict:
    """
    Temporary demo predictor.
    Expected return:
      {"label": "Positive" or "Negative", "confidence": float}
    confidence is a percentage from 0 to 100.
    """
    positive_words = {"good", "great", "excellent", "amazing", "love", "perfect",
                      "fast", "helpful", "recommend", "worth", "best", "happy"}
    negative_words = {"bad", "poor", "terrible", "awful", "hate", "broken",
                      "slow", "waste", "disappointed", "worst", "refund", "damaged"}
    words = set(review.lower().replace(".", " ").replace(",", " ").split())
    score = len(words & positive_words) - len(words & negative_words)

    if score > 0:
        return {"label": "Positive", "confidence": min(97.0, 70.0 + score * 6)}
    if score < 0:
        return {"label": "Negative", "confidence": min(97.0, 70.0 + abs(score) * 6)}
    return {"label": "Positive", "confidence": 50.0}


def generate_ai_content(review: str, sentiment: str) -> dict:
    """Generate explanation and a customer-facing reply with Gemini."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {
            "explanation": "Gemini is not configured yet. Add GEMINI_API_KEY to your .env file to generate an explanation.",
            "reply": "Thank you for sharing your feedback. We appreciate you taking the time to let us know about your experience."
        }

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        prompt = f"""
You are assisting a customer-support team. Analyze the customer review below.
Predicted sentiment from our sentiment model: {sentiment}

Review:
{review}

Return exactly these two sections:
EXPLANATION:
Explain briefly, using evidence from the review, why this sentiment fits. Do not claim facts not present in the review.

SUGGESTED_REPLY:
Write a polite, concise, professional reply from the product/company. Acknowledge the customer's experience. If negative, show empathy and offer a reasonable next step without promising a refund, replacement, or outcome. If positive, thank the customer.
"""
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=prompt
        )
        output = response.text or ""
        explanation = output
        reply = "Thank you for sharing your feedback. We appreciate your support."
        if "SUGGESTED_REPLY:" in output:
            before, after = output.split("SUGGESTED_REPLY:", 1)
            explanation = before.replace("EXPLANATION:", "").strip()
            reply = after.strip()
        else:
            explanation = output.replace("EXPLANATION:", "").strip()

        return {"explanation": explanation, "reply": reply}
    except Exception:
        app.logger.exception("Gemini generation failed")
        return {
            "explanation": "The AI explanation could not be generated right now. Please check your Gemini API configuration and try again.",
            "reply": "Thank you for taking the time to share your feedback. We appreciate hearing from our customers."
        }


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/api/analyze")
def analyze():
    data = request.get_json(silent=True) or {}
    review = (data.get("review") or "").strip()

    if not review:
        return jsonify({"error": "Please enter a product review first."}), 400
    if len(review) > 5000:
        return jsonify({"error": "Review is too long. Please keep it under 5,000 characters."}), 400

    prediction = predict_sentiment(review)
    ai_content = generate_ai_content(review, prediction["label"])

    return jsonify({
        "sentiment": prediction["label"],
        "confidence": round(float(prediction["confidence"]), 1),
        "explanation": ai_content["explanation"],
        "reply": ai_content["reply"]
    })


if __name__ == "__main__":
    app.run(debug=True)
