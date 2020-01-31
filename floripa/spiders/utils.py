import re
import time
import os


class Utils:

    @staticmethod
    def cleanhtml(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    @staticmethod
    def get_today(format):
        return time.strftime(format, time.localtime())

    @staticmethod
    def create_file(path):
        if os.path.isdir(path):
            # self.logger.info('Pasta já criada')
            print('Pasta já criada')
        else:
            os.makedirs(path)
            # self.logger.info('Pasta criada')

    @staticmethod
    def find(regex, text, group, flag=0):
        search = re.search(regex, text, flag)
        try:
            return search.group(group)
        except Exception as e:
            return e    

    @staticmethod
    def find_all(regex, text, group, flag=0):
        matchs = []
        try:
            # return re.findall(regex, text, flag).group(group)
            for match in re.finditer(regex, text, flag):
                matchs.append(match.group(group))
            if not matchs:
                raise Exception('REGEX NOT MATCH')
            return matchs
        except Exception as e:
            return e

    """
    re.I	re.IGNORECASE	ignore case.
    re.M	re.MULTILINE	make begin/end {^, $} consider each line.
    re.S	re.DOTALL	make . match newline too.
    re.U	re.UNICODE	make {\w, \W, \b, \B} follow Unicode rules.
    re.L	re.LOCALE	make {\w, \W, \b, \B} follow locale.
    re.X	re.VERBOSE	allow comment in regex.
    http://xahlee.info/python/python_regex_flags.html
    """
