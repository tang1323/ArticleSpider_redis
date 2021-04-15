# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from datetime import datetime
import scrapy
import re
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst,Join

# from ArticleSpider.utils.common import extract_num# 去common调用extract_num这个函数
# from ArticleSpider.settings import SQL_DATETIME_FORMAT,SQL_DATE_FORMAT


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def add_cnblogs(value): # 谁调用这个方法谁后面就有一个-tangming
    return value+"男"


def date_convert(value):
    # 处理时间的格式，datetime类型变成date,而且只取日期
    try:
        create_date = datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        create_date = datetime.now().date()
        return create_date


def get_nums(value):
    # 把点赞数量或者评论数量变成int类型，这样在数据更好检索
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums


def remove_comment_tags(value):
    # value = "三国梦-lk,编辑,收藏"，先split成列表，然后取三国梦-lk
    return value.split(",")[0]


def return_value(value):
    return value


# 知乎和其他网站都可以用这个方法，这是分词用的生成一个suggest
# def gen_suggests(index, info_tuple):
#     # 根据字符串生成搜索建议数组
#     used_words = set()  # 为什么要设置一个set，是因为在后面要去重
#     suggests = []   # 这就是我们要返回的一个数组
#     for text, weight in info_tuple:
#         if text:
#             # 调用es的anlyzer接口分析字符串, 分词和大小的转换
#             words = es.indices.analyze(index=index, analyzer="ik_max_word", params={'filter':["lowercase"]}, body=text)
#             anylyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"])>1])# 大于一是过滤单个字符的，那是没有意义的
#             # 已经存在过的单词过滤掉
#             new_works = anylyzed_words - used_words
#         else:
#             new_works = set()
#
#         if new_works:
#             suggests.append({"input":list(new_works), "weight":weight})
#     return suggests


# 我们都用这个自定义的itemLoader来做解析，这个是给文章cnblogs的item
class ArticleItemLoader(ItemLoader):
    """
    是用了itemloader才有这个预处理， input_processor，output_processsor
    可以这么来看 Item 和 Itemloader：Item提供保存抓取到数据的容器，而 Itemloader提供的是填充容器的机制。
    第一个是输入处理器（input_processor） ，当这个item，title这个字段的值传过来时，可以在传进来的值上面做一些预处理。
    第二个是输出处理器（output_processor） ， 当这个item，title这个字段被预处理完之后，输出前最后的一步处理。
    """
    # 自定义itemLoader
    default_output_processor = TakeFirst()# list转换成str


class CnblogsArticleItem(scrapy.Item):
    """
    是用了itemloader才有这个预处理， input_processor，output_processsor
    可以这么来看 Item 和 Itemloader：Item提供保存抓取到数据的容器，而 Itemloader提供的是填充容器的机制。
    第一个是输入处理器（input_processor） ，当这个item，title这个字段的值传过来时，可以在传进来的值上面做一些预处理。
    第二个是输出处理器（output_processor） ， 当这个item，title这个字段被预处理完之后，输出前最后的一步处理。
    """
    title = scrapy.Field(
        input_processor = MapCompose(lambda x:x+ "-风骚", add_cnblogs),# 预处理函数,会调用lambda函数,也会拿到一个value值给add_jobbole
    )# 标题

    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert),
        output_processsor = TakeFirst()
    )# 日期

    url = scrapy.Field()# 文章网址

    url_object_id = scrapy.Field()

    front_image_url = scrapy.Field(
        output_processor = MapCompose(return_value)
    )# 封面图片

    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor = MapCompose(get_nums)
    )# 点赞数

    comment_nums = scrapy.Field(
        input_processor = MapCompose(get_nums)
    ) # 评论数

    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    ) # 感兴趣数

    tags = scrapy.Field(
        input_processor = MapCompose(remove_comment_tags),
        # output_processor = Join(",")# list转换成str
    ) # 标签

    content = scrapy.Field() # 文章内容

    def get_insert_sql(self):
        insert_sql = """
                    insert into cnblogs_article(title, url, url_object_id, front_image_url, front_image_path, praise_nums, comment_nums, tags, content, create_date, fav_nums)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)ON DUPLICATE KEY UPDATE create_date = VALUES(create_date)
                """
        params = (
            self.get("title", ""),
            self.get("url", ""),
            self.get("url_object_id", ""),
            self.get("front_image_url", ""),
            self.get("front_image_path", ""),
            self.get("praise_nums", 0),
            self.get("comment_nums", 0),
            self.get("tags", ""),
            self.get("content", ""),
            self.get("create_date", "1970-07-01"),
            self.get("fav_nums", 0),
        )

        # 返回到pipelines中的do_insert，因为那里调用了get_sql，得返回去值
        return insert_sql, params
