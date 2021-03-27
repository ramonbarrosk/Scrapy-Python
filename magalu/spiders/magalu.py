import scrapy
import json
from selenium import webdriver
from selenium_stealth import stealth

class MagaluSpider(scrapy.Spider):
    name = "magazine"
    cep = "57100000"

    def __init__(self):
        options =  webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        #options.add_argument("--headless")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        self.driver = webdriver.Chrome(options=options)
        stealth(self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
        )

    def start_requests(self):
        yield scrapy.Request(url="https://www.magazineluiza.com.br/smartphone/celulares-e-smartphones/s/te/tcsp?page=1", callback=self.parse_paginas)

    def parse_paginas(self,response):
        ultima_pagina = int(response.xpath('//li[@class="css-1a9p55p"][6]/a/text()').get())
        for i in range(ultima_pagina):
            url = f'https://www.magazineluiza.com.br/smartphone/celulares-e-smartphones/s/te/tcsp?page={i+1}'
            yield scrapy.Request(url=url, callback=self.parse_celular)

    def parse_celular(self, response):
        for celular in response.xpath('//ul/a[@data-css-rx7mj=""]'):
            link = celular.xpath('./@href').get()
            yield scrapy.Request(url=link, meta={'link':link},callback=self.parse)

    def parse(self,response):
        self.driver.get(response.meta['link'])
        try:
            cep  = self.driver.find_element_by_xpath('//input[@name="zipcode"]')
            cep.send_keys("57100000")
            botao = self.driver.find_element_by_xpath("//div[@class='freight-product__box']/div/button")
            self.driver.execute_script("arguments[0].click();", botao)  
        except Exception as e:
            print(e)
        dadosJson = response.xpath('//div[@class="header-product js-header-product"]/@data-product').get()
        dadosJson = json.loads(dadosJson)
        nome = dadosJson.get('fullTitle')
        valor = dadosJson.get('bestPriceTemplate')
        frete = self.driver.find_element_by_xpath('//div[contains(@class,"js-freight-info freight-product__freight-text")]').text
        
        yield {
            'nome_produto':nome,
            'valor_produto':valor,
            'valor_frete':frete
        }