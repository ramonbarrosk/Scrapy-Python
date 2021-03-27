import scrapy
import json
import time
from scrapy_selenium import SeleniumRequest

class MagaluSpider(scrapy.Spider):
    name = "magazine"
    cep = "57100000"
    
    def start_requests(self):
        yield SeleniumRequest(url="https://www.magazineluiza.com.br/smartphone/celulares-e-smartphones/s/te/tcsp?page=1", callback=self.parse_paginas)

    def parse_paginas(self,response):
        ultima_pagina = int(response.xpath('//li[@class="css-1a9p55p"][6]/a/text()').get())
        for i in range(ultima_pagina):
            url = f'https://www.magazineluiza.com.br/smartphone/celulares-e-smartphones/s/te/tcsp?page={i+1}'
            yield SeleniumRequest(url=url, callback=self.parse_celular)

    def parse_celular(self, response):
        for celular in response.xpath('//ul/a[@data-css-rx7mj=""]'):
            link = celular.xpath('./@href').get()
            yield SeleniumRequest(url=link, callback=self.parse)

      
    def parse(self,response):
        driver = response.request.meta['driver']
        try:
            cep  = driver.find_element_by_xpath('//input[@name="zipcode"]')
            cep.send_keys("57100000")
            botao = driver.find_element_by_xpath("//div[@class='freight-product__box']/div/button")
            driver.execute_script("arguments[0].click();", botao)  
        except Exception as e:
            print(e)
        dadosJson = response.xpath('//div[@class="header-product js-header-product"]/@data-product').get()
        dadosJson = json.loads(dadosJson)
        nome = dadosJson.get('fullTitle')
        valor = dadosJson.get('bestPriceTemplate')
        time.sleep(15)
        frete = driver.find_element_by_xpath('//div[contains(@class,"js-freight-info freight-product__freight-text")]').text
        
        yield {
            'nome_produto':nome,
            'valor_produto':valor,
            'valor_frete':frete
        }