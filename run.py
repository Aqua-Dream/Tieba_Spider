# -*- coding: utf-8 -*-

import os
import sys
import tieba.settings as settings
import MySQLdb
import warnings
import time

def init_database(dbname):
    warnings.simplefilter('ignore') 
    #都说了if not exists还报警告 = =
    db = MySQLdb.connect(settings.MYSQL_HOST,settings.MYSQL_USER,settings.MYSQL_PASSWD)
    tx = db.cursor()
    tx.execute('set names utf8mb4')
    tx.execute('create database if not exists `%s`default charset utf8mb4\
    default collate utf8mb4_general_ci;' % MySQLdb.escape_string(dbname))
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
    warnings.resetwarnings()
    
def help(msg=None):
    if msg:
        print(msg+'\n')
    print(u'用法：python run.py tieba_name database_name\n')
    print(u'其中，tieba_name是要爬的吧的名字，不含“吧”字；database_name是爬取的数据要存入的数据库名\n')
    print(u'tieba_name和database_name可以都忽略，这样就必须到tieba/settings.py中配置吧名和数据库名\n')
    print(u'settings.py里还有数据库域名、用户名和密码的配置，爬取前请先填好\n')
    os._exit(1)

logfile = 'crawl_log.txt'
def log(tbname, dbname, elapsed):
    try:
        f = open(logfile, 'a')
        now = time.strftime("[%Y-%m-%d %H:%M:%S] ", time.localtime())
        msg = now + u"爬取贴吧“%s”的内容到数据库`%s`，用时%.1f秒\n" 
        f.write(msg.encode('utf8') % (tbname, dbname, elapsed))
        f.close()
    except Exception, e:
        print(u'记录日志失败：%s' % e)
        
def main():
    start = time.time()
    try:
        settings.MYSQL_HOST
        settings.MYSQL_USER
        settings.MYSQL_PASSWD
    except AttributeError, e:
        help(u'settings.py 数据库信息未配置。\n'+str(e))
    if len(sys.argv) == 3:
        tbname, dbname = sys.argv[1], sys.argv[2]
    elif len(sys.argv) <= 1:
        try:
            tbname, dbname = settings.TIEBA_NAME, settings.MYSQL_DBNAME
        except AttributeError, e:
            help(u'数据库信息未配置且无参数。\n'+str(e))
    else:
        help()
        
    if isinstance(tbname, unicode):
        tbname = tbname.encode('utf8')
    if isinstance(dbname, unicode):
        dbname = dbname.encode('utf8')   
    init_database(dbname)
    cmd = 'scrapy crawl_tieba %s %s %s'
    spiders = ('thread', 'post', 'comment')
    for spider in spiders:
        os.system(cmd % (spider, tbname, dbname))
        print(u'爬取 %s 的任务已完成。\n' % spider)
        
    log(tbname, dbname,  time.time()-start)

if __name__ == '__main__':
    main()
