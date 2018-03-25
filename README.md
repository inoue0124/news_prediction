# ニュース記事カテゴリ判定

GunocyのURLを入力するとその記事カテゴリを判定する。

## Description

djangoによるwebアプリとして実装。  
webアプリの分類器はナイーブベイズを使用。

## Features

### 分類器は以下の２種類を実装した。
・ナイーブベイズ  
・SVM

#### 1. ナイーブベイス
入力はニューステキストを単語とその出現回数で表現するBag-of-wordsとした。  
ゼロ頻度問題に対しては単語の出現回数に１を加えるラプラススムージングによって緩和した。

#### 2. SVM
入力はBag-of-wordsをTF-IDFにて重み付けした後，LSIによって300次元へ次元削減を行ったものとした。  
パラメータはグリッドサーチで最も点数の高いものとした。

## Requirement

必要なライブラリに関してはrequirement.txt内に記した。

## Usage

### 1. データベースの構築
    $ python manage.py makemigrations
    $ python manage.py migrate
    $ python manage.py collect_db

### 2. ナイーブベイズの学習
    $ python manage.py train_naive_bayes

### 3. webアプリの起動
    $ python manage.py runserver

### 4. 表示されたURLにアクセスし，Gunocyのニュース記事URLを入力。送信すると，推定カテゴリが表示される。

### その他：
svmの学習を行うには，

    $ python manage.py train_svm

またそれぞれの学習結果はstatic/image以下にConfusion matrixとして表示。

## Result
### ・ナイーブベイズ
![naive_bayes](https://user-images.githubusercontent.com/27270240/34509934-088c25f6-f093-11e7-9ec9-1982befaee3d.png)
### ・SVM
![svm](https://user-images.githubusercontent.com/27270240/34509942-14dfb9e4-f093-11e7-8af5-ba97546c93bf.png)

