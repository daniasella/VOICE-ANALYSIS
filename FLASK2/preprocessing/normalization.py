import re

# daftar filler / noise lisan
FILLER_WORDS = [
    "eee", "eh", "em", "umm", "anu", "yah", "loh", "deh", "sih"
]

# kamus slang → formal 
SLANG_DICT = {
    "gak": "tidak",
    "ga": "tidak",
    "nggak": "tidak",
    "tdk": "tidak",
    "enggak" : "tidak",
    "bgt": "banget",
    "bangettt": "banget",
    "bangsad": "bangsat",
    "sukaaa": "suka",
    "jelekkk": "jelek",
    "bgus": "bagus",
    "pelayanann": "pelayanan",
    "seneng": "senang",
    "kereny": "keren",
    "trs": "terus",
    "aja": "saja",
    "udah": "sudah",
    "gue": "saya",
    "aku" : "saya",
    "lu": "kamu",
    "lo": "kamu",
}

def case_folding(text):
    """Mengubah seluruh teks menjadi huruf kecil"""
    return text.lower()

def normalize_symbols(text):
    """Ubah simbol umum menjadi kata, misalnya % → persen"""
    text = re.sub(r'%', ' persen', text)  # % → persen
    # Tambah simbol lain jika perlu, misalnya:
    # text = re.sub(r'@', ' at ', text)  # @ → at
    # text = re.sub(r'&', ' dan ', text)  # & → dan
    return text

def protect_numbers_with_dots(text):
    """Lindungi angka dengan titik/koma agar tidak dihapus oleh remove_noise"""
    # Pola: angka dengan titik/koma, misalnya 80.000, 1,000, 123.456
    pattern = r'(\d+(?:[.,]\d+)+)'
    placeholders = {}
    counter = 0
    
    def replace_match(match):
        nonlocal counter
        placeholder = f"__NUM{counter}__"
        placeholders[placeholder] = match.group(0)
        counter += 1
        return placeholder
    
    protected_text = re.sub(pattern, replace_match, text)
    return protected_text, placeholders

def restore_numbers(text, placeholders):
    """Kembalikan placeholder ke angka asli"""
    for placeholder, original in placeholders.items():
        text = text.replace(placeholder, original)
    return text

def remove_noise(text):
    """Menghapus karakter selain huruf dan spasi"""
    # Lindungi angka dulu
    protected_text, placeholders = protect_numbers_with_dots(text)   

    # Hapus karakter non-alfanumerik (kecuali placeholder)
    protected_text = re.sub(r"[^a-zA-Z0-9\s__]", " ", protected_text)
    
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    # Pisah gabungan seperti "80ribu" → "80 ribu" (opsional, jika STT sering gabung)
    text = re.sub(r"(\d+)([a-zA-Z]+)", r"\1 \2", text)  # Pisah angka + huruf
    text = re.sub(r"([a-zA-Z]+)(\d+)", r"\1 \2", text)  # Pisah huruf + angka
    text = re.sub(r"\s+", " ", protected_text)

    # Kembalikan angka
    cleaned_text = restore_numbers(protected_text, placeholders)
    return cleaned_text.strip()

def remove_filler(text):
    """Menghapus kata filler/noise lisan"""
    tokens = text.split()
    tokens = [t for t in tokens if t not in FILLER_WORDS]
    return " ".join(tokens)

def normalize_slang(text):
    """Mengubah kata slang menjadi kata baku"""
    tokens = text.split()
    tokens = [SLANG_DICT.get(t, t) for t in tokens]
    return " ".join(tokens)

def remove_repeated_characters(text):
    """Mengurangi pengulangan huruf berlebih : sukaaa -> suka, jelekkk -> jelek"""
    return re.sub(r'(.)\1{2,}', r'\1\1', text)

def text_normalization(text):
    """Pipeline text normalization"""
    text = case_folding(text)
    text = remove_noise(text)
    text = normalize_slang(text)
    text = remove_repeated_characters(text)
    text = remove_filler(text)
    return text
