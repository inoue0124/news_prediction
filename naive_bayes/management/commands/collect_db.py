#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from naive_bayes.models import Article


class Command(BaseCommand):

    def handle(self, *args, **options):
        '''
        gunosy.comから記事本文を取り出し、データベースを作成する。
        1.urllibでhtmlを取得し、beautifulsoupで各記事のurlを取得
        2.取得した各記事のurlから記事本文を取り出しデータベースに保存
        '''

        from bs4 import BeautifulSoup
        from urllib import request
        import sys
        import os
        import time
        import re
        import random
        from tqdm import tqdm, trange  # プログレスバーを表示
        from enum import Enum

        class gunocy_web(Enum):
            '''
            記事のカテゴリー数およびページ数を定義する。
            '''

            base_url = 'https://gunosy.com/categories/'
            categories = 8
            pages = 5
            headers = [('User-agent', 'Chrome/47.0.2526.73 Safari/537.36')]

        # カテゴリーページから各記事のurlが書いてあるタグを取得
        for i in trange(gunocy_web.categories.value, desc='category'):
            for j in trange(gunocy_web.pages.value, desc='    page'):
                url = gunocy_web.base_url.value+str(i+1)+'?page='+str(j+1)
                category_page = request.urlopen(url, timeout=20).read() \
                    .decode('utf-8', 'ignore')
                souped_category_page = BeautifulSoup(category_page, 'html5lib')
                list_titles = souped_category_page \
                    .find_all('div', class_='list_title')

                # urlが書いてあるタグから各記事のurlを取得
                article_url_list = []
                for list_title in list_titles:
                    article_url_list.append(list_title.find('a').get('href'))

                # 取得した各記事のurlから記事本文のhtmlを取り出す
                for article_url in tqdm(article_url_list, desc=' article'):
                    time.sleep(random.random())
                    article_page = request.urlopen(article_url, timeout=20) \
                        .read().decode('utf-8', 'ignore')
                    souped_article_page = \
                        BeautifulSoup(article_page, 'html5lib')
                    article_text = souped_article_page \
                        .find('div', class_='article gtm-click')

                    # article_textからタグとダブルクオーテーションを削除
                    p = re.compile(r'<[^>]*?>|"')
                    article_text = p.sub("", str(article_text))

                    # データベースへcategoryとarticle_textを保存
                    Article.objects.create(category=i+1, text=article_text)
