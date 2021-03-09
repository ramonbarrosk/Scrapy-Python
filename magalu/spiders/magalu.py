import scrapy
import json


class MagaluSpider(scrapy.Spider):
    name = "magazine"
    cep = "57100000"

    #Header da requisição do cep
    def header_cep(self,link):
        header = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'cookie': f'ml2_sid_c=%7B%22zip_code%22:%22{self.cep}%22%7D',
            'referer': link,
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }

        return header
    #request retorna um .json contendo o valor do frete
    def getFrete(self,vendedor,codigo):
        return f'https://www.magazineluiza.com.br/produto/calculo-frete/{self.cep}/{codigo}/{vendedor}.json'

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
            yield scrapy.Request(url=link,callback=self.getProduto)

    def getProduto(self,response):
        dadosJson = response.xpath('//div[@class="header-product js-header-product"]/@data-product').get()
        dadosJson = json.loads(dadosJson)
        codigo = dadosJson.get('sku')
        nome = dadosJson.get('fullTitle')
        valor = dadosJson.get('bestPriceTemplate')
        vendedor = dadosJson.get('seller')
        yield scrapy.Request(url=self.getFrete(vendedor,codigo),callback=self.setFrete,
                             meta = {'nome' : nome,'valor':valor})

    def setFrete(self,response):
        frete = json.loads(response.body)
        if frete.get('delivery') is not None and frete.get('delivery') != {}:
            frete = (frete.get('delivery')[0].get('price'))
        else:
            frete = "Não encontrado"
        yield {
            'nome_celular' : response.meta['nome'],
            'valor_celular' : response.meta['valor'],
            'valor_frete' : frete
        }