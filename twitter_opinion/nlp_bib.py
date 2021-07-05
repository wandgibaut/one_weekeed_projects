import numpy as np
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer, sent_tokenize, word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.collocations import *
from collections import Counter
import glob
import os

class CollectiveKnowledgeExtractor():
    def __init__(self, language='english'):
        self.language = language

    def preprocessing_data(self, full_text):
        tokenizer = RegexpTokenizer(r'\w+')
        lemm = WordNetLemmatizer()

        sentences = sent_tokenize(full_text)
        clean_sentences = sent_tokenize(full_text)
        for i in range(len(clean_sentences)):
            clean_sentences[i] = lemm.lemmatize(clean_sentences[i])

        #tokens = tokenizer.tokenize(re.sub("[,.]", "" , full_text))
        tokens = tokenizer.tokenize(re.sub("[^-9A-Za-z ]", "" , full_text))
        tokens = [lemm.lemmatize(token.lower()) for token in tokens]


        sr= stopwords.words(self.language)
        clean_tokens = [token for token in tokens if token not in sr]

        return clean_sentences, clean_tokens, sentences


    def adjacence_matrix(self, tokens):
        bigram_measures = nltk.collocations.BigramAssocMeasures()
        finder = BigramCollocationFinder.from_words(tokens)
        finder.nbest(bigram_measures.pmi, 10)  

        scored = finder.score_ngrams(bigram_measures.raw_freq)
        sor = sorted(bigram for bigram, score in scored)  

        return sor

    def next_step(self, word, sorted_ad_matrix):
        ste_count = Counter(elem for elem in sorted_ad_matrix if elem[0] == word) + Counter(elem for elem in sorted_ad_matrix if elem[1] == word)
        p = np.array(list(ste_count.values()))
        p = p/sum(p)

        temp = list(ste_count)[np.random.choice(len(ste_count), p=p)]
        if temp[0] == word:
            return temp[1]
        return temp[0]


    def path_extractor(self, sorted_ad_matrix, n_words, phrases_per_word, in_words):
        answer =[]
        for in_word in in_words:
            for j in range(phrases_per_word):
                proto_phrase = ''
                last_word = in_word
                for i in range(n_words):
                    proto_phrase += last_word + ' '
                    last_word = self.next_step(last_word, sorted_ad_matrix)
                answer.append(proto_phrase)
        return answer

    def final_mapper(self, phrases, sentences, original_sentences):
        tokenizer = RegexpTokenizer(r'\w+')
        #tokenizer = word_tokenize
        lemm = WordNetLemmatizer()
        best_sentences = []
        for proto_phrase in phrases:
            rank = []
            for i in range(len(sentences)):
                num_present = 0
                sentence = sentences[i]
                #toki = word_tokenize(re.sub("[,]", "" , sentence), language='portuguese')
                #toki = tokenizer.tokenize(re.sub("[,.]", "" , sentence))
                toki = tokenizer.tokenize(re.sub("[^-9A-Za-z ]", "" , sentence))
                toki = [lemm.lemmatize(toks.lower()) for toks in toki]
                for proto_word in proto_phrase.split(' '):
                    if proto_word in toki:
                        num_present +=1
                rank.append(num_present)
            best_sentences.append(original_sentences[rank.index(max(rank))])

        #print(max(rank))
        return best_sentences


    def full_extraction(self, full_text, n_words, phrases_per_word, in_words):
        #in_tokens = [w for w in in_words]
        sentences, tokens, original_sentences = self.preprocessing_data(full_text)
        sorted_ad_matrix = self.adjacence_matrix(tokens)
        proto_phrases = self.path_extractor(sorted_ad_matrix, n_words, phrases_per_word, in_words)
        selected_sentences = self.final_mapper(proto_phrases, sentences, original_sentences)
        return selected_sentences

    def aux_preprocess(self, words_list):
        tokenizer = RegexpTokenizer(r'\w+')
        tokens = [tokenizer.tokenize(re.sub("[^-9A-Za-z ]", "" , word))[0] for word in words_list]
        answer = [WordNetLemmatizer().lemmatize(toks.lower()) for toks in tokens]
        return answer


def concat_data(all_reviews):
    full_text = ''
    for i in range(len(all_reviews)):
        full_text += all_reviews.iloc[i]['Review'] + '. ' 
    return full_text


def get_companies_jsons(list_companies):
    json_list = [com + '.json' for com in list_companies]
    answer = []
    current_dir = os.getcwd()
    for filename in glob.iglob(current_dir + '/data/**', recursive=True):
            for json_name in json_list:
                if filename.__contains__(json_name):
                    answer.append(filename)
    return answer


if __name__ == '__main__':
    pass


    