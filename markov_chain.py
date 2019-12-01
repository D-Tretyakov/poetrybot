import re
import random
import sys
import nltk
import pickle
from russtress import Accent
nltk.download('averaged_perceptron_tagger_ru')

sys.path.append("./poet-ex-machina")
from includes.utils import Utils
import includes.accentsandsyllables as accentsandsyllables
from includes.rhymesandritms import RhymesAndRitms

accent = Accent()

chast_rechu = {'S': 'a','A': 'b','NUM': 'c','A-NUM': 'd','V': 'e','ADV': 'f','PRAEDIC': 'g',
'PARENTH': 'h','S-PRO': 'i','A-PRO': 'j',
'ADV-PRO': 'k','PRAEDIC-PRO': 'l','PR': 'm','CONJ': 'n','PART': 'o','INTJ': 'p'}


def udar(word):
    slogu = 0
    gl = 0
    flag = False
    for i in accent.put_stress(word):
        if i in 'уеаоэяиюёы' and flag == False:
            gl += 1
        if i in 'уеаоэяиюёы':
            slogu += 1
        if i == "'":
            flag = True
    return gl, slogu


def pos_syllables_udar(word):
    udarr, syllables = udar(word)
    pos = nltk.pos_tag([word], lang="rus")[0][1]
    if pos in chast_rechu.keys():
        pos = chast_rechu[pos]
    else:
        pos = pos[0]

    return "{}{}{}{}".format(pos, syllables, udarr, word)


def is_rhyme(word, rhymed_word):
    word_num_syllables = int(word[1])
    word_accent_syllable = int(word[2])

    rhymed_word_num_syllables = int(rhymed_word[1])
    rhymed_word_accent_syllable = int(rhymed_word[2])

    rhymed_word_accented_syll_offset = rhymed_word_num_syllables - rhymed_word_accent_syllable
    rhymed_end_1 = RhymesAndRitms.getRhymedEnd(rhymed_word[3:], rhymed_word_accented_syll_offset)
    word_accented_syll_offset = word_num_syllables - word_accent_syllable
    rhymed_end_2 = RhymesAndRitms.getRhymedEnd(word[3:], word_accented_syll_offset)

    if not rhymed_end_1 or not rhymed_end_2:
        return False

    j = len(rhymed_end_2) - 1
    for i in range(len(rhymed_end_1) - 1, -1, -1):
        if j < 0:
            return True

        c1 = rhymed_end_1[i]
        c2 = rhymed_end_2[j]

        consonant = Utils.getConsonant(c2)
        if c1 != c2 and c1 != consonant and i > 1:
            return False

        j = j - 1

    return True

class Dictogram(dict):
    def __init__(self, iterable=None):
        # Инициализируем наше распределение как новый объект класса,
        # добавляем имеющиеся элементы
#         super(Dictogram, self).__init__()
        super().__init__()
        self.types = 0  # число уникальных ключей в распределении
        self.tokens = 0  # общее количество всех слов в распределении
        if iterable:
            self.update(iterable)

    def update(self, iterable):
        # Обновляем распределение элементами из имеющегося
        # итерируемого набора данных
        for item in iterable:
            if item in self:
                self[item] += 1
                self.tokens += 1
            else:
                self[item] = 1
                self.types += 1
                self.tokens += 1

    def count(self, item):
        # Возвращаем значение счетчика элемента, или 0
        if item in self:
            return self[item]
        return 0

    def return_random_word(self):
        random_key = random.sample(self, 1)
        # Другой способ:
        # random.choice(histogram.keys())
        return random_key[0]

    def return_weighted_random_word(self):
        # Сгенерировать псевдослучайное число между 0 и (n-1),
        # где n - общее число слов
        random_int = random.randint(0, self.tokens-1)
        index = 0
        list_of_keys = list(self.keys())
        # вывести 'случайный индекс:', random_int
        for i in range(0, self.types):
            index += self[list_of_keys[i]]
            # вывести индекс
            if(index > random_int):
                # вывести list_of_keys[i]
                return list_of_keys[i]


def generate_poem_line(my_sentetence_start):
    with open('model_markov.pickle', 'rb') as f:
        markov_model = pickle.load(f)
    with open('dictonary_for_markov_chain.pickle', 'rb') as f:
        text = pickle.load(f)


    my_sentetence_start = my_sentetence_start.split()[::-1]
    my_sentetence = list(map(pos_syllables_udar, my_sentetence_start))

    random.shuffle(text)

    flag = False
    for slovo in text:

        if slovo != my_sentetence[0] and slovo[-3:] == my_sentetence[0][-3:] and slovo[0] == my_sentetence[0][0] and slovo[1] == my_sentetence[0][1] and slovo[2] == my_sentetence[0][2] and is_rhyme(slovo, my_sentetence[0]) and len(slovo) > 6:
            flag = True

            current_word = slovo

        if flag == False:
            if slovo != my_sentetence[0] and slovo[0] == my_sentetence[0][0] and slovo[1] == my_sentetence[0][1] and slovo[2] == my_sentetence[0][2] and is_rhyme(slovo, my_sentetence[0]) and len(slovo) > 6:
                flag = True

                current_word = slovo

        if flag == False:
            if slovo != my_sentetence[0] and slovo[2] == my_sentetence[0][2] and slovo[1] == my_sentetence[0][1] and is_rhyme(slovo, my_sentetence[0]) and len(slovo) > 6:
                flag = True

                current_word = slovo
        if flag == False:
            if slovo != my_sentetence[0] and slovo[2] == my_sentetence[0][2] and is_rhyme(slovo,my_sentetence[0]) and len(slovo) > 6:
                flag = True

                current_word = slovo
        if flag == False:
            if slovo != my_sentetence[0] and slovo[-3:] == my_sentetence[0][-3:] and slovo[1] == my_sentetence[0][1] and is_rhyme(slovo, my_sentetence[0]) and len(slovo) > 6:
                flag = True
                current_word = slovo

        if flag == False:
            if slovo != my_sentetence[0] and slovo[-3:] == my_sentetence[0][-3:] and slovo[1] == my_sentetence[0][1] and is_rhyme(slovo, my_sentetence[0]) and len(slovo) > 6:
                flag = True
                current_word = slovo

        if flag == False:
            if slovo != my_sentetence[0] and slovo[-3:] == my_sentetence[0][-3:] and slovo[1] == my_sentetence[0][1] and is_rhyme(slovo, my_sentetence[0]) and len(slovo) > 6:
                flag = True

                current_word = slovo
        if flag == False:
            if slovo != my_sentetence[0] and slovo[-3:] == my_sentetence[0][-3:]:
                flag = True

                current_word = slovo
        if flag == False:
            if slovo != my_sentetence[0] and slovo[-2:] == my_sentetence[0][-2:]:
                flag = True

                current_word = slovo
        if flag == False:
            current_word = random.choice(text)

    result = [current_word[3:]]
    
    for i in range(1, len(my_sentetence)):
        current_dictogram = markov_model[current_word]
        slova = list(current_dictogram.keys())

        flag = False
        for slovo in slova:
            if slovo[0] == my_sentetence[i][0] and slovo[1] == my_sentetence[i][1] and slovo[2] == my_sentetence[i][
                2] and slovo != my_sentetence[i] and slovo != current_word:
                current_word = slovo
                flag = True

        if flag == False:
            if slovo[0] == my_sentetence[i][0] and slovo != my_sentetence[i] and slovo[1] == my_sentetence[i][
                1] and slovo != current_word:
                current_word = slovo
                flag = True

        if flag == False:
            for slovo in text:
                if slovo[0] != current_word[0] and slovo[0] == my_sentetence[i][0] and slovo != current_word and slovo[
                    1] == my_sentetence[i][1] and slovo != my_sentetence[i] and slovo[2] == my_sentetence[i][2]:
                    current_word = slovo
                    flag = True
        if flag == False:
            for slovo in text:
                if slovo[1] == my_sentetence[i][1] and slovo[2] == my_sentetence[i][2]:
                    current_word = slovo
                    flag = True
        if flag == False:
            current_word = random.choice(text)
        
        result.append(current_word[3:])
        
    result = ' '.join(result[::-1])
    return result.capitalize()


