# Review Radar

A Flask web app that predicts customer-review sentiment, explains the prediction with Gemini, and drafts a polite customer reply.

## Features
- Review text input with character count
- Sentiment label and confidence percentage
- Gemini-generated explanation and suggested reply
- Copy suggested reply
- Responsive dashboard UI

## Run locally

1. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   # Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   # macOS/Linux:
   source venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and add your Gemini API key.
   The app still runs without a key, but displays fallback AI text.

4. Start the server:

   ```bash
   python app.py
   ```

5. Open http://127.0.0.1:5000

## Connect your ML model later

In `app.py`, replace the body of `predict_sentiment(review)` with your pipeline call.

The function must return:

```python
{"label": "Positive", "confidence": 94.2}
```

`label` must be `Positive` or `Negative`; `confidence` must be a percentage from 0 to 100.

For example, if your model returns a class and probabilities:

```python
prediction = model.predict([review])[0]
probabilities = model.predict_proba([review])[0]
confidence = float(max(probabilities)) * 100
label = "Positive" if prediction == 1 else "Negative"
return {"label": label, "confidence": confidence}
```

Adjust the class mapping (`1` / `0`) to match how your model was trained.

## API

`POST /api/analyze`

Request:

```json
{"review": "The product is excellent and delivery was fast."}
```

Response:

```json
{
  "sentiment": "Positive",
  "confidence": 94.2,
  "explanation": "...",
  "reply": "..."
}
```

The current sentiment predictor is a simple keyword-based demo only. Do not treat its output as a real model prediction. Replace it with your trained pipeline before presenting the results as ML-powered.
