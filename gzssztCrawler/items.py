# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item
from gzssztCrawler.MyField import oracle_field, oracle_article_field


class ListItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    fguid = oracle_field()
    ftitle = oracle_field()
    furl = oracle_field()
    fsocietycode = oracle_field()
    fregistercode = oracle_field()
    finfo  = oracle_field()


class ArticleItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    fguid  = oracle_field()
    fregistercode  = oracle_field()
    ftitle  = oracle_field()
    fdutyperson  = oracle_field()
    fsocietycode   = oracle_field()
    fmaincommercialtype = oracle_field()
    fcommercialrange = oracle_field()
    fpermissionrange = oracle_field()
    fadress = oracle_field()
    fregistermoney = oracle_field()
    fcompanytype = oracle_field()
    fSetuptime = oracle_field()
    fOpenperiod = oracle_field()
    fpermissiondate = oracle_field()
    fgovenmentorgan = oracle_field()
    fstate = oracle_field()
    fconstitution = oracle_field()
    fotherfile = oracle_field()
    fremarks = oracle_field()
    farticle = oracle_article_field()
