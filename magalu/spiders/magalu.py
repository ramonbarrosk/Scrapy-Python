import scrapy
import json
import time
from scrapy_selenium import SeleniumRequest

class MagaluSpider(scrapy.Spider):
    name = "magazine"
    cep = "57100000"
    
    
    def start_requests(self):
        yield SeleniumRequest(url="https://www.magazineluiza.com.br/smartphone/celulares-e-smartphones/s/te/tcsp?page=1", callback=self.parse_celular)

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
        cep = driver.find_element_by_name("zipcode")
        botao = driver.find_element_by_xpath("//div[@class='freight-product__box']/div/button")
        cep.send_keys("57100000")
        driver.execute_script("arguments[0].click();",botao)
        dados = driver.find_element_by_xpath('/html/body/div[3]/div[5]/div[1]/div[3]')
        dados = dados.get_attribute('data-product')
        dadosJson = json.loads(dados)
        nome = dadosJson.get('fullTitle')
        valor = dadosJson.get('bestPriceTemplate')
        time.sleep(5)
        frete = driver.find_element_by_xpath('//div[contains(@class,"js-freight-info freight-product__freight-text")]').text
        yield {
            'nome_produto':nome,
            'valor_produto':valor,
            'valor_frete':frete
        }