# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import re, time, requests, retrying
from urllib.parse import quote
from scrapy import signals
from verifyCode.ruoKuai import RuoKuai


class DownloaderMiddlewareUnkownError(Exception):
    pass


class GzssztcrawlerSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class GzssztcrawlerDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        """
        resp通过检查，则有效，无效的话修理相对应的request，再扔到请求池中
        """
        if self.__check_response(response):
            return response
        else:
            return self.__fix_request(request, spider)

    def __check_response(self, response):
        check_string = "".join(response.xpath("//div[@class='row']").xpath("string(.)").extract())
        if "输入精确" in check_string:
            return False
        else:
            return True

    def __fix_request(self, request, spider):
        """
        修理好request
        """
        url = request.url
        result = re.search("validateCode=(.+)&guid=(.+)&", url)
        validateCode, guid = result.group(1), result.group(2)
        try:
            # 看看这个不通过的request的vcode与spider的vcode是否一样，分两种情况：
            # 1.不一样，code不一定无效，还没更新到request里而已
            # 2.一样，code无效
            j = spider.form_data["validateCode"] == validateCode
        except Exception:
            pass
        else:
            if not j:
                # 1.更新code到request
                self.__renew_url_param(request,
                        spider.form_data["validateCode"], spider.form_data["guid"])
                return request
        # 2.重新获取验证码，更新到request里
        self.__validate(spider)
        self.__renew_url_param(request, spider.form_data["validateCode"], spider.form_data["guid"])

        return request

    def __renew_url_param(self, request, validateCode, guid):
        """
        更新参数到request
        """
        tmp = re.sub("validateCode=(.+)&", validateCode, request.url)
        url = re.sub("guid=(.+)&", guid, tmp)

        request._set_url(url)

    def __validate(self, spider):
        """
        完成验证流程
        """
        guid, code = self.check_v_code()
        search_word = spider.form_data["keywords"]
        spider.form_data["validateCode"] = code
        spider.form_data["guid"] = guid
        requests.get(f"http://cri.gz.gov.cn/Search/Result?validateCode={code}&guid={guid}&keywords={quote(search_word)}")

    @retrying.retry(stop_max_attempt_number=10)
    def check_v_code(self):
        """
        验证码验证
        """
        # 获取验证码
        t = int(time.time()*1000)
        guid = requests.get(f"http://cri.gz.gov.cn/Search/NewGuid?t={t}").text
        validateCode_bytes = requests.get(f"http://cri.gz.gov.cn/Search/ValidateCode?t={t}&guid={guid}").content
        #识别验证码
        rk = RuoKuai()
        rk.load_img(validateCode_bytes)
        code = rk.get_verify_code()
        # 检验识别结果
        url = f"http://cri.gz.gov.cn/Search/CheckVCode?vcode={code}&guid={guid}&t={t}"
        resp = requests.get(url)
        if "false" in resp.content.decode("utf-8"):
            raise Exception("验证码错误")
        else:
            return guid, code

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
