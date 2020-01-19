# -*- coding: utf-8 -*-

import re
from six.moves.urllib import request
from bs4 import BeautifulSoup
from . import emotion


def is_ad(s): #判断楼层是否为广告
    ad = s.xpath(u".//span[contains(text(), '广告')]")
    # 广告楼层中间有个span含有广告俩字
    return ad

def parse_content(content):
    if not content or not content.strip():
        return None
    content = content.replace('\r', '\n') #古老的帖子会出现奇怪的\r
    s = BeautifulSoup(content, 'lxml')
    if s.html:
        s=s.html
    if s.body:
        s=s.body
    if s.div:
        s = s.div  #post 外层有个div
    if s.p:
        s = s.p
    l = list(s.children)
    for i in range(len(l)):
        parse_func = (is_str, is_br, is_img, is_video, other_case)
        for func in parse_func:
            try:
                ret = func(l[i])
            except:
                continue
            if ret is not False: 
                l[i] = ret
                break
    return strip_blank(''.join(l))

def strip_blank(s): #按个人喜好去掉空白字符
    s = re.sub(r'\n[ \t]+\n', '\n', s)
    s = re.sub(r'  +', ' ', s) #去掉多余的空格
    s = re.sub(r'\n\n\n+', '\n\n', s) #去掉过多的连续换行
    return s.strip()

def is_str(s): 
    if s.name: 
        return False
    #NavigableString类型需要手动转换下
    return str(s)

def is_br(s):
    if s.name == 'br':
        return '\n'
    return False

def is_img(s):
    # 处理了部分表情
    if s.name == 'img':
        src = str(s.get('src'))
        return emotion.get_text(src)
    return False

def is_video(s):
    t = str(s.get('class'))
    if 'video' in t:
        url = s.find('a').get('href')
        return ' ' + getJumpUrl(url) + ' '
    return False

#bs带的get_text功能，很好很强大
#粗体红字之类的都一句话搞定了
def other_case(s): 
    return s.get_text()



# 发送请求到 jump.bdimg.com/.. 来获取真实链接
# 阻止302跳转后可以大大节省时间 

class RedirctHandler(request.HTTPRedirectHandler):      
    def http_error_302(self, req, fp, code, msg, headers):  
        raise Exception(headers.get('location'))

def getJumpUrl(url):    
    req = request.Request(url)  
    opener = request.build_opener(RedirctHandler())      
    try:    
        opener.open(url)
    except Exception as e:
        return str(e)
