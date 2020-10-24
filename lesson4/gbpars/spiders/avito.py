import scrapy


class AvitoSpider(scrapy.Spider):
    name = 'youla'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']
    zpath = {
        'brands': '//div[@class="TransportMainFilters_brandsList__2tIkv"]//a[@class="blackLink"]/@href'
        ,'ads': '//div[@id="serp"]//article//a[@data-target="serp-snippet-title"]/@href'
    }
    def parse(self, response, **kwargs):
        for url in response.xpath(xpath['brands']):
            yield response.follow(url, callback=self.brand_parse)

    def brand_parse(self, response, **kwargs):
        for url in response.xpath(xpath['ads']):
            yield response.follow(url, callback=self.ads_parse)

    def ads_parse(selfself, response, **kwargs):
        print(1)
