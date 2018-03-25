# -*- coding: utf-8 -*-

import pickle
import base64
import MeCab
import math
import re
from bs4 import BeautifulSoup
from urllib import request as urlrequest
from naive_bayes.models import naive_model

class PredictCategory():
    def __init__(self, url):
        self.url = url
        self.article_page = urlrequest.urlopen(self.url, timeout=20) \
                      .read().decode('utf-8', 'ignore')
        self.souped_article_page = BeautifulSoup(self.article_page, 
                                                 'html5lib')
        self.article_text = self.souped_article_page \
                       .find('div', class_='article gtm-click')
        # article_textからタグとダブルクオーテーションを削除
        p = re.compile(r'<[^>]*?>|"')
        self.article_text = p.sub("", str(self.article_text))
        self.keywords = self.text2noun_list(self.article_text)
        self.get_values()
        self.categories = {1:'エンタメ', 2:'スポーツ', 3:'おもしろ', 4:'国内',
                      5:'海外', 6:'コラム', 7:'IT・科学', 8:'グルメ'}


    def text2noun_list(self, text):
            '''
            textを形態素解析して、名詞のみのリストを返す関数
            '''

            tagger = MeCab.Tagger()
            keywords = []
            for i in tagger.parse(text).splitlines():
                if (i != 'EOS') and \
                   (i.split('\t')[1].split(",")[0] == "名詞"):
                    keywords.append(i.split('\t')[0])
            return keywords

    def unpack(self, data):
        return pickle.loads(base64.b64decode(data))

    def get_values(self):
        values = naive_model.objects.all()[0]
        self.vocabularies = self.unpack(values.vocabularies)
        self.wordcount = self.unpack(values.wordcount)
        self.prob_category = self.unpack(values.prob_category)
        self.denominator = self.unpack(values.denominator)

    def prob_word_given_category(self, category, word):
        '''
        事後確率P(word|category)を計算して返す関数
        '''
 
        return (self.wordcount[category][word] + 1) / \
                self.denominator[category]


    def score(self, category, text):
        '''
        カテゴリの出現確率P(category)と事後確率P(word|category)の
        対数を計算し、和を返す関数
        '''

        score = math.log(self.prob_category[category])
        for word in text:
            score += math.log(self.prob_word_given_category(category, word))
        return score

    def classify(self, data):
        '''
        関数scoreでカテゴリ毎に事後確率P(category|text)を計算し、
        argmaxを返す関数
        '''

        estimation = None
        max = -float('inf')
        for category in self.prob_category.keys():
            p = self.score(category, data)
            if p > max:
                max = p
                estimation = category
        return estimation    

