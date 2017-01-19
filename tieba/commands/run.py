import scrapy.commands.crawl as crawl
from scrapy.exceptions import UsageError
from scrapy.commands import ScrapyCommand
import config

class Command(crawl.Command):
    def syntax(self):
        return "<tieba_name> <database_name>"

    def short_desc(self):
        return "Crawl tieba"
        
    def long_desc(self):
        return "Crawl baidu tieba data to a MySQL database."
        
    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_option("-a", dest="spargs", action="append", default=[], metavar="NAME=VALUE",
                          help="set spider argument (may be repeated)")
        parser.add_option("-o", "--output", metavar="FILE",
                          help="dump scraped items into FILE (use - for stdout)")
        parser.add_option("-t", "--output-format", metavar="FORMAT",
                          help="format to use for dumping items with -o")
                          
        parser.add_option("-p", "--page", type="int", dest="page", default=9999999,
                          help="set the num of pages you want to crawl")                    

    def run(self, args, opts):
        if len(args) >= 3:
            raise UsageError()
        cfg = config.config()
        self.settings.set('MYSQL_HOST', cfg.config['MYSQL_HOST'])
        self.settings.set('MYSQL_USER', cfg.config['MYSQL_USER'])
        self.settings.set('MYSQL_PASSWD', cfg.config['MYSQL_PASSWD'])
        
        tbname = cfg.config['DEFAULT_TIEBA']
        if len(args) >= 1:
            tbname = args[0]
        if isinstance(tbname, unicode):
            tbname = tbname.encode('utf8')
            
        dbname = None    
        for i in cfg.config['MYSQL_DBNAME'].keys():
            if i.encode('utf8') == tbname:
                dbname = cfg.config['MYSQL_DBNAME'][i]
        if len(args) >= 2:
            dbname = args[1]
            cfg.config['MYSQL_DBNAME'][tbname.decode('utf8')] = dbname
        if not dbname:
            raise UsageError()
            
        self.settings.set('TIEBA_NAME', tbname, priority='cmdline')
        self.settings.set('MYSQL_DBNAME', dbname, priority='cmdline')
        self.settings.set('MAX_PAGE', opts.page, priority='cmdline')
        
        config.init_database(cfg.config['MYSQL_HOST'], cfg.config['MYSQL_USER'], cfg.config['MYSQL_PASSWD'], dbname)
        
        log = config.log(tbname, dbname)
        self.settings.set('SIMPLE_LOG', log)
        
        self.crawler_process.crawl('tieba', **opts.spargs)
        self.crawler_process.start()
        
        cfg.save()

        
            
  