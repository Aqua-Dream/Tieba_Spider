from scrapy.exceptions import UsageError
from scrapy.commands import ScrapyCommand
import config
import filter
from scrapy.utils.conf import arglist_to_dict

class Command(ScrapyCommand):
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
        parser.add_option("-p", "--pages", nargs = 2, type="int", dest="pages", default=[],
                          help="set the range of pages you want to crawl")  
        parser.add_option("-g", "--good", action="store_true", dest="good_only", default=False,
                          help="only crawl good threads and their posts and comments")
        parser.add_option("-f", "--filter", type="str", dest="filter", default="",
                          help='set function name in "filter.py" to filter threads')
        parser.add_option("-s", "--see_lz", action="store_true", dest="see_lz", default=False,
                          help='enable "only see lz" mode')              
                          
    def set_pages(self, pages):
        if len(pages) == 0:
            begin_page = 1
            end_page = 999999
        else:
            begin_page = pages[0]
            end_page = pages[1]
        if begin_page <= 0:
            raise UsageError("The number of begin page must not be less than 1!")
        if begin_page > end_page:
            raise UsageError("The number of end page must not be less than that of begin page!")
        self.settings.set('BEGIN_PAGE', begin_page, priority='cmdline')
        self.settings.set('END_PAGE', end_page, priority='cmdline')

    def run(self, args, opts):
        self.set_pages(opts.pages)
        try:
            opts.spargs = arglist_to_dict(opts.spargs)
        except ValueError:
            raise UsageError("Invalid -a value, use -a NAME=VALUE", print_help=False)
        self.settings.set('GOOD_ONLY', opts.good_only)
        self.settings.set('SEE_LZ', opts.see_lz)
        if opts.filter:
            try:
                opts.filter = eval('filter.' + opts.filter)
            except:
                raise UsageError("Invalid filter function name!")
        self.settings.set("FILTER", opts.filter)
        cfg = config.config()
        if len(args) >= 3:
            raise UsageError("Too many arguments!")
            
        for i in range(len(args)):
            if isinstance(args[i], bytes):
                args[i] = args[i].decode("utf8")
        
        if not 'MYSQL_PORT' in cfg.config.keys():
            cfg.config['MYSQL_PORT'] = 3306
        
        self.settings.set('MYSQL_HOST', cfg.config['MYSQL_HOST'])
        self.settings.set('MYSQL_USER', cfg.config['MYSQL_USER'])
        self.settings.set('MYSQL_PASSWD', cfg.config['MYSQL_PASSWD'])
        self.settings.set('MYSQL_PORT', cfg.config['MYSQL_PORT'])

        tbname = cfg.config['DEFAULT_TIEBA']
        if len(args) >= 1:
            tbname = args[0]
            
        dbname = None    
        if tbname in cfg.config['MYSQL_DBNAME'].keys():
            dbname = cfg.config['MYSQL_DBNAME'][tbname]
        if len(args) >= 2:
            dbname = args[1]
            cfg.config['MYSQL_DBNAME'][tbname] = dbname
        if not dbname:
            raise UsageError("Please input database name!")
            
        self.settings.set('TIEBA_NAME', tbname, priority='cmdline')
        self.settings.set('MYSQL_DBNAME', dbname, priority='cmdline')
        
        config.init_database(cfg.config['MYSQL_HOST'], cfg.config['MYSQL_USER'], cfg.config['MYSQL_PASSWD'],cfg.config['MYSQL_PORT'], dbname)
        
        log = config.log(tbname, dbname, self.settings['BEGIN_PAGE'], opts.good_only, opts.see_lz)
        self.settings.set('SIMPLE_LOG', log)
        self.crawler_process.crawl('tieba', **opts.spargs)
        self.crawler_process.start()
        
        cfg.save()
