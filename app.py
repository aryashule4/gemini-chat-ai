import os
import logging
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API key from environment variable
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    logger.error("Environment variable GOOGLE_API_KEY belum diset.")
    # Don't raise here so app can still start (useful for health checks),
    # but endpoints will return error if key missing.
genai.configure(api_key=GOOGLE_API_KEY)

# Pilih model yang Anda punya akses (contoh: gemini-1.5-flash atau gemini-2.0-flash)
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
model = genai.GenerativeModel(MODEL_NAME)

app = Flask(__name__, template_folder="templates", static_folder="static")


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def generate():
    """
    JSON request:
    { "prompt": "Teks pertanyaan" }
    Response:
    { "reply": "jawaban" }
    """
    if not GOOGLE_API_KEY:
        return jsonify({"error": "Server belum dikonfigurasi dengan GOOGLE_API_KEY."}), 500

    data = request.get_json(silent=True)
    if not data or "prompt" not in data:
        return jsonify({"error": "Field 'prompt' diperlukan."}), 400

    prompt = str(data["prompt"]).strip()
    if not prompt:
        return jsonify({"error": "Prompt kosong."}), 400

    try:
        # Memanggil Gemini
        # generate_content menerima parameter yang lebih kaya; contoh sederhana:
        response = model.generate_content(prompt)

        # response.text biasanya berisi teks hasil model; fallback ke kandungan lain jika perlu
        text = getattr(response, "text", None)
        if not text:
            # beberapa versi API menyimpan text di response.candidates[0].output atau sejenis
            try:
                text = response.candidates[0].output[0].content[0].text
            except Exception:
                text = str(response)

        return jsonify({"reply": text})
    except Exception as e:
        logger.exception("Error saat memanggil Gemini")
        return jsonify({"error": "Terjadi error saat memproses permintaan.", "detail": str(e)}), 500


# Healthcheck (optional)
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    # Untuk development lokal
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
