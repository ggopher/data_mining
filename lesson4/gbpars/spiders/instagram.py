import scrapy
import json

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['http://www.instagram.com/']
    login_url = 'https://www.instagram.com/login/account/ajax'
    def __init__(self, login, enc_password, *args, **kwargs):
        self.tags = ['python']
        self.login = login
        self.enc_passwd = enc_password
        super().__init__(*args, **kwargs)

    def parse(self, response, **kwargs):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self.login_url
                ,callback=self.parse()
                ,method='POST'
                ,formdata={
                    'username': self.login
                    ,'enc_password': self.enc_passwd
                ,}
                ,headers={'X_CSRFToken': js_data['config']['csrf_token']}
            )
        except AttributeError as e:
            if response.json().get('authentificated'):
                for tag in self.tags:
                    yield response.follow(f'/explore/tags/{tag}', callback=self.tag_parse, cb_kwargs={'param': tag})

    def tag_parse(self, response, **kwargs):
        print(1)

    def js_data_extract(self, response):
        script = response.xpath('//script[contains(text(), "window._sharedData =")]/text()').get()
        return json.loads(script.replace("window._sharedData = ", '')[:-1])

