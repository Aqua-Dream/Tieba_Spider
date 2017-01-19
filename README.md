#Tieba_Spider
贴吧爬虫，适合小型贴吧，尚未完工...

 - 多个spider合成一个
 - 记录时间，减少更新时的爬取数量(利用response传递消息)
 - config配置文件

## 系统及依赖参考
Ubuntu 14.04.4 64-bit
Python 2.7.6
mysql  Ver 14.14 Distrib 5.5.53

lxml (3.7.2)
beautifulsoup4 (4.5.3)
Twisted (16.6.0)
Scrapy 1.3.0
MySQL-python (1.2.5)

## 使用方法
先打开config.json文件，在其中配置好数据库的域名、用户名和密码。
```
scrapy run <贴吧名> <数据库名> <-p 页码>
```
其中贴吧名不含末尾的“吧”字，而数据库名则是要存入的数据库名字，数据库在爬取前会被创建，-p选项可以设置要爬取的前X页(每页50个帖子)，若不设置则全爬。例如
```
scrapy run 仙五前修改 Pal5Q_Diy
```
若在config.json里面已经配置好贴吧名和对应数据库名，则可以忽略数据库名，例如
```
scrapy run 仙五前修改
```
若不写参数，则爬取config.json里面DEFAULT的数据库，例如
```
scrapy run
```

## 数据库结构
To be continued...


