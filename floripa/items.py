# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst
from scrapy.loader import ItemLoader


class FloripaItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class FloripaItem(scrapy.Item):
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
