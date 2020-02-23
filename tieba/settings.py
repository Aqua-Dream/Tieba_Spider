# -*- coding: utf-8 -*-

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
#LOG_LEVEL = 'INFO'

COMMANDS_MODULE = 'tieba.commands'

COOKIES_ENABLED = False
