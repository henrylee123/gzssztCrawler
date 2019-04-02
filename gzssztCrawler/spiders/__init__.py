# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
from scrapy import Request, spiders, FormRequest
from queue import Queue, Empty


class MainSpider():

    url_queue = q = Queue()
    for page_num in range(1, 260761):
        url_queue.put(str(page_num))
    url = "http://cri.gz.gov.cn/Search/Result"
    form_data = {

    }

    def start_requests(self):
            while True:
                try:
                    page_num_s = self.url_queue.get_nowait()
                except Empty:
                    break

                self.form_data[""]
                yield FormRequest(
                    ur=self.url, method = 'GET',             # GET or POST
                    formdata = self.form_data)