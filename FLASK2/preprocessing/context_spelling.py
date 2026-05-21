# preprocessing/context_spelling.py

import math
import token
from preprocessing.spelling_candidate import generate_candidates

COMMON_WORDS = {
    "saya", "aku", "dia", "kami", "kita", "anda",
    "tidak", "bukan", "dan", "atau", "yang",
    "ini", "itu", "pada", "karena"
}

def context_aware_spelling(text, lm, vocabulary, indo_dict, max_edit=1):
    tokens = text.split()
    corrected = []

    for i, token in enumerate(tokens):

        # 🔒 jangan sentuh kata aman
        if token in vocabulary or token in COMMON_WORDS:
            corrected.append(token)
            continue
        if token in indo_dict:
            corrected.append(token)
            continue
        if len(token) < 4: # kata pendek diabaikan
            corrected.append(token)
            continue

        prev_word = corrected[i - 1] if i > 0 else "<s>"

        candidates = generate_candidates(token, vocabulary, max_edit)

        if not candidates:
            corrected.append(token)
            continue

        best_word = token
        best_score = -math.log(lm.get_prob(prev_word, token))

        for cand in candidates:
            score = math.log(lm.get_prob(prev_word, cand))
            # hanya ganti jika jauh lebih baik
            if score < best_score - 3.0:
                best_score = score
                best_word = cand
        
        # Tambah di dalam loop for i, token in enumerate(tokens):
        print(f"Token: {token}, Candidates: {candidates}, Best: {best_word}", flush=True)

        corrected.append(best_word)

    return " ".join(corrected)
