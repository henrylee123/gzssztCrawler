# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from twisted.enterprise import adbapi
from gzssztCrawler.items import ListItem, ArticleItem


class GzssztcrawlerPipeline(object):

    insert_sql = {
        "ListItem": "insert into gzsszt_tbs_listHtml (farticle, furl, fpagenum) values (:1, :2, :3)",
        "ArticleItem": '''
            insert into gzsszt_tbs_listHtml (farticle, furl, fpagenum) values (:1, :2, :3)
            '''
    }

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            conn_dct=crawler.settings.get('ORACLE_CONN'))

    def __init__(self, conn_dct):
        self.dbpool = adbapi.ConnectionPool('cx_Oracle', **conn_dct)

    def process_item(self, item, spider):
        self.dbpool.runInteraction(self.insert_db, item)
        return item

    def insert_db(self, tx, item):
        t = type(item)
        insert_sql = self.insert_sql[t]
        try:
            cln_values = list(dict(item).values())
            tx.execute(insert_sql, cln_values)
        except Exception:
            pass

    def close_spider(self, spider):
        self.dbpool.close()
