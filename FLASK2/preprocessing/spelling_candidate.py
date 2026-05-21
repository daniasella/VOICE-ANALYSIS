# preprocessing/spelling_candidate.py

def levenshtein_distance(a, b):
    dp = [[0] * (len(b)+1) for _ in range(len(a)+1)]

    for i in range(len(a)+1):
        dp[i][0] = i
    for j in range(len(b)+1):
        dp[0][j] = j

    for i in range(1, len(a)+1):
        for j in range(1, len(b)+1):
            cost = 0 if a[i-1] == b[j-1] else 1
            dp[i][j] = min(
                dp[i-1][j] + 1,
                dp[i][j-1] + 1,
                dp[i-1][j-1] + cost
            )
    return dp[-1][-1]

def generate_candidates(word, vocabulary, max_dist=2):
    return [
        v for v in vocabulary
        if abs(len(v) - len(word)) <= 2
        and levenshtein_distance(word, v) <= max_dist
    ]

#Sistem membatasi spelling correction berdasarkan panjang kata dan daftar kata umum 
#untuk menghindari perubahan makna akibat metode Levenshtein 
#yang hanya mempertimbangkan jarak karakter tanpa konteks semantik.
