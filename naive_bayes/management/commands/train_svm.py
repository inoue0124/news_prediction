from django.core.management.base import BaseCommand, CommandError
from naive_bayes.models import Article


class Command(BaseCommand):

    def handle(self, *args, **options):

        import os
        import MeCab
        import pickle
        import base64
        from sklearn.model_selection import train_test_split, GridSearchCV
        from sklearn.metrics import confusion_matrix
        from sklearn.externals import joblib
        from sklearn.svm import SVC
        import pandas as pd
        import seaborn as sn
        import matplotlib.pyplot as plt
        from gensim import corpora, models, matutils

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

        def make_bow(noun_list):
            '''
            各記事の名詞リストに対してbag-of-wordsベクトルを返す関数
            '''

            dic = corpora.Dictionary(noun_list)
            # 「出現頻度が20未満の単語」と「30%以上の文書で出現する単語」を排除
            dic.filter_extremes(no_below=10, no_above=0.3)
            bow_corpus = []
            bow_corpus = [dic.doc2bow(d) for d in noun_list]
            tfidf_model = models.TfidfModel(bow_corpus)
            tfidf_corpus = tfidf_model[bow_corpus]
            lsi_model = models.LsiModel(tfidf_corpus, id2word = dic, num_topics = 300)
            lsi_corpus = lsi_model[tfidf_corpus]
            corpus = []
            for doc in lsi_corpus:
                corpus.append([doc[d][1] for d in range(len(doc))])
            return corpus

        def train_svm(train_text, train_category):
            '''
            学習データでsvmの学習を行い、テストデータで正解率を計算する関数。
            '''

            svc = SVC()
            cs = [0.001, 0.01, 0.1, 1, 10]
            gammas = [0.001, 0.01, 0.1, 1]
            parameters = {'kernel': ['rbf'], 'C': cs, 'gamma': gammas}
            clf = GridSearchCV(svc, parameters)
            clf.fit(train_text, train_category)
            # モデルを保存
            test_pred = clf.predict(bow_test)
            # 正解率を表示
            train_score = clf.score(bow_train, label_train)
            test_score = clf.score(bow_test, label_test)
            return train_score, test_score, test_pred


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
            plt.title('News article classification by svm')
            plt.xlabel('ground truth')
            plt.ylabel('prediction')
            plt.savefig('./static/image/svm.png')

        def pack(data):
            '''
            引数のdataをpickle, base64化して返す関数
            '''

            return base64.b64encode(pickle.dumps(data))

        data, label = read_db()
        bow = make_bow(data)
        bow_train, bow_test, label_train, label_test = \
            train_test_split(bow, label, train_size=0.8, random_state=0)
        train_score, test_score, test_pred = train_svm(bow_train, label_train)
        print('学習データ認識率：',train_score)
        print('テストデータ認識率：',test_score)
        print_cmx(label_test, test_pred)
