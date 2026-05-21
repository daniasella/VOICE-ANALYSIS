FLASK2 adalah sistem berbasis web yang dibuat menggunakan Flask untuk melakukan analisis sentimen suara ke suara Voice-to-Voice Sentiment Analysis dalam Bahasa Indonesia.
Sistem menerima input suara dari pengguna, kemudian:

1. Mengubah suara menjadi teks (Speech to Text)
2. Melakukan preprocessing teks
3. Menganalisis sentimen menggunakan model SVM
4. Menampilkan hasil sentimen
5. Mengubah hasil menjadi suara kembali (Text to Speech)

---

Fitur Utama

Input suara langsung dari microphone
Wake word detection
Speech Recognition Bahasa Indonesia
Text Normalization
Context Aware Spelling Correction
Analisis Sentimen SVM
Rule Based Sentiment Detection
Output suara hasil analisis

---

Software:

Python
Flask
Scikit-learn 1.7.1
SpeechRecognition
gTTS
NLTK
Pandas
NumPy

---

Struktur Folder

FLASK2/
│── app.py
│── requirements.txt
│── venv/
│── templates/
│   ├── index.html
│   └── main.html
│── static/
│   ├── css/
│   ├── js/
│   └── tts/
│── model/
│   ├── model3/
│   │   ├── svm_model3.pkl
│   │   ├── tfidf_vectorizer3.pkl
│   │   └── label_encoder.pkl
│   ├── corpus.txt
│   ├── rulebased.py
│   └── data_training.csv
│── preprocessing/
│   ├── normalization.py
│   ├── context_spelling.py
│   ├── lexicon.py
│   ├── spelling_candidate.py
│   └── ngram_model.py

Cara Menjalankan Project

1. Transfer Project
2. Buat Virtual Environment (python -m venv venv)
3. Aktifkan Virtual Environment (venv\Scripts\activate)
4. Install Semua Library(pip install -r requirements.txt)
5. Jalankan Program (python app.py)
6. Buka Browser (http://127.0.0.1:5000)

PASTIKAN:
Microphone aktif
Speaker aktif
Koneksi internet (untuk Google Speech Recognition & gTTS)
FFmpeg terinstall

---

Sistem akan menampilkan:
Teks hasil pengenalan suara
Hasil sentimen
Suara hasil analisis

---

Model dilatih menggunakan 15k dataset sentimen Bahasa Indonesia yang telah melalui preprocessing dan pelabelan manual
Kelas sentimen: Positif, Negatif, dan Netral

---

## Pengembang
Nama: UMMU KHUZAIFAH
Program Studi: Teknik Informatika
Universitas: UNIVERSITAS WAHID HASYIM SEMARANG

---

## Catatan
Project ini dibuat untuk keperluan tugas akhir mengenai implementasi Voice Recognition dan Sentiment Analysis berbasis Machine Learning
