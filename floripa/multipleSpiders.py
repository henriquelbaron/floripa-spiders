from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from scrapy.commands import ScrapyCommand
import xlrd
from xlrd.timemachine import xrange

class Command(ScrapyCommand):
    setting = get_project_settings()
    process = CrawlerProcess(setting)
    workbook = xlrd.open_workbook(
        '/home/henrique/Planilhas/floripa.xls')
    worksheet = workbook.sheet_by_index(0)

    for row_num in xrange(worksheet.nrows):
        if row_num == 0:
            continue
        row = worksheet.row_values(row_num)
        codImovel = str(row[0])
        inscricao = str(row[1])
        grupo = str(row[2])
        process.crawl('floripaIPTU',codImovel=codImovel, inscricao=inscricao) #query dvh is custom argument used in your scrapy
    process.start()