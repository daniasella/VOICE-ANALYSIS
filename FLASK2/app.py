from flask import Flask, render_template, request, jsonify, send_from_directory
import joblib
import sys
import speech_recognition as sr
from gtts import gTTS
from fuzzywuzzy import fuzz
import tempfile, os, subprocess, time, logging, wave, csv

from model.rulebased import detect_umpatan, is_literal_animal_context, rule_based_sentiment
from preprocessing.normalization import text_normalization
from preprocessing.context_spelling import context_aware_spelling
from preprocessing.ngram_model import BigramLM

# ==============================
#   FIX PATH FOR PYINSTALLER
# ==============================
if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.abspath(".")

template_dir = os.path.join(base_dir, "templates")
static_dir = os.path.join(base_dir, "static")
model_dir = os.path.join(base_dir, "model")
preprocessing_dir = os.path.join(base_dir, "preprocessing")
ffmpeg_dir = os.path.join(base_dir, "ffmpeg")


def _ffmpeg_executable():
    """Return full path to ffmpeg executable if available in project, else 'ffmpeg'."""
    # Prefer bundled ffmpeg in ffmpeg/bin/ffmpeg(.exe)
    exe_name = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    bundled = os.path.join(ffmpeg_dir, "bin", exe_name)
    if os.path.exists(bundled):
        return bundled
    return "ffmpeg"

INDONESIAN_DICTIONARY = set()
try:
    with open(os.path.join(model_dir, "corpus2.txt"), "r", encoding="utf-8") as f:
        for line in f:
            word = line.strip().lower()
            if word and word.isalpha():  # Pastikan hanya kata alfabet
                INDONESIAN_DICTIONARY.add(word)
except FileNotFoundError:
    print("[WARNING] corpus2.txt not found. Using empty dict.", flush=True)
    INDONESIAN_DICTIONARY = {"terasi"}  # Fallback dasar

print(f"[INFO] Loaded {len(INDONESIAN_DICTIONARY)} words into Indonesian dictionary.", flush=True)

app = Flask(__name__,
            template_folder=template_dir,
            static_folder=static_dir)

# ==============================
#        LOAD MODEL
# ==============================
model = joblib.load(os.path.join(model_dir, "model3", "svm_model3.pkl"))
vectorizer = joblib.load(os.path.join(model_dir, "model3", "tfidf_vectorizer3.pkl"))
label_encoder = joblib.load(os.path.join(model_dir, "model3", "label_encoder.pkl"))
VOCAB = vectorizer.get_feature_names_out()

# ==============================
#   BUILD N-GRAM MODEL (ONCE)
# ==============================
# Ideal: corpus dari data latih
corpus_sentences = []   

correct = 0
total = 0

with open(os.path.join(model_dir, "data_training.csv"), encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        text = text_normalization(row["text"])
        corpus_sentences.append(text)
        X = vectorizer.transform([text])

        if X.nnz == 0:
            pred = "netral"
        else:
            pred = str(model.predict(X)[0])

        if pred.lower().strip() == row["sentimen"].lower().strip():
            correct += 1
        total += 1

accuracy = correct / total * 100
print("Akurasi dataset tambahan:", accuracy)

with open(os.path.join(model_dir, "corpus.txt"), encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            corpus_sentences.append(line)

bigram_lm = BigramLM(corpus_sentences)

print(f"[INFO] Bigram LM built from {len(corpus_sentences)} sentences", flush=True)

# ==============================
#        TTS FOLDER
# ==============================
TTS_FOLDER = os.path.join(app.static_folder, "tts")
os.makedirs(TTS_FOLDER, exist_ok=True)

# ==============================
#        ROUTES
# ==============================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/main')
def main_page():
    return render_template('main.html')

@app.route('/tts_opening')
def tts_opening():
    opening_text = "Halo, saya adalah sistem voice recognition untuk analisis sentimen!"
    filename = text_to_speech(opening_text, prefix="opening")
    return jsonify({"filename": filename})

# ==============================
#        TTS FUNCTION
# ==============================
def text_to_speech(text, prefix="tts"):
    tts = gTTS(text, lang="id")
    filename = f"{prefix}_{next(tempfile._get_candidate_names())}.mp3"
    path = os.path.join(TTS_FOLDER, filename)
    tts.save(path)
    return f"tts/{filename}"

# ==============================
#        ANALYZE (STT UTAMA)
# ==============================
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        audio_file = request.files['audio']

        temp_audio_path = tempfile.mktemp(suffix=".webm")
        temp_wav_path = tempfile.mktemp(suffix=".wav")

        audio_file.save(temp_audio_path)

        subprocess.run(
            [_ffmpeg_executable(), "-y", "-i", temp_audio_path, "-ac", "1", "-ar", "16000", temp_wav_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # ==============================
        #        AUDIO DURATION
        # ==============================
        with wave.open(temp_wav_path, 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            audio_duration = round(frames / float(rate), 2)

        r = sr.Recognizer()

        # ==============================
        #        STT EXECUTION TIME
        # ==============================
        start_time = time.perf_counter()

        with sr.AudioFile(temp_wav_path) as source:
            audio_data = r.record(source)
            raw_text = r.recognize_google(audio_data, language="id-ID")

        end_time = time.perf_counter()
        execution_time = round(end_time - start_time, 4)

        logging.info(
            f"[STT-Google] Duration: {audio_duration}s | Exec Time: {execution_time}s"
        )

        # ==============================
        #   TEXT PROCESSING
        # ==============================
        print("RAW TEXT       :", raw_text, flush=True)
        
        normalized_text = text_normalization(raw_text)
        final_text = context_aware_spelling(
            normalized_text,
            bigram_lm,
            VOCAB,
            INDONESIAN_DICTIONARY
        )
        print("FINAL TEXT     :", final_text, flush=True)

        # ==============================
        #   SENTIMENT DECISION LOGIC
        # ==============================

        # 1. Rule-based umpatan 
        tokens = final_text.split()

        if detect_umpatan(tokens):
            sentiment = "negatif"
            print("RULE-BASED: UMPATAN TERDETEKSI", flush=True)

        # 2. KONTEKS HEWAN → override SVM
        elif "anjing" in tokens and is_literal_animal_context(tokens):
            sentiment = "positif"
            print("RULE-BASED: KONTEKS HEWAN", flush=True)

        # 3. Rule-based formal sentence
        elif rule_based_sentiment(final_text) is not None:
            sentiment = rule_based_sentiment(final_text)
            print("RULE-BASED: FORMAL SENTENCE", flush=True)

        else:
             # 3. SVM (model 14k data)
            X = vectorizer.transform([final_text])
            print("TFIDF NON ZERO:", X.nnz, flush=True)

            if X.nnz == 0:
                sentiment = "netral"
            else:
                pred = model.predict(X)[0]
                sentiment = label_encoder.inverse_transform([pred])[0]
            print("sentiment     :", sentiment, flush=True)

        # ==============================
        #        TTS OUTPUT
        # ==============================
        output_filename = text_to_speech(
            f"Hasil analisis sentimen Anda adalah {sentiment}"
        )

        question_filename = text_to_speech(
            "Apakah ada lagi yang ingin Anda bicarakan?",
            prefix="question"
        )

        os.remove(temp_audio_path)
        os.remove(temp_wav_path)

        return jsonify({
            "text_raw": raw_text,
            "text_normalized": final_text,
            "sentiment": sentiment,
            "audio_duration": audio_duration,
            "execution_time": execution_time,
            "tts_audio": output_filename,
            "question_audio": question_filename
        })

    except Exception as e:
        return jsonify({"error": str(e)})

# ==============================
#        ANALYZE ANSWER
# ==============================
@app.route('/analyze_answer', methods=['POST'])
def analyze_answer():
    try:
        audio_file = request.files['audio']

        temp_audio_path = tempfile.mktemp(suffix=".webm")
        temp_wav_path = tempfile.mktemp(suffix=".wav")

        audio_file.save(temp_audio_path)

        subprocess.run(
            [_ffmpeg_executable(), "-y", "-i", temp_audio_path, "-ac", "1", "-ar", "16000", temp_wav_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        r = sr.Recognizer()
        with sr.AudioFile(temp_wav_path) as source:
            audio_data = r.record(source)
            answer_text = r.recognize_google(audio_data, language="id-ID").lower()

        os.remove(temp_audio_path)
        os.remove(temp_wav_path)

        # List kata untuk restart
        restart_words = ["ya", "iya", "yup", "oke", "lanjut", "bicara", "silahkan", "silakan", "mau", "lagi", "ya dong"]
        # List kata untuk exit (tidak, enggak, dll.)
        exit_words = ["tidak", "enggak", "ga", "no", "stop", "berhenti", "tidak deh", "ga deh", "ga dong", "tidak dong"]

        # Cek restart dengan fuzzy matching (threshold 80%) atau exact match
        for word in restart_words:
            if fuzz.ratio(answer_text, word) > 80 or word in answer_text:
                return jsonify({"action": "restart"})

        # Cek exit dengan fuzzy matching atau exact match
        for word in exit_words:
            if fuzz.ratio(answer_text, word) > 80 or word in answer_text:
                closing_filename = text_to_speech(
                    "Terima kasih, sampai jumpa!",
                    prefix="closing"
                )
                return jsonify({"action": "exit", "tts_audio": closing_filename})

        # Jika tidak match, unknown
        return jsonify({"action": "unknown", "text": answer_text})

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/wake_word', methods=['POST'])
def wake_word():
    try:
        audio_file = request.files['audio']

        temp_audio_path = tempfile.mktemp(suffix=".webm")
        temp_wav_path = tempfile.mktemp(suffix=".wav")

        audio_file.save(temp_audio_path)

        subprocess.run(
            [_ffmpeg_executable(), "-y", "-i", temp_audio_path, "-ac", "1", "-ar", "16000", temp_wav_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        r = sr.Recognizer()
        with sr.AudioFile(temp_wav_path) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language="id-ID").lower()

        os.remove(temp_audio_path)
        os.remove(temp_wav_path)

        print("WAKE WORD TEXT :", text, flush=True)
        
        # Fuzzy matching untuk toleransi (threshold 80%)
        wake_words = ["halo neo", "halo neu", "halo meo"]
        for word in wake_words:
            if fuzz.ratio(text, word) > 80:
                return jsonify({"wake": True})

        return jsonify({"wake": False})

    except Exception as e:
        print("Error in wake_word:", str(e), flush=True)
        return jsonify({"wake": False})

@app.route('/tts_silakan')
def tts_silakan():
    filename = text_to_speech("Silakan berbicara", prefix="prompt")
    return jsonify({"filename": filename})

# ==============================
#        TTS SERVE
# ==============================
@app.route('/tts/<path:filename>')
def tts_audio(filename):
    return send_from_directory(TTS_FOLDER, filename)

# ==============================
#        RUN APP
# ==============================
if __name__ == '__main__':
    app.run(debug=False)
