# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst



class FloripaItem(scrapy.Item):
    default_output_processor = TakeFirst()
    file_urls = scrapy.Field()
    grupo = scrapy.Field()
    codImovel = scrapy.Field()
    inscricao = scrapy.Field()
    status = scrapy.Field()
    numeroDam = scrapy.Field()
    parcela = scrapy.Field()
    tributo = scrapy.Field()
    vencimento = scrapy.Field()
    valor = scrapy.Field()
    codBarra = scrapy.Field()

class FloripaVO(scrapy.Item):
    codImovel = scrapy.Field(
        output_processor=TakeFirst()
    )
    inscricao = scrapy.Field(
        output_processor=TakeFirst()
    )
    status = scrapy.Field(
        output_processor=TakeFirst()
    )
    nome = scrapy.Field(
        output_processor=TakeFirst()
    )
    cpfCnpj = scrapy.Field(
        output_processor=TakeFirst()
    )
    endereco = scrapy.Field(
        output_processor=TakeFirst()
    )
    faturas = scrapy.Field()
    pdfs = scrapy.Field()
