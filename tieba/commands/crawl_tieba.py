import scrapy.commands.crawl as crawl
from scrapy.exceptions import UsageError


class Command(crawl.Command):
    def syntax(self):
        return "<spider> <tieba_name database_name>"

    def short_desc(self):
        return "Crawl tieba"
        
    def long_desc(self):
        return "Crawl baidu tieba data to a MySQL database."

    def run(self, args, opts):
    
        if len(args) == 3:
            self.settings.set('TIEBA_NAME', args[1], priority='cmdline')
            self.settings.set('MYSQL_DBNAME', args[2], priority='cmdline')
        else:
            raise UsageError()
            
        spname = args[0]

        self.crawler_process.crawl(spname, **opts.spargs)
        self.crawler_process.start()
            
  