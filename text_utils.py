from __future__ import division
import string
import nltk 
from nltk.corpus import stopwords
import re,pprint
from nltk import pos_tag
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from spellchecker import SpellChecker


lemmatizer = WordNetLemmatizer()
wordnet_map = {"N":wordnet.NOUN, "V":wordnet.VERB, "J":wordnet.ADJ, "R": wordnet.ADV}
spell = SpellChecker()


def lower_case(text):
    return text.lower()
def remove_punctuations(text):
    punctuations = string.punctuations
    return text.translate(str.maketrans('','',punctuations))
def remove_stopwords(text):
    STOPWORDS = set(stopwords.words('english'))
    return " ".join(word for word in text.split() if word not in STOPWORDS)
def remove_specialchar(text):
    text = re.sub('[^a-zA-Z0-9]'," ",text)
    text = re.sub('\s+',' ')
    return text

def lemmatized_words(text):
    # find pos tags
    pos_text = pos_tag(text.split())
    return " ".join([lemmatizer.lemmatize(word,wordnet_map.get(pos[0], wordnet.NOUN)) for word, pos in pos_text])
def correct_spellings(text):
    corrected_text = []
    misspelled_text = spell.unknown(text.split())
    for word in text.split():
        if word in misspelled_text:
            corrected_text.append(spell.correction(word))
        else:
            corrected_text.append(word)
    return " ".join(corrected_text)

def signal_extraction(text):
    L = text.split()
    extracted = []
    tags = pos_tag(L)
    for word, tag in tags:
        if tag in ['NN','NNS','NNP','NNPS','VB','VBD','VBG','VBN','VBP','VBZ','JJ','JJR','JJS']:
            extracted.append(word)
    extracted = list(set(extracted))
    return extracted
def tokenise(text):
    return nltk.word_tokenize(text)














    