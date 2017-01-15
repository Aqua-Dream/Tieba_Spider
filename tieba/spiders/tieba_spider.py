# -*- coding: utf-8 -*-

import scrapy
import json
from tieba.items import ThreadItem, PostItem, CommentItem
import helper

class TiebaSpider(scrapy.Spider):
    name = "tieba"
    up_to_date = False #确认更新信息都已爬完
    
    def parse(self, response): #forum parser

        for sel in response.xpath('//li[contains(@class, "j_thread_list")]'):
            if self.up_to_date:
                return
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
            

        next_page = response.xpath('//a[@class="next pagination-item "]/@href')
        if next_page:
            yield self.make_requests_from_url(next_page.extract_first())
            
    def parse_post(self, response):
        for floor in response.xpath("//div[contains(@class, 'l_post')]"):
            #from scrapy.shell import inspect_response
            #inspect_response(response, self)
            if not helper.is_ad(floor):
                data = json.loads(floor.xpath("@data-field").extract_first())
                item = PostItem()
                item['id'] = data['content']['post_id']
                item['author'] = data['author']['user_name']
                item['comment_num'] = data['content']['comment_num']
                content = floor.xpath(".//div[contains(@class,'j_d_post_content')]").extract_first()
                #以前的帖子, data-field里面没有content
                item['content'] = helper.parse_content(content)
                #以前的帖子, data-field里面没有thread_id
                item['thread_id'] = helper.get_threadid(response.url)
                item['floor'] = data['content']['post_no']
                #只有以前的帖子, data-field里面才有date
                try:
                    item['time'] = data['content']['date']
                    #只有以前的帖子, data-field里面才有date
                except:
                    item['time'] = floor.xpath(".//span[@class='tail-info']")\
                    .re_first(r'[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}')
                
                yield item
        next_page = response.xpath(u".//ul[@class='l_posts_num']//a[text()='下一页']/@href")
        if next_page:
            url = response.urljoin(next_page.extract_first())
            yield self.make_requests_from_url(url)


            
class PostSpider(scrapy.Spider):
    name = "post"
            
    def parse(self, response):
        for floor in response.xpath("//div[contains(@class, 'l_post')]"):
            #from scrapy.shell import inspect_response
            #inspect_response(response, self)
            if not helper.is_ad(floor):
                data = json.loads(floor.xpath("@data-field").extract_first())
                item = PostItem()
                item['id'] = data['content']['post_id']
                item['author'] = data['author']['user_name']
                item['comment_num'] = data['content']['comment_num']
                content = floor.xpath(".//div[contains(@class,'j_d_post_content')]").extract_first()
                #以前的帖子, data-field里面没有content
                item['content'] = helper.parse_content(content)
                #以前的帖子, data-field里面没有thread_id
                item['thread_id'] = helper.get_threadid(response.url)
                item['floor'] = data['content']['post_no']
                #只有以前的帖子, data-field里面才有date
                try:
                    item['time'] = data['content']['date']
                    #只有以前的帖子, data-field里面才有date
                except:
                    item['time'] = floor.xpath(".//span[@class='tail-info']")\
                    .re_first(r'[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}')
                
                yield item
        next_page = response.xpath(u".//ul[@class='l_posts_num']//a[text()='下一页']/@href")
        if next_page:
            url = response.urljoin(next_page.extract_first())
            yield self.make_requests_from_url(url)
            
            
class CommentSpider(scrapy.Spider):
    name = "comment"
        
    def parse(self, response):
        for floor in response.xpath("//li[contains(@class, 'lzl_single_post')]"): #各个楼层
            data = json.loads(floor.xpath("@data-field").extract_first())
            item = CommentItem()
            item['id'] = data['spid']
            item['author'] = data['user_name']
            item['post_id'] = helper.get_postid(response.url)
            span = floor.xpath(".//span[@class='lzl_content_main']").extract_first()
            item['content'] = helper.parse_content(span)
            item['time'] = floor.xpath(".//span[@class='lzl_time']/text()").extract_first()
            yield item            