import textract
import PyPDF2
import re
# import pdftotree
import pdfkit
import slate3k as slate


def test():
    fileName = '/home/files/FLORIPA_IPTU/30_01_20/53a01e92-43ae-11ea-81bc-6432a854670d/00912001_45820590745085161.pdf'
    pages = ''
    with open(fileName, 'rb')as f:
        pages = slate.PDF(f)
    # text = textract.process(fileName)
    # text = textract.process(fileName,encoding='ascii')
    # text = pdftotree.parse(fileName, html_path=None, model_type=None, model_path=None, favor_figures=True, visualize=False)

    # pdfFileObject = open(fileName, 'rb')
    # pdfReader = PyPDF2.PdfFileReader(pdfFileObject)
    # count = pdfReader.numPages
    faturas = []
    for page in pages:
        # print(page)
        text = str(page)
        valor = find(
            'Valor\\sdo\\sDocumento\\n\\n\\s{1,}(.+?)\\n', text, 1)
        nome = find('Pagador:\\s(.+?)\\n', text, 1)
        endereco = find('Imovel\\n(.+?)\\n', text, 1)
        cpfCnpj = find('CPF/CNPJ:\\s(.+?)\\n', text, 1)
        parcela = find('Valor\\n\\n(.+?)\\n\\nRG', text, 1)
        vencimento = find('\n\nVencimento\n\n(.+?)\n\n', text, 1)
        codBarras = find(
            '\\d{5}\\.\\d{5}\\s{1,}\\d{5}\\.\\d{6}\\s{1,}\\d{5}\\.\\d{6}\\s{1,}\\d{1}\\s{1,}\\d{14}', text, 0)
        # tributo = '\\n'.join(find_all('(^(TAXA|IMPOSTO)\\s(.+?)$)', text, 1,''))
        tributo = find_all('(^(TAXA|IMPOSTO)\\s(.+?)$)', text, 1, re.M)
        print(tributo)
        numeroDocumento = find(
            '\\d{2}\\/\\d{2}\\/\\d{4}\\n\\n(.+?)\\n\\nDV', text, 1)
        nossoNumero = find('Nosso\\sNúmero\\n\\n(.+?)\\n\\n', text, 1)
        codBeneficiario = find('beneficiário\\n\\n(.+?)\\n\\n', text, 1)
        numeroDam = find('Número do DAM:\\s(.+?)\\n', text, 1)
        faturas.append(dict(valor=valor, nome=nome, endereco=endereco, cpfCnpj=cpfCnpj, parcela=parcela, vencimento=vencimento, codBarras=codBarras,
                            tributo=tributo, numeroDocumento=numeroDocumento, nossoNumero=nossoNumero, codBeneficiario=codBeneficiario, numeroDam=numeroDam))
    # print(faturas)


def find(regex, text, group, flag=0):
    search = re.search(regex, text, flag)
    try:
        return search.group(group)
    except Exception as e:
        return e


def find_all(regex, text, group, flag=0):
    matchs = []
    try:
        # return re.findall(regex, text, flag).group(group)
        for match in re.finditer(regex, text, flag):
            matchs.append(match.group(group))
        if not matchs: raise Exception('REGEX NOT MATCH')
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


if __name__ == '__main__':
    print(test())
