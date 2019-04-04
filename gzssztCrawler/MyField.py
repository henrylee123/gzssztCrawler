from scrapy.loader.processors import MapCompose, TakeFirst
import re
from scrapy import Field


def _utf8_to_gbk(string):
    if string is not str:
        string = str(string)
    return string.encode('gbk',errors='ignore').decode('gbk')


def _drop_blank_ntr(string):
    return re.sub(r'\n|\t|\r| ', '', string)


def oracle_field():
    """
    去掉 \n \r\ t与空格，再把utf8转成gbk
    :return:
    """
    return Field(
            input_processor=MapCompose(_utf8_to_gbk, _drop_blank_ntr),
        output_processor=TakeFirst()
    )

def oracle_article_field():
    """
    去掉 \n \r\ t与空格，再把utf8转成gbk
    :return:
    """
    return Field(
            input_processor=MapCompose(_utf8_to_gbk),
        output_processor=TakeFirst()
    )