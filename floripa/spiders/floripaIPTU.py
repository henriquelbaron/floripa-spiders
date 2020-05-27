# -*- coding: utf-8 -*-
import os
import time
import uuid
import json
import scrapy
# import xlrd
import re
# from dbc_api_python3.deathbycaptcha import SocketClient
# from xlrd.timemachine import xrange
from imagetyperzapi3.imagetyperzapi import ImageTyperzAPI
from scrapy.loader import ItemLoader
import slate3k as slate


from floripa.items import FloripaVO
from floripa.spiders.utils import Utils


class FloripaiptuSpider(scrapy.Spider):
    file_name = '/home/files/FLORIPA_IPTU/' + \
        Utils.get_today('%d_%m_%y') + '/' + str(uuid.uuid1()) + '/'
    name = 'floripaIPTU'
    ita = ImageTyperzAPI('')

    def __init__(self, imoveis=None):
        self.imoveis = imoveis

    def start_requests(self):
        # workbook = xlrd.open_workbook(
        #     '/home/henrique/Planilhas/floripa.xls')
        # worksheet = workbook.sheet_by_index(0)
        # imoveis = []
        # for row_num in xrange(worksheet.nrows):
        #     if row_num == 0:
        #         continue
        #     row = worksheet.row_values(row_num)
        #     imoveis.append(dict(codImovel=str(row[0]), inscricao=str(row[1])))
        
        # self.imoveis = imoveis
        self.logger.info(self.imoveis)
        for imovel in self.imoveis:
            data_atual = Utils.get_today('%d/%m/%y')
            url_modifica = 'http://iptu2019.pmf.sc.gov.br/iptu-virtual/main-iptu/segunda_via.dados.php?tp_entrada=xinscricao_internet&data=' + \
                           data_atual + '&opcao=confere_entradas&cd_refr=' + \
                imovel['inscricao'] + '&cd_refr_ano=2020'
            yield scrapy.FormRequest(
                url=url_modifica, errback=self.error,
                method='GET', callback=self.parse_login,
                cb_kwargs={'imovel': imovel})

    def parse_login(self, response, imovel):
        status = response.xpath('//p[@class="atencao"]/text()').extract_first()
        if status is None:
            self.logger.info('Com Débito')
            formdata = {'nu_insc_imbl': imovel['inscricao'],
                        'ano-segunda-via-select': '2020',
                        'tipo-pagamento-radio': 'parcelado'}
            yield scrapy.FormRequest(
                url='http://iptu2019.pmf.sc.gov.br/iptu-virtual/main-iptu/index-segunda-via.php',
                method='POST', callback=self.com_debito, formdata=formdata, errback=self.error,
                cb_kwargs={'imovel': imovel}
            )
        else:
            status = Utils.cleanhtml(status)
            self.logger.info(status)
            loader = ItemLoader(FloripaVO(), response)
            loader.add_value('codImovel', imovel['codImovel'])
            loader.add_value('inscricao', imovel['inscricao'])
            loader.add_value('status', status)
            yield loader.load_item()

    def com_debito(self, response, imovel):
        linhas = response.xpath('//table[@id="demo-foo-addrow"]/tbody/tr')
        nDams = []

        for fatura in linhas:
            numeroDam = fatura.xpath('./td[2]/text()').extract_first()
            nDams.append(numeroDam.replace('-', ''))
            # faturas = {}
            # faturas['codImovel'] = codImovel
            # faturas['inscricao'] = inscricao
            # faturas['numeroDam'] = numeroDam
            # faturas['tributo'] = fatura.xpath('./td[3]/text()').extract_first()
            # faturas['parcela'] = fatura.xpath('./td[4]/text()').extract_first()
            # faturas['vencimento'] = fatura.xpath('./td[5]/text()').extract_first()
            # faturas['valor'] = fatura.xpath('./td[6]/text()').extract_first()
            # faturas['codBarra'] = fatura.xpath('./td[8]/a[2]/@onclick').re(r'\d{47}')[0]
            # # yield faturas;
            # floripaVO.add_value('faturas', faturas)

        # recaptcha_params = {
        #     'pageurl': 'http://iptu2019.pmf.sc.gov.br/iptu-virtual/main-iptu/index-segunda-via.php',
        #     'googlekey': '6LfatIkUAAAAABA1IFcpmL9KkJbFCDsSPZGeaplW',
        #     # 'type': 2,
        # }
        # json_Captcha = json.dumps(recaptcha_params)
        # client = SocketClient('projetabrasilsi@gmail.com', 'P2a3u0l9')
        # balance = client.get_balance()
        # self.logger.info("Remaining Balance: " + str(balance))
        # captcha = client.decode(type=4,token_params=json_Captcha)
        # self.logger.info(captcha["text"])

        balance = self.ita.account_balance()
        self.logger.info('Balance: {}'.format(balance))
        recaptcha_params = {
            'page_url': 'http://iptu2019.pmf.sc.gov.br/iptu-virtual/main-iptu/index-segunda-via.php',
            'sitekey': '6LfatIkUAAAAABA1IFcpmL9KkJbFCDsSPZGeaplW',
            'type': 2,
        }
        captcha_id = self.ita.submit_recaptcha(recaptcha_params)
        while self.ita.in_progress():
            time.sleep(5)
        captcha = self.ita.retrieve_recaptcha(captcha_id)
        formdata = {
            'data': '',
            'controle': 'ADMIN',
            'g-recaptcha-response': captcha,
            'nu_dam[]': []
        }
        for numero in nDams:
            formdata['nu_dam[]'].append(numero)

        yield scrapy.FormRequest(method='POST', formdata=formdata, callback=self.download, errback=self.error,
                                 url='http://iptu2019.pmf.sc.gov.br/iptu-virtual/main-iptu/segunda_via_internet.pdf.php',
                                 cb_kwargs={'imovel': imovel})

    def download(self, response, imovel):
        path = self.file_name + \
            imovel['codImovel'].replace('.', '') + '_' + imovel['inscricao']
        path += '.pdf'
        self.logger.info('Salvando PDF em ' + path)
        Utils.create_file(self.file_name)

        with open(path, 'wb') as f:
            f.write(response.body)
        pages = ''
        with open(path, 'rb')as f:
            pages = slate.PDF(f)
        pageOne = str(pages[0])
        floripaVO = ItemLoader(FloripaVO(), response)
        floripaVO.add_value('codImovel', imovel['codImovel'])
        floripaVO.add_value('inscricao', imovel['inscricao'])
        floripaVO.add_value('status', 'Com Débito')
        floripaVO.add_value('nome', Utils.find(
            'Pagador:\\s(.+?)\\n', pageOne, 1))
        floripaVO.add_value('endereco', Utils.find(
            'Imovel\\n(.+?)\\n', pageOne, 1))
        floripaVO.add_value('cpfCnpj', Utils.find(
            'CPF/CNPJ:\\s(.+?)\\n', pageOne, 1))
        for page in pages:
            faturas = {}
            text = str(page)
            valor = Utils.find(
                'Valor\\sdo\\sDocumento\\n\\n\\s{1,}(.+?)\\n', text, 1)
            faturas['parcela'] = Utils.find(
                'Valor\\n\\n(.+?)\\n\\nRG', text, 1)
            faturas['vencimento'] = Utils.find(
                '\n\nVencimento\n\n(.+?)\n\n', text, 1)
            faturas['codBarras'] = Utils.find(
                '\\d{5}\\.\\d{5}\\s{1,}\\d{5}\\.\\d{6}\\s{1,}\\d{5}\\.\\d{6}\\s{1,}\\d{1}\\s{1,}\\d{14}', text, 0)
            # tributo = '\\n'.join(find_all('(^(TAXA|IMPOSTO)\\s(.+?)$)', text, 1,''))
            faturas['tributos'] = Utils.find_all(
                '(^(TAXA|IMPOSTO)\\s(.+?)$)', text, 1, re.M)
            faturas['numeroDocumento'] = Utils.find(
                '\\d{2}\\/\\d{2}\\/\\d{4}\\n\\n(.+?)\\n\\nDV', text, 1)
            faturas['nossoNumero'] = Utils.find(
                'Nosso\\sNúmero\\n\\n(.+?)\\n\\n', text, 1)
            faturas['codBeneficiario'] = Utils.find(
                'beneficiário\\n\\n(.+?)\\n\\n', text, 1)
            faturas['numeroDam'] = Utils.find(
                'Número do DAM:\\s(.+?)\\n', text, 1)
            floripaVO.add_value('faturas', faturas)
        floripaVO.add_value('pdfs', path)
        yield floripaVO.load_item()

    def error(self, response, imovel):
        self.logger.error(response)
        floripaVO = ItemLoader(FloripaVO(), response)
        floripaVO.add_value('codImovel', imovel['codImovel'])
        floripaVO.add_value('inscricao', imovel['inscricao'])
        floripaVO.add_value('status', 'Reprocessar')
        
        yield floripaVO.load_item()
