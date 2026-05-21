# rulebased.py
# ----------------------------------
# Rule-based sentiment guard
# Untuk menangani kalimat FORMAL
# ----------------------------------

from preprocessing.lexicon import KATA_MAKIAN, PRONOMINA, INTENSIFIER

def normalize_text(text: str) -> str:
    return text.lower().strip()


FORMAL_POSITIVE = {
    "kontribusi anda dalam proyek ini sangat krusial bagi keberhasilan tim",
    "saya sangat menghargai dedikasi yang anda berikan untuk mencapai target ini",
    "kualitas pekerjaan anda selalu melampaui ekspektasi yang ditetapkan",
    "anda telah menunjukkan performa yang sangat luar biasa pada kuartal ini",
    "inisiatif anda dalam menyelesaikan masalah tersebut sangatlah tepat guna",
    "kami merasa bangga memiliki profesional seperti anda di organisasi ini",
    "kerja keras anda memberikan dampak positif yang signifikan bagi perusahaan",
    "perhatian anda terhadap detail merupakan aset berharga bagi tim kami",
    "anda memiliki kemampuan luar biasa dalam mengelola tanggung jawab yang kompleks",
    "pencapaian ini adalah bukti nyata dari kompetensi dan integritas anda",
    "terima kasih atas profesionalisme yang konsisten anda tunjukkan",
    "hasil riset yang anda susun sangat komprehensif dan membantu pengambilan keputusan",
    "anda berhasil menyelesaikan tugas ini dengan efisiensi yang sangat tinggi",
    "ketepatan waktu anda dalam menyerahkan laporan patut dijadikan teladan",
    "anda telah memberikan nilai tambah yang luar biasa bagi divisi ini",
    "kolaborasi kita hari ini membuahkan hasil yang sangat produktif",
    "saya sangat mengagumi cara anda merangkul perbedaan pendapat dalam tim",
    "sinergi yang kita bangun akan mempercepat pencapaian visi perusahaan",
    "terima kasih telah menjadi rekan kerja yang sangat suportif dan kooperatif",
    "kemampuan komunikasi anda sangat membantu kelancaran proyek lintas divisi",
    "anda selalu mampu menciptakan suasana kerja yang harmonis dan profesional",
    "kepemimpinan anda dalam kelompok ini sangat menginspirasi banyak pihak",
    "ide inovatif anda membuka peluang baru bagi pertumbuhan bisnis kita",
    "anda berhasil mengubah tantangan menjadi peluang yang menguntungkan",
    "masa depan organisasi ini terlihat sangat cerah dengan kehadiran sdm seperti anda",
    "optimisme anda memberikan energi tambahan bagi seluruh anggota tim",
    "anjing hewan pintar dan setia"
}


FORMAL_NEGATIVE = {
    "hasil pekerjaan ini tidak memuaskan",
    "saya kecewa dengan pelayanan toko itu",
    "filmnya membosankan",
    "hasil pekerjaan yang diserahkan saat ini belum memenuhi standar kualitas minimum perusahaan",
    "terdapat penurunan signifikan dalam akurasi data yang disajikan dalam laporan bulanan",
    "kualitas output yang dihasilkan cenderung tidak konsisten dan memerlukan pengawasan ketat",
    "analisis yang diberikan kurang mendalam dan gagal mengidentifikasi akar permasalahan",
    "banyak ditemukan kesalahan administratif yang seharusnya dapat dihindari dengan ketelitian",
    "performa anda pada kuartal ini berada di bawah ekspektasi yang telah ditetapkan sebelumnya",
    "dokumentasi proyek yang disusun sangat tidak terstruktur dan sulit untuk dipahami",
    "kurangnya perhatian terhadap detail menyebabkan banyak revisi yang membuang waktu",
    "hasil riset anda tidak didukung oleh metodologi yang kuat dan data yang valid",
    "anda gagal mencapai target yang telah disepakati di awal periode",
    "efisiensi kerja anda menurun drastis dibandingkan periode sebelumnya",
    "laporan yang diberikan tidak menyertakan solusi konkret atas masalah yang dilaporkan",
    "tingkat kesalahan teknis dalam pekerjaan anda berada di atas ambang batas toleransi",
    "anda kurang menunjukkan pemahaman mendalam terhadap prosedur operasional standar",
    "kualitas presentasi anda tidak mencerminkan profesionalisme yang diharapkan organisasi",
    "keterlambatan dalam menyerahkan laporan telah menghambat alur kerja tim",
    "manajemen waktu yang buruk menyebabkan banyak tugas menumpuk di akhir periode",
    "anda gagal memenuhi komitmen waktu yang telah ditetapkan"

}


def rule_based_sentiment(text: str):
    """
    Mengembalikan:
    - 'positif'
    - 'negatif'
    - None (jika tidak terdeteksi)
    """
    text = normalize_text(text)

    for sent in FORMAL_POSITIVE:
        if sent in text:
            return "positif"

    for sent in FORMAL_NEGATIVE:
        if sent in text:
            return "negatif"

    return None
#=========================================================

def detect_umpatan(tokens):
    if is_literal_animal_context(tokens):
        return False

    for i, word in enumerate(tokens):
        if word == "anjing":
            # cek kata sebelum
            if i > 0 and tokens[i-1] in KATA_MAKIAN:
                return True
            
            # cek kata sesudah
            if i < len(tokens)-1 and tokens[i+1] in PRONOMINA:
                return True
            
            # cek intensifier
            if i < len(tokens)-1 and tokens[i+1] in INTENSIFIER:
                return True
    return False

ANIMAL_CONTEXT = {
    "hewan", "peliharaan", "setia", "lucu", "pintar",
    "cerdas", "penjaga", "pelacak", "terapi",
    "pemilik", "tuan", "tuannya", "anak", "rumah", "terlatih"
}

def is_literal_animal_context(tokens):
    score = 0
    for t in tokens:
        if t in ANIMAL_CONTEXT:
            score += 1
    return score >= 2
