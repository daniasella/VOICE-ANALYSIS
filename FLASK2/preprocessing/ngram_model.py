# preprocessing/ngram_model.py
from collections import Counter

class BigramLM:
    def __init__(self, corpus):
        self.unigram = Counter()
        self.bigram = Counter()

        for sentence in corpus:
            tokens = ["<s>"] + sentence.split() + ["</s>"]
            for i in range(1, len(tokens)):
                self.unigram[tokens[i-1]] += 1
                self.bigram[(tokens[i-1], tokens[i])] += 1

        self.vocab_size = len(self.unigram)

    def get_prob(self, w1, w2):
        return (self.bigram[(w1, w2)] + 1) / (
            self.unigram[w1] + self.vocab_size
        )

