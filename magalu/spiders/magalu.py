import scrapy
import json
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time

class MagaluSpider(scrapy.Spider):
    name = "magazine"
    cep = "57100000"

    def start_requests(self):
        yield scrapy.Request('https://www.magazineluiza.com.br/smartphone/celulares-e-smartphones/s/te/tcsp?page=1', callback=self.parse_paginas)

    def parse_paginas(self,response):
        ultima_pagina = int(response.xpath('//li[@class="css-1a9p55p"][6]/a/text()').get())
        for i in range(ultima_pagina):
            url = f'https://www.magazineluiza.com.br/smartphone/celulares-e-smartphones/s/te/tcsp?page={i+1}'
            yield scrapy.Request(url=url, callback=self.parse)
            
    def parse(self, response):
        for celular in response.xpath('//ul/a[@data-css-rx7mj=""]'):
            link = celular.xpath('./@href').get()
            yield scrapy.Request(url=link,meta = {'link':link},callback=self.getProduto)
         
    def getProduto(self,response):
        
        driver = webdriver.Firefox()
        driver.get(response.meta['link'])
        cep = driver.find_element_by_name("zipcode")
        botao = driver.find_element_by_xpath("//div[@class='freight-product__box']/div/button")
        cep.send_keys("57100000")
        driver.execute_script("arguments[0].click();",botao)
        time.sleep(5)
        dados = driver.find_element_by_xpath('/html/body/div[3]/div[5]/div[1]/div[3]')
        dados = dados.get_attribute('data-product')
        dadosJson = json.loads(dados)
        nome = dadosJson.get('fullTitle')
        valor = dadosJson.get('bestPriceTemplate')
        try:
            frete = driver.find_element_by_xpath('//div[@class="freight-product__box-container"]/table/tbody/tr/td[3]/span/span').text
        except NoSuchElementException:
            try:
                frete = driver.find_element_by_xpath('//div[@class="freight-product__box-container"]/table/tbody/tr[2]/td[@class="freight-product__box-item-delivery-price freight-product__box-item"]/span').text
            except NoSuchElementException:
                frete = "Produto indisponível"
        driver.quit()
        yield {
            'nome_produto':nome,
            'valor_produto': valor,
            'valor_frete': frete
        }


        

    