from os import getcwd as curPath
from time import sleep

# from numpy import resize
from selenium import webdriver

# from browser.utils import string2float

from platform import system as sistema_operacional

SEP_DIR = '\\'

class ChromeBrowser(webdriver.Chrome):

    def __init__(self, *args, **kwargs) -> webdriver.Chrome:
        """
            INPUT:
                chromeDriverPath (str): Path ate o chromedriver, Default: path atual
        """
        # Inicializa Browser com chromeDriverPath, default
        super(ChromeBrowser, self).__init__(*args,**kwargs)

        self.JQUERY_BUILD_LIST_FROM_ELEMENT = """let listaInfosSelenium = []; \\
            $("{jquery_element}").each(function(){{  \\
                listaInfosSelenium.push(this.{atributo});  \\
            }}); \\
            return listaInfosSelenium"""

    def insereTextoLento(self, xpath_texto: str, texto: str, delay_escrita: float =0.08, delay_retorno: float =2.5) -> None:
        """
        INPUT:
            self: webdriver.Chrome
            xpath_texto(str): xpath do local onde o texto sera inserido
            texto (str): Texto que deve ser inserido
            delay_escrita (float): tempo de espera (em segundos) entre digitar cada caracter, Default: 0.08
            delay_retorno (float): tempo de espera (em segundos) para retornar, apos digitar tds os caracteres, Default: 2.5
        """
        self.find_element_by_xpath(xpath_texto).clear()
        # Inserimos os caracteres com Delay, pq o site nao reconhece quando escrevemos muito rapido
        for char in texto:
            self.find_element_by_xpath(xpath_texto).send_keys(char)
            sleep(delay_escrita)
        sleep(delay_retorno)

    def constroiFuncaoNaPagina(self, nome: str, corpo_funcao: str, parametros_str: str ='') -> None:
        assert all([map(lambda parametro: type(parametro) is str, [nome, corpo_funcao, parametros_str])]), "ERRO: TODOS os parametros devem ser 'strings'!"

        BASE_FUNCAO = """
            var script = document.createElement('script');
            script.text = 'function {nome}({parametros_str}){{ \\
                {corpo_funcao} \\
                }}'; 
            document.getElementsByTagName('head')[0].appendChild(script);
        """
        # Adiciona metodo ao JS da pagina
        self.execute_script(BASE_FUNCAO.format(nome=nome, corpo_funcao=corpo_funcao, parametros_str=parametros_str))

    def existejQueryNaPagina(self) -> bool:
        VERSAO_JQUERY = \
            """try { \\
                return jQuery.fn.jquery \\
            } \\
            catch(err){ \\
                return "ERRO" \\
            }"""
        self.constroiFuncaoNaPagina(nome='get_jquery_selenium', corpo_funcao=VERSAO_JQUERY)

        SENTENCA_JQUERY = "return get_jquery_selenium()"

        jQuery = self.execute_script(SENTENCA_JQUERY)
        if jQuery ==  'ERRO':
            return False
        else: 
            return True

    def insereJqueryNaPagina(self) -> None:
        SENTENCA_JQUERY ="""
        var script = document.createElement('script');
        script.src = 'https://code.jquery.com/jquery-3.4.1.min.js';
        script.type = 'text/javascript';
        document.getElementsByTagName('head')[0].appendChild(script); 
        """
        self.execute_script(SENTENCA_JQUERY)
    
    def get_element_length_by_jquery(self, jquery_element: str) -> int:
        return self.execute_script("""return $("{elemento}").length """.format(elemento=jquery_element))

    def enviaComandoParaElemento(self, jquery_element: str, posicao: int ='', comando: str =''):
        if posicao:
            assert type(posicao) is int, """ERRO: type(posicao) deve ser 'INT', não '{tipo}'""".format(tipo=type(posicao))
            posicao = [posicao]
        
        if comando:
            assert type(comando) is str, """ERRO: type(comando) deve ser 'str', não '{comando}'""".format(tipo=type(comando))
            comando = '.' + comando
        
        return self.execute_script("""return $("{jquery_element}"){posicao}{comando}""".format(jquery_element=jquery_element, posicao=posicao, comando=comando))
    
    def get_url(self, url: str, add_jquery: bool = True) -> None:
        # Acessa url
        _return = self.get(url=url)

        # Adiciona o jQuery na pagina
        if add_jquery and not self.existejQueryNaPagina():
            self.insereJqueryNaPagina()

        return _return
    
    def obtem_headers_tabela(self, tabela_id: str) -> (list, int):
        """
            Objetivo: Obter Headers da tabela 

            OUTPUT:
                tuple (list, int)
                list -> nome das colunas
                int - > Numero de colunas
        """
        jquery_element = '#{tabela_id} > thead > tr:first > th'.format(tabela_id=tabela_id)

        # constroi funcao para obter o nome das headers
        self.constroiFuncaoNaPagina(
            'get_headers_info_selenium',
            self.JQUERY_BUILD_LIST_FROM_ELEMENT.format(
                jquery_element=jquery_element,
                atributo='innerText'
            )
        )
        #  Executa função, para obter a lista
        nome_colunas = [coluna.lower() for coluna in self.execute_script(""" return get_headers_info_selenium() """)]

        return nome_colunas, len(nome_colunas)
    
    def dados_tabela_2_dict(self, tabela_id: str) -> dict:
        
        # Obtem informacoes das headers
        list_table_headers, num_headers = self.obtem_headers_tabela(tabela_id=tabela_id)

        jquery_element = '#{tabela_id} > tbody > tr > td'.format(tabela_id=tabela_id)

        # constroi funcao para obter o texto de cada campo da tabela
        self.constroiFuncaoNaPagina(nome='get_table_body_info_selenium', corpo_funcao=self.JQUERY_BUILD_LIST_FROM_ELEMENT.format(jquery_element=jquery_element, atributo='innerText'))
        #  Executa função, para obter a lista
        list_texto_tabela = self.execute_script(""" return get_table_body_info_selenium() """)

        list_texto_tabela = list(map(lambda coluna: coluna.replace('.', '').replace(',', '.'), list_texto_tabela))
        
        # Temos um vetor 1 x num_headers*num_linhas -> Redimensionamos para: num_linhas x num_headers
        if not list_texto_tabela:
            return {nome_info: [] for nome_info in list_table_headers}
        elif len(list_texto_tabela) > num_headers:
            lista_ativos = resize(list_texto_tabela, (-1, num_headers))
        else:
            lista_ativos = resize(list_texto_tabela, (1, num_headers))

        dados = {nome_info: list(map(string2float, lista_ativos[:, index])) for index, nome_info in enumerate(list_table_headers)}

        return dados
