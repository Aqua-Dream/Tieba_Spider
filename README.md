#Tieba_Spider
贴吧爬虫。

## 系统及依赖参考
Ubuntu 14.04.4 64-bit

Python 2.7.6

mysql Ver 14.14 Distrib 5.5.53

lxml (3.7.2)

beautifulsoup4 (4.5.3)

Twisted (16.6.0)

Scrapy 1.3.0

MySQL-python (1.2.5)

## 使用方法
先打开config.json文件，在其中配置好数据库的域名、用户名和密码。接着直接运行命令即可：
```
scrapy run <贴吧名> <数据库名> <-p 页码>
```
其中贴吧名不含末尾的“吧”字，而数据库名则是要存入的数据库名字，数据库在爬取前会被创建，-p选项可以设置要爬取的前X页(每页50个帖子)，若不设置则全爬。例如
```
scrapy run 仙剑五外传 Pal5Q -p 100
```
若在config.json里面已经配置好贴吧名和对应数据库名，则可以忽略数据库名，例如
```
scrapy run 仙五前修改
```
若不写参数，则爬取config.json里面DEFAULT的数据库，例如
```
scrapy run
```
**特别提醒** 任务一旦断开，不可继续进行。因此SSH打开任务时，请保证不要断开连接，或者考虑使用后台任务或者screen命令等。

## 数据保存结构
 - thread
为各帖子的一些基本信息。

|属性|类型|备注|
|-|
|id|BIGINT(12)|"http://tieba.baidu.com/p/4778655068"的ID就是4778655068|
|title|VARCHAR(100)||
|author|VARCHAR(30)||
|reply_num|INT(4)|回复数量(含楼中楼, 不含1楼)|
|good|BOOL|是否为精品帖|


 - post

为各楼层的一些基本信息，包括1楼。

|属性|类型|备注|
|-|
|id|BIGINT(12)|楼层也有对应ID|
|floor|INT(4)|楼层编号|
|author|VARCHAR(30)||
|content|TEXT|楼层内容|
|time|DATETIME|发布时间|
|comment_num|INT(4)|楼中楼回复数量|
|thread_id|BIGINT(12)|楼层的主体帖子ID，外键|


 - comment
楼中楼的一些信息。

|属性|类型|备注|
|-|
|id|BIGINT(12)|楼中楼也有ID，且和楼层一样|
|author|VARCHAR(30)||
|content|TEXT|楼中楼内容|
|time|DATETIME|发布时间|
|post_id|BIGINT(12)|楼中楼的主体楼层ID，外键|

## 耗时参考
耗时和服务器带宽以及爬取时段有关，下面是我的阿里云服务器对几个贴吧的爬取用时，仅供参考。
|贴吧名|帖子数|回复数|楼中楼数|用时(秒)|
|-|
|pandakill|3638|41221|50206|222.2|
|lyingman|11290|122662|126670|718.9|
|仙剑五外传|67356|1262705|807435|7188|

下面几个吧是同一时刻爬取的：
|贴吧名|帖子数|回复数|楼中楼数|用时(秒)|
|-|
|仙五前修改|530|3518|7045|79.02|
|仙剑3高难度|2080|21293|16185|274.6|
|古剑高难度|1703|26086|32941|254.0|

**特别提醒** 请注意下爬取数据的占用空间，别把磁盘占满了。

## 参考文献
[Scrapy 1.0 文档][1]

[Scrapy 源代码][2]

[Beautiful Soup的用法][3]

[Ubuntu/Debian 安装lxml的正确方式][4]

[Twisted adbapi 源代码][5]

有什么问题或建议欢迎到[我的主页][6]留言~


  [1]: http://scrapy-chs.readthedocs.io/zh_CN/1.0/
  [2]: https://coding.net/u/fmyl/p/scrapy
  [3]: https://cuiqingcai.com/1319.html
  [4]: http://www.cnblogs.com/numbbbbb/p/3434519.html
  [5]: https://github.com/twisted/twisted/blob/twisted-16.5.0/src/twisted/enterprise/adbapi.py
  [6]: http://aqua.hk.cn