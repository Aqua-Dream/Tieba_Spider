# -*- coding: utf-8 -*-

import json
import os
import sys
import MySQLdb
import warnings
import time
import csv
from io import open

class config:
    config_path = 'config.json'
    config = None

    def __init__(self):
        with open(self.config_path, 'r', encoding='utf8') as f:
            self.config = json.loads(f.read())
            # loads后若有中文 为unicode
    def save(self):
        with open(self.config_path, 'wb') as f:
            s = json.dumps(self.config, indent=4, ensure_ascii=False).encode('utf8')
            f.write(s)

class log:
    log_path = 'spider.log'
    
    def __init__(self, tbname, dbname, begin_page, good_only, see_lz):
        if not os.path.isfile(self.log_path):
            with open(self.log_path, 'wb') as f:
                row = ['start_time','end_time','elapsed_time','tieba_name','database_name', 'pages', 'etc']
                s = '\t'.join(row) + '\n'
                if not isinstance(s, bytes):
                    s = s.encode('utf8')
                f.write(s)
        self.tbname = tbname
        self.dbname = dbname
        self.begin_page = begin_page
        etc = []
        if good_only:
            etc.append('good_only')
        if see_lz:
            etc.append('see_lz')
        self.etc = '&'.join(etc)
        if not self.etc:
            self.etc = "None"
        self.start_time = time.time()
        
    def log(self, end_page):
        end_time = time.time()
        elapsed_time = '%.4g' % (end_time - self.start_time)
        start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.start_time))
        end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))
        tbname = self.tbname

        pages = '%d~%d'%(self.begin_page, end_page) if end_page >= self.begin_page else 'None'
        with open(self.log_path, 'ab') as f:
            row = [start_time, end_time, elapsed_time, tbname, self.dbname, pages, self.etc]
            s = '\t'.join(row) + '\n'
            if not isinstance(s, bytes):
                s = s.encode('utf8')
            f.write(s)
        
        
def init_database(host, user, passwd, dbname):
    warnings.filterwarnings('ignore', message = ".*exists.*")  
    warnings.filterwarnings('ignore', message = ".*looks like a.*") 
    db = MySQLdb.connect(host, user, passwd)
    tx = db.cursor()
    tx.execute('set names utf8mb4')
    tx.execute('create database if not exists `%s`default charset utf8mb4\
    default collate utf8mb4_general_ci;' % MySQLdb.escape_string(dbname).decode("utf8"))
    #要用斜引号不然报错
    #万恶的MySQLdb会自动加上单引号 结果导致错误
    db.select_db(dbname)
    tx.execute("create table if not exists thread(\
        id BIGINT(12), title VARCHAR(100), author VARCHAR(30), reply_num INT(4),\
        good BOOL, PRIMARY KEY (id)) CHARSET=utf8mb4;")
    tx.execute("create table if not exists post(\
        id BIGINT(12), floor INT(4), author VARCHAR(30), content TEXT,\
        time DATETIME, comment_num INT(4), thread_id BIGINT(12),PRIMARY KEY (id),\
        FOREIGN KEY (thread_id) REFERENCES thread(id)) CHARSET=utf8mb4;")
    tx.execute("create table if not exists comment(id BIGINT(12),\
        author VARCHAR(30), content TEXT, time DATETIME, post_id BIGINT(12),\
        PRIMARY KEY (id), FOREIGN KEY (post_id) REFERENCES post(id)) CHARSET=utf8mb4;")
    db.commit()
    db.close()