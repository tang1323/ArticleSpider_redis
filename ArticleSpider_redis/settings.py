# Scrapy settings for ScrapyRedisTest project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'ArticleSpider_redis'

SPIDER_MODULES = ['ArticleSpider_redis.spiders']
NEWSPIDER_MODULE = 'ArticleSpider_redis.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'ScrapyRedisTest (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'ScrapyRedisTest.middlewares.ScrapyredistestSpiderMiddleware': 543,
# }


# 这是设置增量爬取中的优先级队列
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.PriorityQueue'

# scheduler翻译过来是调度器，是管理一个队列的
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# DUPEFILTER翻译过来是双过滤器
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

# 设置爬虫结束的时候是否保持redis数据库中的去生集合与任务队列
# 爬虫退出时不清空redis内的数据
SCHEDULER_PERSIST = True
# 这个就是pipelines在settings的配置，这里是放到redis中的
ITEM_PIPELINES = {
    'ArticleSpider_redis.pipelines.MysqlTwistedPipline': 3,# 这是异步插入数据库
    'scrapy_redis.pipelines.RedisPipeline': 1
}


# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   'ArticleSpider_redis.middlewares.RandomUsrAgentMiddlware': 543,  # 这是更换user_agent的，#数字越小，优先级越高
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3080.5 Safari/537.36"

# 在middlewares中重载了三个函数就是更换user-agent的
# 一个随机的user-Agent设置为随机
RANDOM_UA_TYPE = "random"

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    'ScrapyRedisTest.pipelines.ScrapyredistestPipeline': 300,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
# 设置redis数据库
REDIS_URL = 'redis://127.0.0.1:6379'

# LOG_LEVEL = 'DEBUG'

# Introduce an artifical delay to make use of parallelism. to speed up the
# crawl.
# 这是下载速度，那就是限速,己经在spider中设置
# DOWNLOAD_DELAY = 1


# 连接mysql数据库
MYSQL_HOST = "localhost"
MYSQL_DBNAME = "article_spider"
MYSQL_USER = "tangming"
MYSQL_PASSWORD = "130796"


SQL_DATETIME_FORMAT = "%Y-%M-%D %h:%M:%S"
SQL_DATE_FORMAT = "%Y-%M-%D"
