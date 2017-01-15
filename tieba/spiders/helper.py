# -*- coding: utf-8 -*-

import re
import urllib2
from bs4 import BeautifulSoup

pid_reg = re.compile(r'pid=([0-9]*)')
tid_reg = re.compile(r'/p/([0-9]*)')

def get_postid(url):
    return int(pid_reg.findall(url)[0])
def get_threadid(url):
    return int(tid_reg.findall(url)[0])    
    

def is_ad(s): #判断楼层是否为广告
    ad = s.xpath(u".//span[contains(text(), '广告')]")
    # 广告楼层中间有个span含有广告俩字
    return ad

'''
def get_datetime(s):
    for info in s.xpath(".//span[@class='tail-info']/text()").extract():
        info = info.strip()
        if is_datetime(info):
            return info

datetime_reg = re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}')
# 贴吧时间规范 yyyy-MM-dd HH:mm 
# 我们的目的不是检测规范性而是寻找时间 所以不需要严格检测
def is_datetime(s): #判断是不是贴吧格式的时间
    return datetime_reg.match(s)
'''

def parse_content(content):
    if not content or not content.strip():
        return None
    content = content.replace('\r', '\n') #古老的帖子会出现奇怪的\r
    s = BeautifulSoup(content, 'lxml')
    s = s.div if s.div else s.span  #post 和 comment 标签不同

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

def is_str(s): #NavigableString类型需要手动转换下
    if s.name: 
        return False
    return unicode(s)

def is_br(s):
    if s.name == 'br':
        return '\n'
    return False

def is_img(s):
    if s.name == 'img':
        src = unicode(s.get('src')).strip()
        for reg in emotion_reg:
            result = reg.findall(src)
            # 将常见表情换成对应文字
            if result:
                return emotion_text[int(result[0]) - 1]
        return ' ' + src + ' '
    return False

def is_video(s):
    t = unicode(s.get('class'))
    if u'video' in t:
        url = s.find('a').get('href').strip()
        assert(url)
        return ' ' + getJumpUrl(url) + ' '
    return False

#bs带的get_text功能，很好很强大
#粗体红字之类的都一句话搞定了
def other_case(s): 
    return s.get_text()

# 表情只处理最常用的，原因是电脑端和客户端各种版本表情种类繁多，地址又不尽相同。常用的(1~50号)表情已经可以覆盖大部分范围了。

emotion_text = (u'[呵呵]',u'[哈哈]',u'[吐舌]',u'[啊]',u'[酷]',u'[怒]',u'[开心]',u'[汗]',u'[泪]',u'[黑线]',u'[鄙视]',u'[不高兴]',u'[真棒]',u'[钱]',u'[疑问]',u'[阴险]',u'[吐]',u'[咦]',u'[委屈]',u'[花心]',u'[呼~]',u'[笑眼]',u'[冷]',u'[太开心]',u'[滑稽]',u'[勉强]',u'[狂汗]',u'[乖]',u'[睡觉]',u'[惊哭]',u'[升起]',u'[惊讶]',u'[喷]',u'[爱心]',u'[心碎]',u'[玫瑰]',u'[礼物]',u'[彩虹]',u'[星星月亮]',u'[太阳]',u'[钱币]',u'[灯泡]',u'[茶杯]',u'[蛋糕]',u'[音乐]',u'[haha]',u'[胜利]',u'[大拇指]',u'[弱]',u'[OK]')

emotion_reg = (
    re.compile(r'http://static.tieba.baidu.com/tb/editor/images/client/image_emoticon(50|[1-9]|[1-4][0-9])\.png'),
    re.compile(r'http://tb2.bdstatic.com/tb/editor/images/face/i_f([0-4][0-9]|50)\.png')
)


# 发送请求到 jump.bdimg.com/.. 来获取真实链接
# 阻止302跳转后可以大大节省时间 
class RedirctHandler(urllib2.HTTPRedirectHandler):      
    def http_error_302(self, req, fp, code, msg, headers):  
        raise Exception(headers.getheaders('location')[0])

def getJumpUrl(url):    
    req = urllib2.Request(url)    
    debug_handler = urllib2.HTTPHandler()    
    opener = urllib2.build_opener(debug_handler, RedirctHandler)      
    try:    
        opener.open(url)
    except Exception, e:
        return unicode(e)