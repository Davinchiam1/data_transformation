import re
import os
import pandas as pd
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import nltk
from nltk.util import ngrams
from pymorphy3 import MorphAnalyzer
from collections import defaultdict
from collections.abc import Iterable
from data_loading import Data_loading

# for first initiation, use following commands to download necessary data for nltk module

# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')
# nltk.download('averaged_perceptron_tagger')

def _get_wordnet_pos(word):
    """Map POS tag to first character lemmatize() accepts"""
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}
    return tag_dict.get(tag, wordnet.NOUN)


def _split_phrases(text):
    """In development"""
    words = text.split()  # split a string into a list of words

    phrases = []  # create an empty list to store phrases
    current_phrase = ""  # start with an empty line

    # sort through all the words and combine adjacent ones into phrases
    for word in words:
        if word.isdigit():  # skip numbers
            continue
        elif word.istitle():  # if the word begins with a capital letter, then this is the beginning of a new phrase
            phrases.append(current_phrase.strip())  # add the previous phrase to the list
            current_phrase = word  # start a new phrase
        else:
            current_phrase += " " + word  # add a word to the current phrase

    # add the last phrase to the list
    phrases.append(current_phrase.strip())

    return phrases


class Find_keywords:
    """Class for processing text info in dataframe into set of keywords and their relative frequency in text"""

    def __init__(self, language="russian"):
        self.frequency = {}
        self.temp_frame = None
        self.n_grams = 1
        self.text = ''
        self.patterns = "[0-9!#$%&'()*+,./:;<=>?@[\]^_`{|}~—\"\-]+"
        self.lang = language
        if language == "russian":
            self.morph = MorphAnalyzer()
        else:
            self.morph = WordNetLemmatizer()

    def _get_text(self, filepath, name_colum, selection=None):
        """
            Get text data from target file
            Args:
                filepath (str): path to file with text data.
                name_colum (): name of the target column.
                selection (list): type of selection.

            Returns:
                None
        """
        if filepath.split('.')[-1].lower() == 'csv':
            self.temp_frame = pd.read_csv(filepath, delimiter=';')
        elif filepath.split('.')[-1].lower() == 'xlsx':
            self.temp_frame = pd.read_excel(filepath)
        if selection is not None:
            # work in progress
            self.temp_frame = self.temp_frame.loc[self.temp_frame[selection[0]] == selection[1]]
        self.temp_frame = self.temp_frame[name_colum]

    def _tokenize(self, docs):
        """
            Tokenizing text docs
            Args:
                docs (str): text data.

            Returns:
                tokens (list):list of unic tokens collected from docs
        """
        tokens = []
        #  for 1 word tokens
        if self.n_grams == 1:
            docs = re.sub(self.patterns, '', docs)  # delete non-text data
            for token in docs.split():
                if token and token not in self.stopwords:
                    token = token.strip()
                    if self.need_normalization:
                        if self.lang != 'russian':
                            token = self.morph.lemmatize(token, _get_wordnet_pos(token)).lower()
                        else:
                            token = self.morph.normal_forms(token)[0]
                    else:
                        token = token.lower()
                    tokens.append(token)
                    if self.n_grams > 1:
                        tokens = list(ngrams(tokens, self.n_grams))
        # for n-word tokens (2 or 3 word max tested)
        else:
            # current_phrase = ""
            # for word in docs.split():
            #     if word.isdigit():  # пропустить числа
            #         continue
            #     elif word.istitle():  # если слово начинается с заглавной буквы, то это начало нового словосочетания
            #         tokens.append(current_phrase.strip())  # добавить предыдущее словосочетание в список
            #         current_phrase = word  # начать новое словосочетание
            #     else:
            #         current_phrase += " " + word  # добавить слово к текущему словосочетанию
            #
            # # добавить последнее словосочетание в список
            # tokens.append(current_phrase.strip())
            docs = re.sub(self.patterns, '', docs)
            for token in docs.split():
                if token and token not in self.stopwords:
                    token = token.strip()
                    if self.need_normalization:
                        if self.lang != 'russian':
                            token = self.morph.lemmatize(token, _get_wordnet_pos(token)).lower()
                        else:
                            token = self.morph.normal_forms(token)[0]
                    else:
                        token = token.lower()
                    tokens.append(token)
            tokens = list(ngrams(tokens, self.n_grams))
        if len(tokens) > 1:
            return tokens
        return None

    def _prepare_text(self):
        """Function for preparing text and setting parameters for base tokenization method"""
        if self.n_grams == 1:
            self.stopwords = stopwords.words(self.lang)
            self.patterns = "[!#$%&'()*+,./:;<=>?@[\]^_`{|}~—\"\-]"
        else:
            self.stopwords = ['']
            self.patterns = "[!#$%&'()*+,./:;<=>?@[\]^_`{|}~—\"\-]"
            self.stopwords.extend(['шт', 'мл', "для", "гр", 'л', '№', 'е', "c", 'and', 'to', ])
        self.temp_frame = self.temp_frame.apply(self._tokenize)

    def _count_frequency(self, output_file):
        """
            Count relative frequency of tokenized fragments
            Args:
                output_file (str): name for output file.

            Returns:
                None
        """
        self.frequency = defaultdict(int)
        for tokens in self.temp_frame.iloc[:]:
            if isinstance(tokens, Iterable):
                for token in tokens:
                    if self.n_grams > 1:
                        phrase = ''
                        for word in token:
                            phrase = phrase + ' ' + word
                        # self.frequency[token] += 1
                        self.frequency[phrase] += 1
                    else:
                        self.frequency[token] += 1

        final_frame = pd.DataFrame.from_dict(self.frequency, orient='index').reset_index()
        final_frame.columns = ['keyword', 'frequency']
        final_frame.to_excel(output_file, sheet_name='list1', index=False)

    def use(self, name_colum, need_normalization=False, read_xlsx=True, directory=None,
            set_dates=False, filepath=None, n_grams=1, output_file='./keywords.xlsx', temp_frame=None):
        """
            Function for executing a script loading data and marking if necessary. most parameters determine loading method.
            Args:
                name_colum (): name of target column.
                need_normalization (bool): determines whether to normalize word forms. Default False.
                read_xlsx (bool): determines whether to read xlsx files. Default False.
                directory (string): path to directory with target files to load.
                set_dates (bool): determines whether to set dates from filenames. Default False.
                filepath (string): path to file for loading data from single file.
                n_grams (int): number of n-grams for tokenization
                output_file (str): path of output file.
                temp_frame (pd.Dataframe): passes the dataframe if the method is called in conjunction with others in the
                                           data processing chain.

            Returns:
                None
        """
        self.need_normalization = need_normalization
        self.n_grams = n_grams
        if __name__ == "__main__":
            dl = Data_loading()
            self.temp_frame = dl.get_data(read_xlsx=read_xlsx, directory=directory, set_dates=set_dates,
                                          filepath=filepath)
        else:
            self.temp_frame = temp_frame
        self.temp_frame = self.temp_frame[name_colum]
        self._prepare_text()
        self._count_frequency(output_file=output_file)

# test1 = Find_keywords()
# # test1.use(filepath='./test.xlsx', otput_file='./test_out1.xlsx', name_colum='Title', n_grams=2)
# test1.use(filepath='C:\\Users\\aos.user5\\Desktop\\Масло для лица\\wb\\периоды.xlsx', name_colum='Name',
#           need_normalization=False, otput_file="C:\\Users\\aos.user5\\Desktop\\Масло для лица\\масло ключевые очист.xlsx")