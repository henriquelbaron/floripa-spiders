import re
import time;


class Utils:

    @staticmethod
    def cleanhtml(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    @staticmethod
    def get_today(format):
        return time.strftime(format, time.localtime())
