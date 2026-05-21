/* ==============================
   GLOBAL STATE
============================== */
let mediaRecorder;
let audioChunks = [];
let isSystemActive = true;
let standbyInterval = null;
let wakeLock = false; // ⛔ mencegah wake word double trigger
let silenceTimer = null;
let retryCount = 0;  // Counter untuk retry rekaman
let answerRetryCount = 0;

//const MAX_RECORD_DURATION = 7000; // detik rekaman utama
const ANSWER_DURATION = 4000;     // detik jawaban ya/tidak
const SILENCE_LIMIT = 3000; // 3 detik
const SILENCE_THRESHOLD = 0.02; // sensitivitas suara
const MAX_RETRY = 3;  // Maksimal retry jika error
const MAX_ANSWER_RETRY = 4;  // Maksimal retry jawaban tidak dikenali

const recordBtn = document.getElementById("recordBtn");
const resultDiv = document.getElementById("result");
const ttsPlayer = document.getElementById("ttsPlayer");
const wave = document.getElementById("wave");

/* ==============================
   MAIN RECORD (AUTO TIMER)
============================== */
recordBtn.onclick = async () => {
  if (!isSystemActive) return;
  startMainRecording();
};

/* ==============================
   PROCESS MAIN AUDIO
============================== */
async function processMainAudio() {
  const blob = new Blob(audioChunks, { type: "audio/webm" });
  const formData = new FormData();
  formData.append("audio", blob, "record.webm");

  resultDiv.innerHTML = "Menganalisis...";

  const res = await fetch("/analyze", { method: "POST", body: formData });
  const data = await res.json();

  if (data.error) {
    console.error("Error dari server:", data.error);
    resultDiv.innerHTML = `<p style="color:red;"> Error: ${data.error}. Mencoba mendengarkan ulang...</p>`;
      
    if (retryCount < MAX_RETRY) {
        retryCount++;
        setTimeout(() => {
          console.log(`🔄 Retry rekaman ke-${retryCount}`);
          startMainRecording();  // Rekam ulang otomatis
        }, 2000);  // Tunggu 2 detik sebelum retry
      } else {
        resultDiv.innerHTML += `<p> Maksimal retry tercapai. Kembali ke standby.</p>`;
        retryCount = 0;  // Reset counter
        isSystemActive = false;
        startWakeWordStandby();  // Kembali ke wake word
      }
      return;
    }

    // Reset counter jika berhasil
    retryCount = 0;
    
  // ⛔ Jika STT menghasilkan undefined / kosong
  if (
    !data.text_raw ||
    data.text_raw === "undefined" ||
    data.text_raw.trim() === ""
  ) {
    console.warn("🔇 STT undefined, rekam ulang...");

    resultDiv.innerHTML = "<p>🔇 Suara tidak terdengar, silakan bicara ulang...</p>";

    setTimeout(() => {
      startMainRecording(); // ⬅️ LANGSUNG REKAM ULANG
    }, 800);

    return; // ⛔ STOP agar TTS tidak jalan
  }

  resultDiv.innerHTML = `
    <p><strong>Teks:</strong> ${data.text_normalized}</p>
    <p><strong>Sentimen:</strong> ${data.sentiment}</p>
  `;

  // TTS hasil
  ttsPlayer.src = "/tts/" + data.tts_audio.split("tts/")[1];
  await ttsPlayer.play();

  ttsPlayer.onended = async () => {
    ttsPlayer.src = "/tts/" + data.question_audio.split("tts/")[1];
    await ttsPlayer.play();

    ttsPlayer.onended = () => startAnswerRecording();
  };
}

/* ==============================
   ANSWER RECORD (YA / TIDAK)
============================== */
async function startAnswerRecording() {
  if (!isSystemActive) return;

  resultDiv.innerHTML += "<p>⏳ Menunggu jawaban (ya / tidak)...</p>";

  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const rec = new MediaRecorder(stream, { mimeType: "audio/webm;codecs=opus" });
  let chunks = [];

  rec.ondataavailable = e => chunks.push(e.data);
  rec.start();

  setTimeout(() => rec.stop(), ANSWER_DURATION);

  rec.onstop = async () => {
    stream.getTracks().forEach(t => t.stop());

    const blob = new Blob(chunks, { type: "audio/webm" });
    const fd = new FormData();
    fd.append("audio", blob, "answer.webm");

    const res = await fetch("/analyze_answer", { method: "POST", body: fd });
    const data = await res.json();

    /* === JAWABAN YA === */
    if (data.action === "restart") {
      const promptRes = await fetch("/tts_silakan");
      const prompt = await promptRes.json();

      ttsPlayer.src = "/tts/" + prompt.filename.split("tts/")[1];
      await ttsPlayer.play();

      ttsPlayer.onended = () => {
        resultDiv.innerHTML = "";
        recordBtn.click(); // restart
      };
      return;
    }

    /* === JAWABAN TIDAK === */
    if (data.action === "exit") {
      isSystemActive = false;

      ttsPlayer.src = "/tts/" + data.tts_audio.split("tts/")[1];
      await ttsPlayer.play();

      resultDiv.innerHTML += `
        <p>👋 Terima kasih, sampai jumpa!</p>
        <p>Katakan 'HALO NEO' untuk memulai lagi.</p>`;

      startWakeWordStandby();
      return;
    }

    /* === SILENT / TIDAK DIKENALI → LOOP LAGI === */
    resultDiv.innerHTML += "<p>⚠️ Jawaban tidak terdengar, silakan jawab ya atau tidak.</p>";

    setTimeout(() => {
      startAnswerRecording(); // 🔁 LOOP TANPA BATAS
    }, 500);
  };
}
  
/* ==============================
   WAKE WORD STANDBY
============================== */
function startWakeWordStandby() {
  if (standbyInterval) return;

  console.log("🔇 Sistem standby (wake word aktif)");

  standbyInterval = setInterval(async () => {
    if (isSystemActive || wakeLock) return;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const rec = new MediaRecorder(stream, { mimeType: "audio/webm;codecs=opus" });
      let chunks = [];

      rec.ondataavailable = e => chunks.push(e.data);
      rec.start();

      setTimeout(() => rec.stop(), 3000);  // Rekaman 3 detik untuk toleransi

      rec.onstop = async () => {
        stream.getTracks().forEach(t => t.stop());

        const blob = new Blob(chunks, { type: "audio/webm" });
        const fd = new FormData();
        fd.append("audio", blob, "wake.webm");

        console.log("📡 Mengirim audio wake word ke server...");

        const res = await fetch("/wake_word", {
          method: "POST",
          body: fd
        });

        const data = await res.json();
        console.log("📥 Response dari server:", data);

        if (data.wake === true && !wakeLock) {
          wakeLock = true;
          console.log("🔥 WAKE WORD DETECTED");

          clearInterval(standbyInterval);
          standbyInterval = null;

          isSystemActive = true;
          recordBtn.disabled = false;
          recordBtn.textContent = "🎙 Mendengarkan...";

          resultDiv.innerHTML = "<p>Suara terdeteksi. Mendengarkan ulang...</p>";

          // TTS sambutan (ubah teks menjadi lebih pendek)
          const resTTS = await fetch("/tts_silakan");  // Tetap gunakan endpoint yang sama, tapi ubah di server jika perlu
          const tts = await resTTS.json();

          ttsPlayer.src = "/tts/" + tts.filename.split("tts/")[1];
          await ttsPlayer.play();

          ttsPlayer.onended = () => {
            console.log("🎵 TTS selesai, memulai rekaman otomatis...");  // Logging debug
            wakeLock = false;  // Reset sebelum rekaman
            startMainRecording();  // ⬅️ LANGSUNG MULAIREKAM ULANG TANPA KLIK
          };
        }
      };
    } catch (error) {
      console.error("Error accessing microphone in standby:", error);
      clearInterval(standbyInterval);
      standbyInterval = null;
    }
  }, 3000);  // Interval 3 detik
}

/* ==============================
   MAIN RECORDING FUNCTION
============================== */
async function startMainRecording() {
  console.log("🎙 Memulai rekaman utama otomatis...");  // Logging debug
  if (!isSystemActive) {
    console.warn("Sistem tidak aktif, rekaman dibatalkan.");
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm;codecs=opus" });
    audioChunks = [];

    // Inisialisasi Web Audio API untuk analisis volume
    const audioContext = new AudioContext();
    const source = audioContext.createMediaStreamSource(stream);
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 2048;  // Ukuran FFT untuk analisis cepat

    source.connect(analyser);

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

    mediaRecorder.onstop = async () => {
      stream.getTracks().forEach(t => t.stop());
      audioContext.close();
      wave.classList.remove("recording");
      recordBtn.textContent = "🎙 Mulai Bicara";
      await processMainAudio();
    };

    mediaRecorder.start();
    wave.classList.add("recording");
    recordBtn.textContent = "🎙 Mendengarkan...";

    detectSilence(analyser);

  } catch (error) {
    console.error("Error starting main recording:", error);
    resultDiv.innerHTML = "<p>❌ Gagal mengakses mikrofon untuk bicara. Periksa permission browser.</p>";
    // Jika gagal, kembalikan ke standby jika perlu
    isSystemActive = false;
    startWakeWordStandby();
  }
}

/* ==============================
   TIMER SILENCE DETECTION
============================== */
function detectSilence(analyser) {
  const data = new Uint8Array(analyser.fftSize);
  analyser.getByteTimeDomainData(data);

  let sum = 0;
  for (let i = 0; i < data.length; i++) {
    sum += Math.abs(data[i] - 128);
  }

  const volume = sum / data.length / 128;

  if (volume > SILENCE_THRESHOLD) {
    // ADA suara → reset timer
    if (silenceTimer) {
      clearTimeout(silenceTimer);
      silenceTimer = null;
    }
  } else {
    // TIDAK ada suara → mulai hitung jeda
    if (!silenceTimer) {
      silenceTimer = setTimeout(() => {
        if (mediaRecorder && mediaRecorder.state === "recording") {
          console.log("⏹ Stop recording (silence detected)");
          mediaRecorder.stop();
        }
      }, SILENCE_LIMIT);
    }
  }

  if (mediaRecorder && mediaRecorder.state === "recording") {
    requestAnimationFrame(() => detectSilence(analyser));
  }
}
