#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "husterxsp"

import sys
import time
import sqlite3
import requests
import re
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding("utf-8")

class Book(object):
    def __init__(self, book_id, name, url, score, comment_num, desc):
        self.book_id = book_id
        self.name = name
        self.score = score
        self.url = url
        self.description = desc
        self.comment_num = comment_num

tags = ['小说', '中国小说', '文学', '中国文学', '外国文学']
tables = ['novel', 'cn_novel', 'literature', 'cn_literature', 'fo_literature']

def main():
    main_url = "https://book.douban.com/tag/"

    for i in range(len(tags)):
        start = 0
        result = []

        while True:
            request_url = main_url + tags[i] + "?type=T&start=" + str(start)
            response = requests.get(request_url)
            print(response)

            soup = BeautifulSoup(response.content, "html.parser")
            booklist = soup.find_all("li", class_ = "subject-item")

            if booklist == None or len(booklist) == 0:
                break

            for item in booklist:
                info = item.find('div', class_ = 'info')

                try:
                    name = info.h2.a.text
                    url = info.h2.a['href']
                    book_id = re.search('.*/(\d+)/', url).group(1)
                    score = info.find('span', class_ = 'rating_nums').text
                    desc = info.p.text
                    comment_num = info.find('span', class_ = 'pl').text
                    comment_num = re.search('(\d+)', comment_num).group(1)
                    # comment_num = re.findall(r'\d+', comment_num)[0]
                except Exception as e:
                    print(e)

                book = Book(book_id, name, url, score, comment_num, desc)
                for attr, value in book.__dict__.items():
                    value = re.sub(re.compile(r'\s+|\n|\t'), '', str(value))
                    setattr(book, attr, value)

                result.append(book)

            start += 20
    
        insert_database(result, tables[i])
        print('finished tag %s' % (tags[i]))

def insert_database(result, table_name):
    # 按照评分 & 评论数 排序
    result.sort(lambda a, b: -1 
        if ( float(a.score) > float(b.score) or
            (float(a.score) == float(b.score) and int(a.comment_num) > int(b.comment_num) ) )
            else 0
    )

    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    cursor.execute('drop table if exists %s' % (table_name))
    conn.execute('''CREATE TABLE %s
        (book_id TEXT PRIMARY KEY,
        name TEXT,
        score REAL,
        url TEXT,
        comment_num INT,
        description TEXT
        );''' % (table_name))

    # 注意sql_str中的 %s 需要加引号
    for book in result:
        try:
            sql_str = r"insert into '%s' values ('%s', '%s', %f, '%s', %d, '%s')" % (table_name, book.book_id, book.name, float(book.score), book.url, int(book.comment_num), book.description)
            cursor.execute(sql_str)
        except Exception as e:
            print(e)
            print(sql_str)

    cursor.close()
    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()
