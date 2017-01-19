# -*- coding: utf-8 -*-

import scrapy
import json
from tieba.items import ThreadItem, PostItem, CommentItem
import helper
import time

class TiebaSpider(scrapy.Spider):
    name = "tieba"
    max_page = 9999
    
    def parse(self, response): #forum parser
        for sel in response.xpath('//li[contains(@class, "j_thread_list")]'):
            data = json.loads(sel.xpath('@data-field').extract_first())
            item = ThreadItem()
            item['id'] = data['id']
            item['author'] = data['author_name']
            item['reply_num'] = data['reply_num']
            item['good'] = data['is_good']
            if not item['good']:
                item['good'] = False
            item['title'] = sel.xpath('.//div[contains(@class, "threadlist_title")]/a/text()').extract_first()
            yield item
            meta = {'thread_id': data['id'], 'page': 1}
            url = 'http://tieba.baidu.com/p/%d' % data['id']
            yield scrapy.Request(url, callback = self.parse_post,  meta = meta)
        next_page = response.xpath('//a[@class="next pagination-item "]/@href')
        if next_page:
            self.max_page -= 1
            if self.max_page > 0:
                yield self.make_requests_from_url(next_page.extract_first())
            
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
                item['content'] = helper.parse_content(content, True)
                #以前的帖子, data-field里面没有thread_id
                item['thread_id'] = meta['thread_id']
                item['floor'] = data['content']['post_no']
                #只有以前的帖子, data-field里面才有date
                if 'time' in data['content'].keys():
                    item['time'] = data['content']['date']
                    #只有以前的帖子, data-field里面才有date
                else:
                    item['time'] = floor.xpath(".//span[@class='tail-info']")\
                    .re_first(r'[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}')
                yield item
        if has_comment:
            url = "http://tieba.baidu.com/p/totalComment?tid=%d&fid=1&pn=%d" % (meta['thread_id'], meta['page'])
            yield scrapy.Request(url, callback = self.parse_comment, meta = meta)
        next_page = response.xpath(u".//ul[@class='l_posts_num']//a[text()='下一页']/@href")
        if next_page:
            meta['page'] += 1
            url = response.urljoin(next_page.extract_first())
            yield scrapy.Request(url, callback = self.parse_post, meta = meta)

    def parse_comment(self, response):
        comment_list = json.loads(response.body)['data']['comment_list']
        for value in comment_list.values():
            comments = value['comment_info']
            for comment in comments:
                item = CommentItem()
                item['id'] = comment['comment_id']
                item['author'] = comment['username']
                item['post_id'] = comment['post_id']
                item['content'] = helper.parse_content(comment['content'], False)
                item['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(comment['now_time']))
                yield item
         