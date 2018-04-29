#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "husterxsp"

import web
import sys
import json
import sqlite3
import os

reload(sys)
sys.setdefaultencoding("utf-8")

render = web.template.render('templates/')

tags = ['小说', '中国小说', '文学', '中国文学', '外国文学']
tables = ['novel', 'cn_novel', 'literature', 'cn_literature', 'fo_literature']

urls = (
    '/', 'index'
)

class Book(object):
    def __init__(self, book_id, name, score, url, comment_num, desc):
        self.book_id = book_id
        self.name = name
        self.score = score
        self.url = url
        self.comment_num = comment_num
        self.description = desc

class index:
    def GET(self):
        res = {
            'tags': [],
            'tables': []
        }
        res['tags'] = tags
        for table_name in tables:
            res['tables'].append(read_database(table_name))

        return render.index(json.dumps(res))

def read_database(table_name):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    cursor.execute('select * from "%s"' % table_name)
    values = cursor.fetchall()

    cursor.close()
    conn.close()

    for index in range(len(values)):
        item  = values[index]
        # 转换为dict便于前端的table展示
        values[index] = Book(item[0], item[1], item[2], item[3], item[4], item[5]).__dict__
    return values

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()