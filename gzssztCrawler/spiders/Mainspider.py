import uuid
from gzssztCrawler.items import ListItem, ArticleItem
from scrapy import Request, Spider, FormRequest
from queue import Queue, Empty
from scrapy.loader import ItemLoader
# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

class gzssztSpider(Spider):

    name = "gzsszt"

    url_queue = q = Queue()
    for page_num in range(1, 260761):
        url_queue.put(str(page_num))

    main_url = "http://cri.gz.gov.cn"

    url = "http://cri.gz.gov.cn/Search/Result"

    form_data = {
        "validateCode": "r39rg",
        "guid": "B06472433EE2DFD1512136CB54E94EFFA0163DD255C9BC91F4FA42F65C89277C",
        "keywords": "广州注册企业",
        "page": "",
    }

    def start_requests(self):
            while True:
                try:
                    page_num_s = self.url_queue.get_nowait()
                except Empty:
                    break

                self.form_data["page"] = page_num_s
                yield FormRequest(
                    url=self.url, method = 'GET',             # GET or POST
                    formdata = self.form_data)

    def parse(self, response):
        selector_list = response.xpath("//div[@class='inner-results']")
        for selector in selector_list:
            guid = uuid.uuid4().hex
            item_loader = ItemLoader(ListItem(), selector=selector)
            try:
                title = selector.xpath("./ul/li[2]").xpath("string(.)").extract()[0]
            except Exception as e:
                print(str(e))
                title = ""
            item_loader.add_value("fguid", guid)
            item_loader.add_value("ftitle", title)
            item_loader.add_xpath("furl", "./h3/a/@href")
            item_loader.add_xpath("fsocietycode", "./p[2]/text()")
            item_loader.add_xpath("fregistercode", "./ul/li[1]/text()")
            item_loader.add_xpath("finfo", "./p[1]/text()")
            item = item_loader.load_item()
            yield item

            try:
                url = item["furl"]
            except Exception:
                pass
            else:
                yield Request(url=self.main_url + url, meta={"guid": guid},
                              callback=self.parse_article)

    def parse_article(self, response):
        selector = response.xpath("//table[@class='table table-hover ']")[0]
        item_loader = ItemLoader(ArticleItem(), selector=selector)

        item_loader.add_value("fguid", response.meta["guid"])
        item_loader.add_xpath("fregistercode", "./tr[1]/text()")
        item_loader.add_xpath_string("ftitle", "./tr[contains(./th/text(), '名称')]/td")
        item_loader.add_xpath_string("fdutyperson", "./tr[contains(./th/text(), '法定代表人')]/td")
        item_loader.add_xpath_string("fsocietycode", "./tr[contains(./th/text(), '社会信用代码')]/td")
        item_loader.add_xpath_string("fmaincommercialtype", "./tr[contains(./th/text(), '主营项目类别')]/td")
        item_loader.add_xpath_string("fcommercialrange", "./tr[contains(./th/text(), '经营范围')]/td")
        item_loader.add_xpath_string("fpermissionrange", "./tr[contains(./th/text(), '许可经营范围')]/td")
        item_loader.add_xpath_string("fadress", "./tr[contains(./th/text(), '住所')]/td")
        item_loader.add_xpath_string("fregistermoney", "./tr[contains(./th/text(), '注册资本')]/td")
        item_loader.add_xpath_string("fcompanytype", "./tr[contains(./th/text(), '商事主体类型')]/td")
        item_loader.add_xpath_string("fSetuptime", "./tr[contains(./th/text(), '成立日期')]/td")
        item_loader.add_xpath_string("fOpenperiod", "./tr[contains(./th/text(), '营业期限')]/td")
        item_loader.add_xpath_string("fpermissiondate", "./tr[contains(./th/text(), '核发日期')]/td")
        item_loader.add_xpath_string("fgovenmentorgan", "./tr[contains(./th/text(), '登记机关')]/td")
        item_loader.add_xpath_string("fstate", "./tr[15]/td")
        item_loader.add_xpath_string("fconstitution", "./tr[contains(./th/text(), '章程')]/td")
        item_loader.add_xpath_string("fotherfile", "./tr[contains(./th/text(), '其他文件')]/td")
        item_loader.add_xpath_string("fremarks", "./tr[contains(./th/text(), '备注')]/td")
        item_loader.add_value("farticle", response.text)

        item = item_loader.load_item()
        yield item