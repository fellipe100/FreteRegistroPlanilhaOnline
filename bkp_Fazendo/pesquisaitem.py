#!/usr/bin/env python
# coding: utf-8

# <h1>Processo Registro de Frete Planilha Online</h1>
# 

# <h1>pesquisaItem</h1>
# 
# Este processo acessa a planilha fornecida na plataforma WebSheets, verificando se há pedidos aprovados para geração de DACTE.<br><br>
# 
# <h3>Passos pesquisaItem</h3><br>
# • Acessa planilha WebSheets<br>
# • Coleta de pedidos a serem processados pelo robô<br>

# In[1]:


from core import *

def pesquisaitem():
    print("\n\n[Step]--> pesquisaitem - INICIO")
    
#     collect_all_spreedshet_data()
    
    print("\n\n[Step]--> pesquisaitem - FINAL")
    
    return


# <h1>pesquisaItem_Sure</h1>
# 
# Sem necessidade para esse módulo, será mantido apenas para geração de logs.
# 
# <h4>Passos pesquisaitem_Sure</h4><br>
# • Geração de Log.<br>

# In[2]:


def pesquisaitem_Sure():
    print("\n\n[Step]--> pesquisaitem_Sure - INICIO")
    print("\n\n[Step]--> pesquisaitem_Sure - FINAL")
    
    return


# <h1>Funçoes pesquisaItem</h1>
# 
# Contem a funcão openWebSheet, utilizada para realizar a comunicação com a API da plataforma WebSheets
# 
# <h3>func: openWebSheets(str=authFile, str=worksheet, srt=activeSheet='')</h3>
# <p style="text-indent :5em;" > A função recebe o caminho do arquivo com a chave para acesso à API, o nome da planilha a ser acessada e, opcionalmente, o nome da aba que deverá ser acessada. Se o nome da aba não for fornecido, será utilizada a aba padrão da planilha.<br>
# <br>Essa função retorna a Sessão aberta com a API</p>
# 
# <!-- <img src="images_doc/notepad_aberto.png" width=640 heigth=400> -->
# <br>

# In[3]:


def openWebSheet(authFile, worksheet, activeSheet=''):

    # authFile                 =    name of authentication file provided by Google API Service
    # worksheet                =    name of the websheet
    # activeSheet (optional)   =    title of the sheet to be activated and returned. If empty, returns default sheet  
    
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(authFile, scope)
    client = gspread.authorize(creds)
    
    # Opens the conection
    ws = client.open(worksheet)
    
    # Checks if the sheet title was passed to the function
    if activeSheet != '':
        return ws.worksheet(activeSheet)      
    
    #Returns the worksheet on the default sheet
    return ws.sheet1 


# <h1>Testes e Homologação</h1>
# <br>
# <p>Para fins de desenvolvimento interativo, é possível simular a estrutura do framework (modo Training) e rodar o código do StepName diretamente no Jupyter:</p>

# In[4]:


from core import *

if isDebug(__name__): # somente rodar o codigo no Jupyter
    #pesquisaitem()
    #pesquisaitem_sure()
    #print(abrir_notepad('prd'))
    pesquisaitem()


# <h1>Unit Tests</h1>
# <br>
# <p>Cada função que realiza um trabalho significativo deverá ter seu respectivo teste unitário.
# 
# Em contradição ao jeito que programavamos em .ahk, o "sentido do desenvolvimento de código" agora deverá respeitar a metodologia de TDD (test driven development) - Primeiramente desenha-se  as funções de teste unitário e <b>somente então</b> inicia-se a codificação em si, com o o objetivo de satisfazer os testes unitários.</p>

# In[5]:


from core import *
# import gspread 
# from oauth2client.service_account import ServiceAccountCredentials

def test_collect_all_spreedshet_data():
    test_cases = [{"test_name": "planilha_populada",
                   "expected_result": "POPULATED"}
#                   {"test_name": "planilha_vazia",
#                    "expected_result": "EMPTY"},
                 ]
    results = []
    expected_results = []
    
    for test_case in test_cases:
        all_data = collect_all_spreedshet_data()
    
        if len(all_data) > 0:
            results.append("POPULATED")
        else:
            results.append("EMPTY")
        
        
        expected_results.append(test_case["expected_result"])  

    print("unity test: {}".format(collect_all_spreedshet_data.__name__))
    print("results {}".format(results))
    print("expected_results {}".format(expected_results))

    assert results == expected_results

    print("Teste bem sucedido")
    return


# permitir os testes de serem rodados somente via Jupyter
if isDebug(__name__):
    test_collect_all_spreedshet_data()
    pass  
    


# In[ ]:




