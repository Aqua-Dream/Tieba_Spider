# -*- coding: utf-8 -*-

import scrapy
import json
from tieba.items import ThreadItem, PostItem, CommentItem
from . import helper
import time
from math import ceil

class TiebaSpider(scrapy.Spider):
    name = "tieba"
    cur_page = 1    #modified by pipelines (open_spider)
    end_page = 9999
    filter = None
    see_lz = False
    my_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}
    
    def parse(self, response): #forum parser
        print("Crawling page %d..." % self.cur_page)
        for sel in response.xpath('//li[contains(@class, "j_thread_list")]'):
            data = json.loads(sel.xpath('@data-field').extract_first())
            if data['id'] == 1: # 去掉"本吧吧主火热招募"
                continue
            item = ThreadItem()
            item['id'] = data['id']
            item['author'] = data['author_name']
            item['reply_num'] = data['reply_num']
            item['good'] = data['is_good']
            if not item['good']:
                item['good'] = False
            item['title'] = sel.xpath('.//div[contains(@class, "threadlist_title")]/a/@title').extract_first()
            if self.filter and not self.filter(item["id"], item["title"], item['author'], item['reply_num'], item['good']):
                continue
            #filter过滤掉的帖子及其回复均不存入数据库
                
            yield item
            meta = {'thread_id': data['id'], 'page': 1}
            url = 'http://tieba.baidu.com/p/%d' % data['id']
            if self.see_lz:
                url += '?see_lz=1'
            yield scrapy.Request(url, callback = self.parse_post,  meta = meta, 
                headers=self.my_headers)
        next_page = response.xpath('//a[@class="next pagination-item "]/@href')
        self.cur_page += 1
        if next_page:
            if self.cur_page <= self.end_page:
                yield scrapy.Request('http:'+next_page.extract_first())
            
    def parse_post(self, response): 
        meta = response.meta
        has_comment = False
        for floor in response.xpath("//div[contains(@class, 'l_post')]"):
            if not helper.is_ad(floor):
                data = json.loads(floor.xpath("@data-field").extract_first())
                item = PostItem()
                item['id'] = data['content']['post_id']
                item['author'] = data['author']['user_name']
                item['comment_num'] = data['content']['comment_num']
                if item['comment_num'] > 0:
                    has_comment = True
                content = floor.xpath(".//div[contains(@class,'j_d_post_content')]").extract_first()
                #以前的帖子, data-field里面没有content
                item['content'] = helper.parse_content(content)
                #以前的帖子, data-field里面没有thread_id
                item['thread_id'] = meta['thread_id']
                item['floor'] = data['content']['post_no']
                #只有以前的帖子, data-field里面才有date
                if 'date' in data['content'].keys():
                    item['time'] = data['content']['date']
                    #只有以前的帖子, data-field里面才有date
                else:
                    item['time'] = floor.xpath(".//span[@class='tail-info']")\
                    .re_first(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}')
                yield item

        if has_comment:
            url = "http://tieba.baidu.com/p/totalComment?tid=%d&fid=1&pn=%d" % (meta['thread_id'], meta['page'])
            if self.see_lz:
                url += '&see_lz=1'
            yield scrapy.Request(url, callback = self.parse_totalComment, meta = meta, 
                headers=self.my_headers)
        next_page = response.xpath(u".//ul[@class='l_posts_num']//a[text()='下一页']/@href")
        if next_page:
            meta['page'] += 1
            url = response.urljoin(next_page.extract_first())
            yield scrapy.Request(url, callback = self.parse_post, meta = meta, 
                headers=self.my_headers)

    def parse_totalComment(self, response):
        meta = response.meta.copy()
        comment_list = json.loads(response.text)['data']['comment_list']
        if not comment_list:
            return
        for value in comment_list.values():
            comments = value['comment_info']
            for comment in comments:
                item = CommentItem()
                item['id'] = comment['comment_id']
                item['author'] = comment['username']
                item['post_id'] = meta['post_id'] = comment['post_id']
                item['content'] = helper.parse_content(comment['content'])
                item['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(comment['now_time']))
                yield item
            comment_pages = ceil(value['comment_num'] / 10.0)
            for i in range(1, comment_pages): # other pages
                url = "https://tieba.baidu.com/p/comment?tid=%d&pid=%d&pn=%d" % (meta['thread_id'], item['post_id'], i+1) 
                yield scrapy.Request(url, callback = self.parse_comment, meta = meta)
         
    def parse_comment(self, response):
        comment_list = response.xpath('body/li')
        for i in range(len(comment_list)-1):
            comment = comment_list[i]
            data = json.loads(comment.attrib['data-field'])
            item = CommentItem()
            item['id'] = data['spid']
            item['author'] = data['user_name']
            item['post_id'] = response.meta['post_id']
            item['content'] = helper.parse_content(comment.css('.lzl_content_main').get())
            item['time'] = comment.css('.lzl_time').xpath('./text()').get()
            yield item
