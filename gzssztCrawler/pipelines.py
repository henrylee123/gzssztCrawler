# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from twisted.enterprise import adbapi
import re


class GzssztcrawlerPipeline(object):
    table_operation ={
        "ListItem": {
            "table_name": "gzsszt_tbs_listHtml",
            "value_num": 0,
            "values": []
        },
        "ArticleItem": {
            "table_name": "gzsszt_tbs_articleHtml",
            "value_num": 0,
            "values": []
        }
    }
    batch_size = 5

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
        t = str(type(item))
        d = dict(item)

        t  = re.search("\.([^\.]+)'", t).group(1)

        cln_values = list(d.values())
        self.table_operation[t]["values"].append(cln_values)
        self.table_operation[t]["value_num"] += 1
        if self.table_operation[t]["value_num"] == self.batch_size:
            insert_sql = self.get_insert_sql(t, self.table_operation[t]["table_name"], list(d))
            try:
                a=  self.table_operation[t]["values"][:self.batch_size]
                tx.executemany(insert_sql, a)
            except Exception as e:
                print(str(e))
            self.table_operation[t]["values"] = self.table_operation[t]["values"][self.batch_size:]
            self.table_operation[t]["value_num"] -= self.batch_size

    def close_spider(self, spider):
        self.dbpool.close()

    def get_insert_sql(self,t, table_name, cln_name_list):
        """
        拼接sql
        """
        s = self.table_operation[t].get(table_name, self.add_new_sql(t, table_name, cln_name_list))
        return s

    def add_new_sql(self, t, table_name, cln_name_list):
        # 生成"col1, col2, col3, col4"
        cln = ','.join(cln_name_list)
        # 生成 :1,:2,:3
        value_format = ",".join([":"+str(num) for num in range(1, len(cln_name_list ) + 1)])
        sql =f'INSERT INTO {table_name} ({cln}) VALUES ({value_format})'
        self.table_operation[t]["insert_sql"] = sql
        return sql