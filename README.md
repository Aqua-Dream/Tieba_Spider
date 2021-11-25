# Tieba_Spider
[Readme(EN)](README_en.md)

贴吧爬虫。


## 依赖参考
Python >= 3.6

mysql >= 5.5

beautifulsoup4 >= 4.6.0

**scrapy == 2.4.1**

mysqlclient >= 1.3.10

## 使用方法
先打开config.json文件，在其中配置好数据库的域名、用户名和密码。接着直接运行命令即可：
```
scrapy run <贴吧名> <数据库名> <选项>
```
其中贴吧名不含末尾的“吧”字，而数据库名则是要存入的数据库名字，数据库在爬取前会被创建。例如
```
scrapy run 仙五前修改 Pal5Q_Diy
```
但若要在控制台输入中文(非ASCII字符)，请确保控制台编码为UTF8。

若在config.json里面已经配置好贴吧名和对应数据库名，则可以忽略数据库名。若忽略贴吧名，则爬取config.json里面DEFAULT的数据库。

**特别提醒** 任务一旦断开，不可继续进行。因此SSH打开任务时，请保证不要断开连接，或者考虑使用后台任务或者screen命令等。

## 选项说明

|短形式|长形式     |参数个数|作用                              |举例                           |
|------|-----------|--------|----------------------------------|-------------------------------|
|-p    |--pages    |2       |设定爬取帖子的开始页和结束页      |scrapy run ... -p 2 5          |
|-g    |--good_only|0       |只爬精品帖                        |scrapy run ... -g              |
|-s    |--see_lz   |0       |只看楼主，即不爬非楼主的楼层      |scrapy run ... -s              |
|-f    |--filter   |1       |设定帖子过滤函数名(见`filter.py`) |scrapy run ... -f thread_filter| 

举例：
```
scrapy run 仙剑五外传 -gs -p 5 12 -f thread_filter
```
使用只看楼主模式爬仙剑五外传吧精品帖中第5页到第12页的帖子，其中能通过过滤器`filter.py`中的`thread_filter`函数的帖子及其内容会被存入数据库。

## 数据处理
对爬取的数据并非原样入库，会进行一些处理。

1. 广告楼层会被去掉(右下角有“广告”两字的楼层)。
2. 加粗和红字效果丢失为纯文本(beautifulsoup的get_text功能)。
3. 常用表情会转换为文字表达(emotion.json，欢迎补充)。
4. 图片和视频会变成对应链接(要获取视频链接需要拿到一个302响应)。

## 数据保存结构
 - thread
 
为各帖子的一些基本信息。

|属性     |类型        |备注                                                    |
|---------|------------|--------------------------------------------------------|
|id       |BIGINT(12)  |"http://tieba.baidu.com/p/4778655068" 的ID就是4778655068|
|title    |VARCHAR(100)|                                                        |
|author   |VARCHAR(30) |                                                        |
|reply_num|INT(4)      |回复数量(含楼中楼, 不含1楼)                             |
|good     |BOOL        |是否为精品帖                                            |


 - post

为各楼层的一些基本信息，包括1楼。

|属性       |类型       |备注                  |
|-----------|-----------|----------------------|
|id         |BIGINT(12) |楼层也有对应ID        |
|floor      |INT(4)     |楼层编号              |
|author     |VARCHAR(30)|                      |
|content    |TEXT       |楼层内容              |
|time       |DATETIME   |发布时间              |
|comment_num|INT(4)     |楼中楼回复数量        |
|thread_id  |BIGINT(12) |楼层的主体帖子ID，外键|


 - comment
 
楼中楼的一些信息。

|属性   |类型       |备注                      |
|-------|-----------|--------------------------|
|id     |BIGINT(12) |楼中楼也有ID，且和楼层共用|
|author |VARCHAR(30)|                          |
|content|TEXT       |楼中楼内容                |
|time   |DATETIME   |发布时间                  |
|post_id|BIGINT(12) |楼中楼的主体楼层ID，外键  |

爬取方式决定了comment有可能先于对应的post被爬取，从而外键错误。因此任务开始阶段数据库的外键检测会被关闭。

## 耗时参考
耗时和服务器带宽以及爬取时段有关，下面是我的阿里云服务器对几个贴吧的爬取用时，仅供参考。

|贴吧名    |帖子数|回复数 |楼中楼数|用时(秒)|
|----------|------|-------|--------|--------|
|pandakill |3638  |41221  |50206   |222.2   |
|lyingman  |11290 |122662 |126670  |718.9   |
|仙剑五外传|67356 |1262705|807435  |7188    |

下面几个吧是同一时刻爬取的：

|贴吧名     |帖子数|回复数|楼中楼数|用时(秒)|
|-----------|------|------|--------|--------|
|仙五前修改 |530   |3518  |7045    |79.02   |
|仙剑3高难度|2080  |21293 |16185   |274.6   |
|古剑高难度 |1703  |26086 |32941   |254.0   |

**特别提醒** 请注意下爬取数据的占用空间，别把磁盘占满了。

## 更新日志
更新后请先删除原有的日志`spider.log`。

2020-08-09更新：解决了只爬楼中楼前10层的问题。注：由于python官方已放弃对python 2的支持，此后版本将不再保证python 2能正常运行。

2020-02-23更新：解决了被百度识别为爬虫返回403的问题。

2018-06-13更新：新增支持python 3。请卸载原来的python库`mysql-python`，改为使用`mysqlclient`。

2017-03-23更新：修改了页选项参数形式，增加了只看楼主、只爬精品和自定义过滤帖子功能。

## 参考文献
[Scrapy 1.0 文档][1]

[Scrapy 源代码][2]

[Beautiful Soup的用法][3]

[Ubuntu/Debian 安装lxml的正确方式][4]

[Twisted adbapi 源代码][5]

[mysql升级8.0后遇到的坑][6]

有什么问题或建议欢迎到[我的主页][7]留言~

  [1]: http://scrapy-chs.readthedocs.io/zh_CN/1.0/
  [2]: https://coding.net/u/fmyl/p/scrapy
  [3]: https://cuiqingcai.com/1319.html
  [4]: http://www.cnblogs.com/numbbbbb/p/3434519.html
  [5]: https://github.com/twisted/twisted/blob/twisted-16.5.0/src/twisted/enterprise/adbapi.py
  [6]: https://www.shiqidu.com/d/358
  [7]: https://aqua.hk.cn/Programming/oew0fr/
