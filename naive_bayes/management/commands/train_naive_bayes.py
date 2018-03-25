from django.core.management.base import BaseCommand, CommandError
from naive_bayes.models import Article
from naive_bayes.models import naive_model

class Command(BaseCommand):

    def handle(self, *args, **options):

        import MeCab
        import math
        from collections import defaultdict
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import confusion_matrix
        import pickle
        import base64
        import pandas as pd
        import seaborn as sn
        import matplotlib.pyplot as plt

        def text2noun_list(text):
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

        def read_db():
            '''
            データベースから記事とカテゴリを読み出し、名詞のみのリストにする関数
            '''

            data = []
            label = []
            for h in Article.objects.all():
                data.append(text2noun_list(h.text))
                label.append(h.category)
            return data, label

        def arrange_var():
            '''
            定義した変数にデータを格納する関数
            '''

            for i in range(len(data_train)):
                for word in data_train[i]:
                    vocabularies[label_train[i]].append(word)
                    wordcount[label_train[i]][word] += 1
            for i in range(8):
                prob_category[i+1] = label_train.count(i+1)/len(label_train)
                denominator[i+1] = len(vocabularies[i+1])

        def prob_word_given_category(category, word):
            '''
            事後確率P(word|category)を計算して返す関数
            '''

            return (wordcount[category][word] + 1) / denominator[category]

        def score(category, text):
            '''
            カテゴリの出現確率P(category)と事後確率P(word|category)の
            対数を計算し、和を返す関数
            '''

            score = math.log(prob_category[category])
            for word in text:
                score += math.log(prob_word_given_category(category, word))
            return score

        def classify(data):
            '''
            関数scoreでカテゴリ毎に事後確率P(category|text)を計算し、
            argmaxを返す関数
            '''

            estimation = None
            max = -float('inf')
            for category in prob_category.keys():
                p = score(category, data)
                if p > max:
                    max = p
                    estimation = category
            return estimation

        def accuracy(data, label):
            '''
            関数classifyにdataを渡し、最も可能性の高いカテゴリを計算。
            対応するlabelと照合して正解率を計算する関数
            '''

            count = 0
            prediction_label = []
            for i in range(len(data)):
                prediction_label.append(classify(data[i]))
                if label[i] == classify(data[i]):
                    count += 1
            return count/len(data), prediction_label

        def print_cmx(true_label, pred_label):
            '''
            Confusion matrixを描画する。
            '''

            labels = sorted(list(set(true_label)))
            cmx_data = confusion_matrix(true_label, pred_label, labels=labels)
            labels = ['Entertain', 'Sports', 'Funny',
                      'Domestic', 'Oversees', 'Column', 'IT', 'Cuisine']
            df_cmx = pd.DataFrame(cmx_data, index=labels, columns=labels)
            plt.figure(figsize=(10, 7))
            sn.heatmap(df_cmx, annot=True, square=True, cmap='Blues')
            plt.title('News article classification by naive bayes')
            plt.xlabel('ground truth')
            plt.ylabel('prediction')
            plt.savefig('./static/image/naive_bayes.png')

        def pack(data):
            '''
            引数のdataをpickle, base64化して返す関数
            '''

            return base64.b64encode(pickle.dumps(data))

        vocabularies = {}  # {カテゴリ:語彙(Bag of words)}の辞書
        wordcount = {}  # {カテゴリ:{単語:単語出現数}}の辞書
        prob_category = {}  # {カテゴリ:P(category)}の辞書
        for i in range(8):
            wordcount[i+1] = defaultdict(int)
            vocabularies[i+1] = []
        denominator = {}  # {カテゴリ:カテゴリ中の総単語数}の辞書

        data, label = \
            read_db()  # data:名詞のみの記事データ, label:正解ラベル
        data_train, data_test, label_train, label_test = \
            train_test_split(data, label, train_size=0.8)
        arrange_var()
        accuracy_test, pred_label_test = accuracy(data_test, label_test)
        accuracy_train, pred_label_train = accuracy(data_train, label_train)
        print('学習データ認識率：',accuracy_train)
        print('テストデータ認識率：',accuracy_test)
        print_cmx(label_test, pred_label_test)

        packed_vocabularies = pack(vocabularies)
        packed_wordcount = pack(wordcount)
        packed_prob_category = pack(prob_category)
        packed_denominator = pack(denominator)
        naive_model.objects.update_or_create(vocabularies=packed_vocabularies, \
                                   wordcount=packed_wordcount, \
                                   prob_category=packed_prob_category, \
                                   denominator=packed_denominator)
