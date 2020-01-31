from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher
from scrapy.settings import Settings
from scrapy.utils.project import get_project_settings

def crawl_koovs():
    settings = get_project_settings()
    crawler = CrawlerProcess(settings)
    dispatcher.connect(reactor.stop, signals.spider_closed)
    crawler.configure()
    crawler.crawl('floripaIPTU')
    crawler.start()
    reactor.run()


if __name__ == '__main__':
    print(crawl_koovs())