import json

class config:
    _config = None

    def __init__(self, config_path):
        self.config_path = config_path
        s = open(config_path, 'r').read()
        self._config = json.loads(s)
        
    def get_db_info():
        return (self._config['MYSQL_HOST'], self._config['MYSQL_USER'], self._config['MYSQL_PASSWD'])
        
    def set_data(tbname, dbname, time):
        data = self._config['data']
        data[tbname] = {'database': dbname, 'recent_crawl': time}
        
    def get_database(tbname):
        return self._config['data'][tbname]['database']
        
    def get_recent_crawl(tbname):
        return self._config['data'][tbname]['recent_crawl']
        
    def save(self):
        f = open(self.config_path, 'wb')
        s = json.dumps(self._config, indent=4, ensure_ascii=False)
        if isinstance(s, unicode):
            s = s.encode('utf8')
        f.write(s)
        f.close()
