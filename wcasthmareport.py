# -*- coding: utf-8 -*-
'''
Created on Mon Mar  6 13:41:33 2017

@author: mmcvicar
'''

import scrapy
from loginform import fill_login_form

class MySpiderWithLogin(scrapy.Spider):
    name = 'my-spider'

    start_urls = [
        'http://somewebsite.com/some-login-protected-page',
        'http://somewebsite.com/another-protected-page',
    ]

    login_url = 'https://app.wellcentive.com/CHA/'

    login_user = 'cha admin'
    login_password = 'chachf5901'

    def start_requests(self):
        # let's start by sending a first request to login page
        yield scrapy.Request(self.login_url, self.parse_login)

    def parse_login(self, response):
        # got the login page, let's fill the login form...
        data, url, method = fill_login_form(response.url, response.body,
                                            self.login_user, self.login_password)

        # ... and send a request with our login data
        return FormRequest(url, formdata=dict(data),
                           method=method, callback=self.start_crawl)

    def start_crawl(self, response):
        # OK, we're in, let's start crawling the protected pages
        for url in self.start_urls:
            yield scrapy.Request(url)

    #def parse(self, response):
        # do stuff with the logged in response