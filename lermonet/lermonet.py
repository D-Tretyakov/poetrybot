from __future__ import print_function
import os
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID" 
os.environ["CUDA_VISIBLE_DEVICES"] = ""
from keras.callbacks import LambdaCallback
from keras.models import Sequential
from keras.models import load_model
from keras.layers import Dense
from keras.layers import LSTM
from keras.optimizers import RMSprop
from keras.utils.data_utils import get_file
import numpy as np
import random
import sys
import io
import re
import json
from russtress import Accent
from pyphonetics import Soundex
from fonetika.soundex import RussianSoundex
import rusyllab
from fonetika.distance import PhoneticsInnerLanguageDistance
from collections import defaultdict
import nltk
import edlib

model = load_model('lermonet_3.h5')
accent = Accent()
soundex = RussianSoundex(delete_first_letter=True, code_vowels=True)
# phon_distance = PhoneticsInnerLanguageDistance(soundex)

with open('rhymes_dict_sdx.txt', 'r') as f:
    rhymes_dict = json.loads(f.read())

def get_rhyme_ending(word):
    stress_pos = accent.put_stress(word).find('\'')
    if stress_pos == -1:
        return word

    lst = list(word)
    lst[stress_pos-1] = lst[stress_pos-1].upper()
    word = ''.join(lst)
    sx = rusyllab.split_words([word])
    for i in range(len(sx)):
        if not sx[i].islower():
            return ''.join(sx[i:]).lower()

# def is_rhyme(word1, word2):
#     end1 = get_rhyme_ending(word1)
#     end2 = get_rhyme_ending(word2)
#     if phon_distance.distance(end1, end2) <= 1:
#         return True
#     else:
#         return False

# def check_rhyme_end_with_word(end, word):
#     word_end = get_rhyme_ending(word)
#     if phon_distance.distance(end, word_end) <= 1:
#         return True
#     else:
#         return False

p = re.compile(r'[а-яА-ЯёЁ]+')
def get_rhyme_line(sent):
    rhyme_lines = []
    words = p.findall(sent)
    if words:
        word = p.findall(sent)[-1]
    else:
        return 'Рифма тут так себе будет...\nДавай другую\n'
    
    sdx_ending = soundex.transform(get_rhyme_ending(word))
    for end in rhymes_dict:
        if edlib.align(end, sdx_ending)["editDistance"] < 1:
            rhyme_lines += rhymes_dict[end]
    if rhyme_lines:
        # return re.sub(r'[\s]', '', random.choice(rhyme_lines))
        return random.choice(rhyme_lines)
    else:
        return 'Рифма тут так себе будет...\nДавай другую\n'

def sample(preds, temperature=0.1):
    # helper function to sample an index from a probability array
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)

def get_start_str(sent, size):
    lermontov_line = get_rhyme_line(sent)
    start_str = lermontov_line + '\n'

    sent += start_str
    if len(sent) >= size:
        return [sent[len(sent)-size:], start_str]
    else:
        return [(' ' * (size-len(sent))) + sent, start_str]

with open('./Lermontov all (raw text).txt', encoding='utf-8') as f:
    text = f.read()
print('corpus length:', len(text))

chars = sorted(list(set(text)))
# print('total chars:', len(chars))
char_indices = dict((c, i) for i, c in enumerate(chars))
indices_char = dict((i, c) for i, c in enumerate(chars))

# cut the text in semi-redundant sequences of maxlen characters
maxlen = 40
step = 3
sentences = []
next_chars = []
for i in range(0, len(text) - maxlen, step):
    sentences.append(text[i: i + maxlen])
    next_chars.append(text[i + maxlen])
# print('nb sequences:', len(sentences))

def generate_rhyme(count, sent):
    generated = ""
    sentence, start_str = get_start_str(sent, maxlen)
    if start_str.startswith('Рифма тут так себе будет'):
        return start_str
    chrs = ''
    generated += sentence

    for _ in range(count):
        x = np.zeros((1, maxlen, len(chars)))
        for t, char in enumerate(sentence):
            x[0, t, char_indices[char]] = 1.

        preds = model.predict(x, verbose=0)[0]
        next_index = sample(preds, 0.2)
        next_char = indices_char[next_index]

        generated += next_char
        chrs += next_char
        sentence = sentence[1:] + next_char
    return '\n'.join([start_str.strip()] + chrs.split('\n')[:1]).strip()

# if __name__ == "__main__":
#     while(1):
#         sent = input('Enter sentence: ')
#         print(generate_rhyme(100, sent))