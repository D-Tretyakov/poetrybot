import includes.accentsandsyllables as accentsandsyllables
# from includes.utils import Utils
# from includes.rhymesandritms import RhymesAndRitms
accents = accentsandsyllables.AccentsAndSyllables()

word='корова'
x = {'word':word}
# y = accents.setAccentsAndSyllablesAuto(x)
y=accents.setAccentsAndSyllablesAuto(x)
# word_num_syllables =y['sylNum']
# word_accent_syllable = y['accentSylNum']
print(y)