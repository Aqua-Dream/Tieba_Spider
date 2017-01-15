# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors
from urllib import quote

class TiebaPipeline(object):
    @classmethod
    def from_settings(cls, settings):
        return cls(settings)

    def __init__(self, settings):
        
        dbname = settings['MYSQL_DBNAME']
        tbname = settings['TIEBA_NAME']
        if not dbname.strip():
            raise ValueError("No database name!")
        if not tbname.strip():
            raise ValueError("No tieba name!")          
        if isinstance(tbname, unicode):
            settings['TIEBA_NAME'] = tbname.encode('utf8')

        self.settings = settings
        
        self.dbpool = adbapi.ConnectionPool('MySQLdb',
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8mb4',
            cursorclass = MySQLdb.cursors.DictCursor,
        )
        
    def open_spider(self, spider):
        if spider.name == 'thread':
            spider.start_urls = ["http://tieba.baidu.com/f?kw=" +\
                quote(self.settings['TIEBA_NAME'])]
        elif spider.name == "post":
            results = self.dbpool._runInteraction(self.dbpool._runQuery, 'select id from thread;')
            #从源码知，带下划线的是阻塞的
            url = 'http://tieba.baidu.com/p/%d'
            spider.start_urls = (url % row['id'] for row in results)
        elif spider.name == "comment":
            # sql = 'select id, thread_id, comment_num from post;'
            sql = 'select id from post;'
            results = self.dbpool._runInteraction(self.dbpool._runQuery, sql)
            def url_generator(results):
                url = 'http://tieba.baidu.com/p/totalComment?tid=4902778604&fid=1&pn=2'
                for result in results:
                    (pid, tid, cnum) = (result['id'], result['thread_id'], result['comment_num'])
                    pn = (cnum + 9) / 10 # 10回复每页
                    for i in range(pn):
                        yield url % (tid, pid, i + 1)
            
            spider.start_urls = url_generator(results)   
        else:
            raise ValueError("Undefined spider!")
        
    def process_item(self, item, spider):
        _conditional_insert = {
            'thread': self.insert_thread, 
            'post': self.insert_post, 
            'comment': self.insert_comment
        }
        query = self.dbpool.runInteraction(_conditional_insert[spider.name], item)
        query.addErrback(self._handle_error, item, spider)
        return item
        
    def insert_thread(self, tx, item):
        sql = "insert into thread values(%s, %s, %s, %s, %s) on duplicate key\
        update reply_num=values(reply_num), good=values(good)"
        # 回复数量和是否精品有可能变化，其余一般不变
        params = (item["id"], item["title"], item['author'], item['reply_num'], item['good'])
        tx.execute(sql, params)     
        
    def insert_post(self, tx, item):
        sql = "insert into post values(%s, %s, %s, %s, %s, %s, %s) on duplicate key\
        update content=values(content), comment_num=values(comment_num)"
        # 楼中楼数量和content(解析方式)可能变化，其余一般不变
        params = (item["id"], item["floor"], item['author'], item['content'], 
            item['time'], item['comment_num'], item['thread_id'])
        tx.execute(sql, params)
        
    def insert_comment(self, tx, item):
        tx.execute('set names utf8mb4')
        sql = "insert into comment values(%s, %s, %s, %s, %s) on duplicate key update content=values(content)"
        params = (item["id"], item['author'], item['content'], item['time'], item['post_id'])
        tx.execute(sql, params)
        
    #错误处理方法
    def _handle_error(self, fail, item, spider):
        spider.logger.error('Insert to database error: %s \
        When dealing with item: %s' %(fail, item))
