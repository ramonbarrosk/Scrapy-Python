import scrapy



class MagaluSpider(scrapy.Spider):
    name = "magazine"

    
   
    def start_requests(self):
        urls = [f'https://www.magazineluiza.com.br/smartphone/celulares-e-smartphones/s/te/tcsp?page={i}' for i in range(1,106)]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
    def parse(self, response):
        
        for celular in response.xpath('//ul/a[@data-css-rx7mj=""]'):
            nome_smartphone = celular.xpath('.//div/h3/text()\n').extract()
            valor_vista = celular.xpath('.//div/*[@data-css-lz0zr=""]/text()\n').extract()
            valor_prazo = celular.xpath('.//div/div/div[@data-css-1keosrk=""]/text()\n').extract()
           
            yield {
                'nome_smartphone' : nome_smartphone,
                'valor_vista' : valor_vista,
                'valor_prazo' : valor_prazo
            }
       