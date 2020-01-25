# -*- coding: utf-8 -*-
import scrapy
import xlrd
from xlrd.timemachine import xrange
import time
import uuid
import os
import re
from scrapy_splash import SplashFormRequest
from imagetyperzapi3.imagetyperzapi import ImageTyperzAPI
from scrapy.loader import ItemLoader
from floripa.items import FloripaItem, FloripaItemLoader


class FloripaiptuSpider(scrapy.Spider):
    name = 'floripaIPTU'
    start_urls = ['http://iptu2019.pmf.sc.gov.br/iptu-virtual/main-iptu///']

    def parse(self, response):
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
            data_atual = time.strftime('%d/%m/%y', time.localtime())
            url_modifica = 'http://iptu2019.pmf.sc.gov.br/iptu-virtual/main-iptu/segunda_via.dados.php?tp_entrada=xinscricao_internet&data=' + \
                data_atual+'&opcao=confere_entradas&cd_refr=' + inscricao + '&cd_refr_ano=2020'
            yield scrapy.FormRequest(
                url=url_modifica,
                method='GET', callback=self.parse_login, dont_filter=True, cb_kwargs={'codImovel': codImovel, 'inscricao': inscricao, 'grupo': grupo})

    def parse_login(self, response, codImovel, inscricao, grupo):
        status = response.xpath('//p[@class="atencao"]/text()').extract_first()
        if status == None:
            status = 'Com Débito'
            formdata = {'nu_insc_imbl': inscricao,
                        'ano-segunda-via-select': '2020',
                        'tipo-pagamento-radio': 'parcelado'}
            yield SplashFormRequest(
                url='http://iptu2019.pmf.sc.gov.br/iptu-virtual/main-iptu/index-segunda-via.php',
                method='POST', callback=self.com_debito, formdata=formdata, dont_filter=True,
                cb_kwargs={'codImovel': codImovel,
                           'inscricao': inscricao, 'grupo': grupo}, args={'wait': '2'}
            )
        else:
            status = self.cleanhtml(status)
            loader = FloripaItemLoader(FloripaItem(), response)
            loader.add_value('grupo', grupo)
            loader.add_value('codImovel', codImovel)
            loader.add_value('inscricao', inscricao)
            loader.add_value('status', status)
            yield loader.load_item()

    def com_debito(self, response, codImovel, inscricao, grupo):
        faturas = response.xpath('//table[@id="demo-foo-addrow"]/tbody/tr')
        nDams = []
        for fatura in faturas:
            numeroDam = fatura.xpath('./td[2]/text()').extract_first()
            numeroDam = numeroDam.replace('-', '')
            nDams.append(numeroDam)
            loader = FloripaItemLoader(FloripaItem(), fatura)
            loader.add_value('grupo', grupo)
            loader.add_value('codImovel', codImovel)
            loader.add_value('inscricao', inscricao)
            loader.add_value('status', 'Com Débito')
            loader.add_value('numeroDam', numeroDam)
            loader.add_xpath('tributo', './td[3]/text()')
            loader.add_xpath('parcela', './td[4]/text()')
            loader.add_xpath('vencimento', './td[5]/text()')
            loader.add_xpath('valor', './td[6]/text()')
            loader.add_xpath(
                'codBarra', './td[8]/a[2]/@onclick', re='\d{47}')
            yield loader.load_item()

        access_token = '2447DFA2F60747DABF7152A14142511F'
        ita = ImageTyperzAPI(access_token)
        balance = ita.account_balance()
        self.logger.info('Balance: {}'.format(balance))
        recaptcha_params = {
            'page_url': 'http://iptu2019.pmf.sc.gov.br/iptu-virtual/main-iptu/index-segunda-via.php',
            'sitekey': '6LfatIkUAAAAABA1IFcpmL9KkJbFCDsSPZGeaplW',
            'type': 2,
        }
        captcha_id = ita.submit_recaptcha(recaptcha_params)
        while ita.in_progress():
            time.sleep(5)

        recaptcha_response = ita.retrieve_recaptcha(captcha_id)

        formdata = {
            'data': '',
            'controle': 'ADMIN',
            'g-recaptcha-response': recaptcha_response
        }
        for numero in nDams:
            formdata['nu_dam[]'] = numero

        self.logger.info(formdata)
        request = SplashFormRequest(method='POST', dont_filter=True,  formdata=formdata, args={'wait': '2'},
                                    url='http://iptu2019.pmf.sc.gov.br/iptu-virtual/main-iptu/segunda_via_internet.pdf.php')
        path = request.url.split('/')[-1]
        # path = path.replace('.php', '')
        # path = self.file_name+codImovel+'_'+inscricao
        # path = path.replace('.', '')
        # path += '.pdf'
        # self.log(path)
        self.logger.info('Saving PDF %s', path)
        with open(path, 'wb') as f:
            f.write(request.body)
        self.log('##########################')
        self.log(request)
        self.log('##########################')

    def download(self, response):
        pass

    def cleanhtml(self, raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext
