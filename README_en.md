# Tieba_Spider
[Readme(CN)](README.md)

Spider for [Baidu Tieba](https://tieba.baidu.com). Crawl threads, posts and comments, and store them into MySQL database. 

## Dependency
Python >= 3.6

mysql >= 5.5

beautifulsoup4 >= 4.6.0

scrapy >= 2.4

mysqlclient >= 1.3.10

## Usage
First time: Edit `config.json`. Fill in database host, username as well as password.

Command:
```
scrapy run <Tieba_Name> <Database_Name> <Option>
```
You should not include the extra tail character `吧` in tieba name. Database will be created automatically if not exists. 

Example:
```
scrapy run 仙五前修改 Pal5Q_Diy
```
Attention: If you type in non-ASCII character, please make sure that the encoding of console is `UTF8`.

You can omit database name if is has been specified in `config.json`. Tieba name can also be ignored if you would like to crawl the **DEFAULT_TIEBA**.

**Attention** Pause is not supported. Once the task is interrupted, you have to restart it.

## Option

|Short |Long       |Args    |Function                              |Example                        |
|------|-----------|--------|--------------------------------------|-------------------------------|
|-p    |--pages    |2       |The start and end page to be crawled  |scrapy run ... -p 2 5          |
|-g    |--good_only|0       |Only crawl good threads               |scrapy run ... -g              |
|-s    |--see_lz   |0       |Only crawl posts from original poster |scrapy run ... -s              |
|-f    |--filter   |1       |Name of filter (See `filter.py`)      |scrapy run ... -f thread_filter| 

Example：
```
scrapy run 仙剑五外传 -gs -p 5 12 -f thread_filter
```
Crawl tieba `仙剑五外传` of good threads from page 5 to 12. Only the threads that can pass `thread_filter` function would be recorded. For each thread, only posts from original poster would be recorded.

## Text Cleaning
The crawled message would be modified as follows:

1. Advertisements floor (with `广告` on the bottom right) would be discarded。
2. Bold or red text effects would be discarded.
3. Frequent used emtion picture would be converted to text (by emotion.json).
4. Pictures and videos would be stored as their link.

## Database Structure
 - thread
 
Base information of each thread.

|Attribute|Type        |Remark                                                  |
|---------|------------|--------------------------------------------------------|
|id       |BIGINT(12)  |"http://tieba.baidu.com/p/4778655068".ID = 4778655068   |
|title    |VARCHAR(100)|                                                        |
|author   |VARCHAR(30) |                                                        |
|reply_num|INT(4)      |Including comment; excluding the first floor            |
|good     |BOOL        |                                                        |


 - post

Information of each post (including the first floor).

|Attribute  |Type       |Remark                               |
|-----------|-----------|-------------------------------------|
|id         |BIGINT(12) |                                     |
|floor      |INT(4)     |                                     |
|author     |VARCHAR(30)|                                     |
|content    |TEXT       |                                     |
|time       |DATETIME   |Post time                            |
|comment_num|INT(4)     |                                     |
|thread_id  |BIGINT(12) |Corresponding thread id (foreign key)|


 - comment
 
Information of each comment.

|Attribute|Type       |Remark                             |
|---------|-----------|-----------------------------------|
|id       |BIGINT(12) |                                   |
|author   |VARCHAR(30)|                                   |
|content  |TEXT       |                                   |
|time     |DATETIME   |Post time                          |
|post_id  |BIGINT(12) |Corresponding post id (foreign key)|

It is possible that comment is crawled before its corresponding post. Therefore, to avoid foreign key error, constraints detection would be stopped during crawling.

## Time
Crawling time is mainly decided by the network. Belowing data are for your reference:

|Tieba Name|Thread Num|Reply Num|Comment Num|Time(s) |
|----------|----------|---------|-----------|--------|
|pandakill |3638      |41221    |50206      |222.2   |
|lyingman  |11290     |122662   |126670     |718.9   |
|仙剑五外传|67356     |1262705  |807435     |7188    |

## References
[Scrapy 1.0 文档][1]

[Scrapy 源代码][2]

[Beautiful Soup的用法][3]

[Ubuntu/Debian 安装lxml的正确方式][4]

[Twisted adbapi 源代码][5]

[mysql升级8.0后遇到的坑][6]


  [1]: http://scrapy-chs.readthedocs.io/zh_CN/1.0/
  [2]: https://coding.net/u/fmyl/p/scrapy
  [3]: https://cuiqingcai.com/1319.html
  [4]: http://www.cnblogs.com/numbbbbb/p/3434519.html
  [5]: https://github.com/twisted/twisted/blob/twisted-16.5.0/src/twisted/enterprise/adbapi.py
  [6]: https://www.shiqidu.com/d/358
