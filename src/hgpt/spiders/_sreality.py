import scrapy


class SRealitySpider(scrapy.Spider):
    name = "sreality"

    def start_requests(self):
        # GET request
        yield scrapy.Request("https://www.sreality.cz", meta={"playwright": True})
        # POST request
        yield scrapy.FormRequest(
            url="https://httpbin.org/post",
            formdata={"foo": "bar"},
            meta={"playwright": True},
        )

    def parse(self, response, **kwargs):
        # 'response' contains the page as seen by the browser
        return {"url": response.url}
