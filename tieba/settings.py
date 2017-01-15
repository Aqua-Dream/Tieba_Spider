# -*- coding: utf-8 -*-

TIEBA_NAME = u'仙五前修改'  #name of tieba to crawl
MYSQL_DBNAME = 'Pal5Q_Diy'  #name of database to store data


# start MySQL database configure setting
MYSQL_HOST = 'localhost'    #host
MYSQL_USER = 'root'         #user name
MYSQL_PASSWD = '`fmyl597013296'     #password
# end of MySQL database configure setting


BOT_NAME = 'tieba'

SPIDER_MODULES = ['tieba.spiders']
NEWSPIDER_MODULE = 'tieba.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html

ITEM_PIPELINES = {
    'tieba.pipelines.TiebaPipeline': 300,
}

LOG_LEVEL = 'WARNING'

COMMANDS_MODULE = 'tieba.commands'
