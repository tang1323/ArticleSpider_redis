# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import codecs   # 可以避免编码的繁锁的工作
import json
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi   # 可以将mysqldb操作换成一个异步操作

import MySQLdb
import MySQLdb.cursors


class ArticlespiderOnePipeline(object):
    def process_item(self, item, spider):
        return item


# 保存到json文件中的类
class JsonWithEncodingPipeline(object):
    # 自定义json文件的导出
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding="utf-8")

    def process_item(self, item, spider):
        # 将item转换成dict
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        # 将文件写入到lines中
        self.file.write(lines)
        return item

    # 关闭文件
    def spider_closed(self, spider):
        self.file.close()

        class MysqlPipeline(object):
            # 采用同步的机制写入mysql中，量少的时候可以用这个方法，但量多就采用twisted这个框架去写，在下面那个MysqlTwistedPipline方法就是标准写法
            def __init__(self):
                self.conn = MySQLdb.connect('localhost', 'root', '130796', 'article_spider', charset="utf8",
                                            use_unicode=True)
                self.cursor = self.conn.cursor()  # 执行数据库用cursor

            def process_item(self, item, spider):  # 写mysql语句的函数
                insert_sql = """
                    insert into jobbole_artilce(title, url, create_date, url_object_id, front_image_url, front_image_path, comment_nums, fav_nums,praise_nums, tags, content)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                self.cursor.execute(insert_sql, (
                item["title"], item["url"], item["create_date"], item["fav_nums"]))  # 同步执行，如果不执行完这步就不会执行完下一步
                self.conn.commit()  # 同步执行，如果不执行完这步就不会执行完下一步
                # 那么就需要一种异步执行


# 这是异步的机制写入mysql中
class MysqlTwistedPipline(object):
    def __init__(self, dbpool):# 接收参数
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        # from MySQLdb.cursors import DictCursor
        dbparms = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            password = settings["MYSQL_PASSWORD"],
            charset ='utf8',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode = True
        )
        # ConnectionPool这是一个连接池，这是一个关键
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)

        return cls(dbpool)

    # 写mysql语句的函数
    def process_item(self, item, spider):
        # 使用twisted 将mysql插入变成异步执行
        # dbpool是一个容器
        query = self.dbpool.runInteraction(self.do_insert, item)
        # 处理异常，handle_error是随便定义的一个方法，item和spider是自己返回一个错误信息，想要返回什么自己往里加
        query.addErrback(self.handle_error, item, spider)
        return item

    # failure是自己传的
    def handle_error(self,failure, item, spider):
        # 处理异步插入的异常
        # 这一步很重要，是调试的根本入口，就是在爬取数据入数据库的时候出现异常都 是这里调试出来的
        print(failure)

    # 这个cursor是adbapi自己传进来的
    def do_insert(self, cursor, item):
        # 执行具体的插入
        # 根据不同的item构建不同的sql语句并插入到mysql中
        # insert_sql = """
        #                     insert into cnblogs_article(title, url, url_object_id, front_image_url, front_image_path, praise_nums, comment_nums, tags, content, create_date, fav_nums)
        #                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)ON DUPLICATE KEY UPDATE create_date = VALUES(create_date)
        #                 """
        # params = list()
        # params.append(item.get("title", ""))
        # params.append(item.get("url", ""))
        # params.append(item.get("url_object_id", ""))
        # front_image = ",".join(item.get("front_image_url", []))
        # params.append(front_image)
        # params.append(item.get("front_image_path", ""))
        # params.append(item.get("praise_nums", 0))  # 没有数据则为0
        # params.append(item.get("comment_nums", 0))  # 没有数据则为0
        # params.append(item.get("tags", ""))
        # params.append(item.get("content", []))
        # params.append(item.get("create_date", "1970-07-01"))
        # params.append(item.get("fav_nums", 0))  # 没有数据则为0
        # cursor.execute(insert_sql, tuple(params))
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)


class JsonExporterPipleline(object):
    # 调用scrapy提供的json export导出json文件
    def __init__(self):
        self.file = open('articleexport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding = "utf-8", ensure_ascii= False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


# 只处理封面图片
class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        # 判断如果没有封面图片时不执行以下语句,有就执行,好比知乎没有封面图片
        if "front_image_url" in item:
            for ok, value in results:
                image_file_path = value["path"]
                item["front_image_path"] = image_file_path
            pass

        return item

