import xlrd
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.signalmanager import dispatcher
from scrapy.utils.project import get_project_settings
from xlrd.timemachine import xrange


def call_floripa(imoveis= None):
    workbook = xlrd.open_workbook(
        '/home/henrique/Planilhas/floripa.xls')
    worksheet = workbook.sheet_by_index(0)
    imoveis = []
    results = []

    for row_num in xrange(worksheet.nrows):
        if row_num == 0:
            continue
        row = worksheet.row_values(row_num)
        imoveis.append(dict(codImovel=str(row[0]), inscricao=str(row[1])))

    def crawler_results(signal, sender, item, response, spider):
        results.append(item)

    dispatcher.connect(crawler_results, signal=signals.item_passed)
    process = CrawlerRunner(get_project_settings())
    process.crawl('floripaIPTU', imoveis=imoveis)
    process.run()

    print(results)
    return results


if __name__ == '__main__':
    print(call_floripa())