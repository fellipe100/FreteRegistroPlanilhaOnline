#Automatic 'import pieces' by BPA Deploy - Nose Testing
import pieces

#!/usr/bin/env python
# coding: utf-8

# <h1>Processo Registro de Frete Planilha Online</h1>
# 

# <h2>Escopo do Projeto</h2>
# 
# <ol type="1">
# 
#   
#   O processo consiste em 4 etapas, sendo elas:<br>
#   <ol>
#     <li>Consulta à planilha WebSheets</li>
#     <li>Geração de Dacte e MIRO</li>
#     <li>Atualização da planilha WebSheets</li>
#     <li>Envio de e-mail para informar conclusão do processo</li>
#   </ol>
#   
#   <u>prepara_ambiente.ipynb</u>
#   <li>Robô acessa sistema SAP e faz login na transação ZLES010T</li>
#  
#   <u>pesquisaitem.ipynb</u>
#   <li>É feito o acesso à planilha WebSheet e coletado os pedidos na aba Pendentes</li>
#   
#   <u>entradacte.ipynb</u>
#   <li>Cada pedido coletado da planilha WebSheets, que esteja com status Aprovado para processamento, é pesquisado no sistema SAP e a opção Gerar DACTE é selecionada<br>
#   Após a geração da DACTE, o código MIRO é informado pelo sistema SAP e a planilha WebSheet é atualizada, removendo o pedido da aba Pendentes e incluindo na aba Concluidos, incluindo o codigo MIRO gerado pelo sistema.</li>
#   
#   <u>emailfinalizado.ipynb</u>
#   <li>Envio de e-mail para caixa departamental informando o registro das DACTEs em caráter de malote, endereçado ao colaborador que aprovou o processamento na planilha WebSheets.</li>
# </ol>

# <h1>PreparaAmbiente</h1>
# 
# No PreparaAmbiente iremos apenas abrir e efetuar login no SAP<br><br>
# 
# <h3>Passos PreparaAmbiente</h3><br>
# • Abrir SAP<br>
# • Efetuar Login no sistema<br>
# • Acessar a transação ZLES010T<br>

# In[3]:


from core import *

def prepara_ambiente():
    print("\n\n[Step]--> preparaAmbiente - INICIO")
    
    pieces.lib.close_process("saplogon.exe")
    
    
    '''
      Lógica do excel aqui
    '''
    pieces.lib.filelog("entrando na funcao verificado_Dados_Excel")
    verificado_Dados_Excel()
    pieces.lib.filelog("saindo da funcao verificado_Dados_Excel")
    
    
    
    open_sap_logon("C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe")
#     session = login_sap("usr_robos","Bpa@1234*","SAP - QA")

#     session = login_sap("USR_ROBOS4","#d6r$M?iE!$#","SAP PRD")
    session = login_sap("USR_MACRO1","Mac1234;","SAP PRD")
    
    try:
        pieces.lib.filelog("checando se já possui sessão aberta")
        session.findById("wnd[1]").close()
        pieces.lib.filelog("Já possui sessão aberta, finalizando todas as sessões")
        session, application = pieces.lib_processo.get_running_sap_session()
        enter_transaction_sap(session, "ex", check_field_id=None)
        pieces.lib.set_default_key("finalizadosemsucesso")

    except:
        pieces.lib.filelog("Efetuando login na transação")
        enter_transaction_sap(session,"/nZLES010T")
     
    print("\n\n[Step]--> preparaAmbiente - FINAL")
    return

def open_sap_logon(path_sap, *, timeout=60):
    """
    Inputs
        path_sap             # str Absulte path to SAP application (local or network)
    Outputs
        pywinauto obj        # Success: SAP pywinauto at login screen
        -1                   # Error: Timeout while waiting for app window
        -2                   # Error: Invalid path or app not found in the specified folder
        -3                   # Error: Invalid path (not str)
    """
    
    pieces.lib.filelog("[[ open_sap_logon ]]")

    # validate inputs
    if not isinstance(path_sap, str):
        return -3
    if not pieces.lib.os.path.exists(path_sap):
        return -2
    
    timer = pieces.lib.Timer(timeout)
    while timer.not_expired:
        
        # Verifying whether a SAP logon window already exists
        try:
            sap_app = pieces.pywinauto.application.Application(backend='uia').connect(title_re='.*SAP Logon.*')
            sap_app_top_window = sap_app.top_window()
            return sap_app_top_window
        except pieces.pywinauto.application.findwindows.ElementNotFoundError:
            pass
    
        # Otherwise, open a new application
        pieces.lib.filelog("SAP Logon not found. Starting it.")
        try:
            pieces.subprocess.Popen(path_sap, shell=True)
            sap_app = pieces.pywinauto.Desktop(backend="uia").window(title_re='.*SAP Logon.*')
            sap_app.wait(wait_for='exists', timeout=timeout)
        except pieces.pywinauto.application.AppStartError:
            pieces.lib.ultradebug("open_sap_logon(): The specified path no longer exists or app couldn't be launched. Path -> " + str(path_sap))
            return -2
        except pieces.pywinauto.timings.TimeoutError:
            # Ignore it, let the class Timer handle the timeout (return -1)
            pass
            
    return -1

def login_sap(username, password, env, *, timeout=60):
    """
    Inputs
        username        # str SAP Username
        password        # str SAP Password
        env             # str SAP Connection enviroment ["SAP - QA", "SAP PRD"]
        
    Outputs
        SAP obj         # Success: SAP COM Object
        -10             # Error: Timeout ao tentar preencher o login
        -11             # Error: Timeout ao carregar a próxima tela (tela inicial SAP)
        -2              # Error: Invalid env variable. Not "str"
        -3              # Error: Invalid env variable. Should be "SAP - QA" or "SAPPRD - 01" (case-insensitive)
        -4              # Error: SAP Enviroment is offline, unreachable or unavailable
    """
    
    # Input validation
    if not isinstance(username, str):
        pieces.lib.iamlost("login_sap(): Invalid username >> " + str(username))
    if not isinstance(password, str):
        pieces.lib.iamlost("login_sap(): Invalid password >> " + str(password))
    
    try:
        env = env.upper()
    except:
        return -2
    if env not in ["SAP - QA", "SAP PRD"]:
        pieces.lib.filelog("Attention!\n\nlogin_sap() 'env' is invalid >> {}\n\nIt wont fix itself!".format(env))
        return -3
    
    timer = pieces.lib.Timer(timeout)
    while timer.not_expired:
        SapGuiAuto = pieces.win32com.client.GetObject('SAPGUI')
        if not type(SapGuiAuto) == pieces.win32com.client.CDispatch:
            return -5

        application = SapGuiAuto.GetScriptingEngine
        
        if not type(application) == pieces.win32com.client.CDispatch:
            SapGuiAuto = None
            return -6
        
        try:
            connection = application.OpenConnection(env, True)
        except win32com.client.dynamic.pythoncom.com_error as e:
            ## SAP env is offline / unavailable
            if "-2147352567" in str(e):
                return -6
            else:
                return -7
            
        if not type(connection) == pieces.win32com.client.CDispatch:
            application = None
            SapGuiAuto = None
            return -8

        session = connection.Children(0)
        if not type(session) == pieces.win32com.client.CDispatch:
            connection = None
            application = None
            SapGuiAuto = None
            return -9

        MAIN_SAP_WINDOW = "wnd[0]"
        session.findById(MAIN_SAP_WINDOW).maximize
        
        ID_FIELD_USERNAME = "wnd[0]/usr/txtRSYST-BNAME"
        ID_FIELD_PASSWORD = "wnd[0]/usr/pwdRSYST-BCODE"
        ID_FIELD_LANGUAGE = "wnd[0]/usr/txtRSYST-LANGU"
        
        # Enter credentials
        session.findById(ID_FIELD_USERNAME).text = username
        session.findById(ID_FIELD_PASSWORD).text = password
        session.findById(ID_FIELD_LANGUAGE).text = "PT"
        
        # Enter
        session.findById("wnd[0]").sendVKey(0)
        
        # try to enter any text @ transaction edit field, if it works, we are online
        ID_FIELD_TRANSACTION = "wnd[0]/tbar[0]/okcd"
        text = session.findById(ID_FIELD_TRANSACTION).text = "CHECK"
        session.findById(ID_FIELD_TRANSACTION).text = ""
        if text == "CHECK":
            return session

    return -10




def enter_transaction_sap(session, transaction_code, *, check_field_id=None):
    """
    Inputs
        session               # SAPGUI COM Object
        transaction_code      # SAP transaction
        check_field_id        # verify id

    Outputs
        -10             # Error: Timeout ao tentar preencher o login
        -11             # Error: Timeout ao carregar a próxima tela (tela inicial SAP)
        -2              # Error: Invalid 'transaction_code'. Not "str"
        -3              # Error: Invalid 'check_field_id'. Not "str" and not None
        -4              # Error: Invalid 'check_field_id'. Does not contain a valid ID
    """

    pieces.lib.filelog("[[ enter_transaction ]]")
    # Validate Input
    if not isinstance(transaction_code, str):
        return -2
    if check_field_id is not None:
        if not isinstance(check_field_id, str):
            return -3
        if not "wnd[0]/usr" in check_field_id:
            return -4
    
    # If the transaction does not start with \n, attach it
    # \n makes any transaction reachable from within other transaction
    # By doing it so, we dont need SAP to be on its initial screen
    transaction_code = transaction_code.strip()
    if not transaction_code.startswith("/n"):
        transaction_code = "/n" + transaction_code
    
    session.findById("wnd[0]/tbar[0]/okcd").text = transaction_code
    session.findById("wnd[0]").sendVKey(0)
    
    # check if check_field_exists (ie: could access transaction)
    if check_field_id is not None:
        session.findById(check_field_id).text = "aa"
        session.findById(check_field_id).text = ""
    pieces.lib.filelog("[[ enter_transaction = ".format(transaction_code).format("]]"))
    return 1


# In[4]:


# Verificador de registro da planilha do excel 
def verificado_Dados_Excel():    
    # value --- Texto para procurar na celula
    
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = pieces.ServiceAccountCredentials.from_json_keyfile_name("API-leao-RegistroDeFrete-e68a2d5382c4.json", scope)  
    client = pieces.gspread.authorize(creds)
    
    sheet = client.open("Casos-Dacte").sheet1
    
    validador = True
    
    while(validador):
        pieces.lib.time.sleep(10)
        valor = sheet.cell(2 , 1).value
        pieces.lib.time.sleep(10)
        if(valor != ""):
            validador = False
        print("Planilha esta vazia")
       
    pieces.lib.filelog("Saindo da funcao e indo processar no sap")
    return 


# In[ ]:





# <h1>PreparaAmbiente_Sure</h1>
# 
# Sem necessidade, este modulo se manterá apenas para geração de log. <br>
# 
# <h4>Passos PreparaAmbiente_Sure</h4><br>
# • Geração de Log<br>

# In[5]:


def prepara_ambiente_sure():
    print("\n\n[Step]--> preparaAmbiente_Sure - INICIO")
    print("\n\n[Step]--> preparaAmbiente_Sure - FINAL")
    return


# <h1>Funçoes PreparaAmbiente</h1>
# 
# Contém algumas funções de manuseio do SAP (iniciar app e login)
# 
# <h2>Funcoes SAP</h2>
# <h3>func: open_sap_logon()</h3>
# <p style="text-indent :5em;" > Procura por um SAP Logon já existente, se não localizar, inicia um novo.<br></p>
# 
# <img src="images_doc/sap_logon.png" width=320 heigth=200>
# <br>

# <h1>Testes e Homologação</h1>
# <br>
# <p>Para fins de desenvolvimento interativo, é possível simular a estrutura do framework (modo Training) e rodar o código do StepName diretamente no Jupyter:</p>

# In[6]:


from core import *

if isdebug(__name__): # somente rodar o codigo no Jupyter
    prepara_ambiente()
    prepara_ambiente_sure()


# <h1>Unit Tests</h1>
# <br>
# <p>Cada função que realiza um trabalho significativo deverá ter seu respectivo teste unitário.
# 
# Em contradição ao jeito que programavamos em .ahk, o "sentido do desenvolvimento de código" agora deverá respeitar a metodologia de TDD (test driven development) - Primeiramente desenha-se  as funções de teste unitário e <b>somente então</b> inicia-se a codificação em si, com o o objetivo de satisfazer os testes unitários.</p>

# In[17]:


from core import *

def test_open_sap_logon():
    """
    Function is expected to return a valid pywinauto window specification for SAP Logon.
    Additional testings for timeout and invalid paths.
    """
    test_cases = [
        # Timeout
        {
            "test_case_name" : "Timeout",
            
            "path_sap" : pieces.gvars.path_sap,
            "timeout" : -0.01, ## timer starts already expired
            "expected_result" : -1
        },
     
        # False SAP Path (pointing to C:\saplogon.exe)
        {
            "test_case_name" : "False SAP path",
            
            "path_sap" : r"C:\saplogon.exe",
            "expected_result" : -2
        },
        
        # Invalid SAP Path
        {
            "test_case_name" : "Invalid SAP path",
            
            "path_sap" : [-1],
            "expected_result" : -3
        },

        # Everything OK. Title is expected
        {
            "test_case_name" : "Everything OK",
            
            "path_sap" : pieces.gvars.path_sap,
#             "expected_result" : "SAP Logon 730" ## Title
            "expected_result" : ""

        }
    ]
    
    results = []
    expected_results = []
    for case in test_cases:
        pieces.lib.filelog("Testing for... {}".format(case["test_case_name"]))
        path_sap = case["path_sap"]
        timeout = case.get("timeout", None) or 60
        this_result = open_sap_logon(path_sap=path_sap, timeout=timeout)
        
        # If expected correct result, return the title instead otherwise we cant compare
        if not isinstance(this_result, int):
            this_result = this_result.texts()[0]
        
        results.append(this_result)
        expected_results.append(case["expected_result"])

    
    print("Unit Testing open_sap_logon():\n\t"           "Results: " + str(results) +           "\n\tExpected Results: " + str(expected_results))
    
    assert results == expected_results
    print("open_sap_logon: Success!\n\n") 
#-------------------------------------------------------------------------------------------------------------------------------
def test_login_sap():
    """
    Function to test SAP login functionality
    """
    
    env = pieces.gvars.enviroment
    if not env in ['hmg', 'prd']:
        pieces.lib.filelog("Unit Test test_login_sap(): Invalid pieces.lib.enviroment. Expected 'prd' or 'hmg' >> ".format(env))
    sap_username = "usr_robos"
    sap_password = "Bpa@1234*"

    
    test_cases = [
        {
            "test_case_name" : "Correct login",
            
            "sap_username": "usr_robos",
            "sap_password": "Bpa@1234*",
            "sap_env": "SAP - QA",
            "expected_result" : "QA0"
        },
    ]
    
    results = []
    expected_results = []
    for case in test_cases:
        pieces.lib.filelog("Testing for... {}".format(case["test_case_name"]))
        sap_username = case["sap_username"]
        sap_password = case["sap_password"]
        sap_env = case["sap_env"]
        timeout = case.get("timeout", None) or 60
        this_result = login_sap(sap_username, sap_password, sap_env)

        # If expected correct result, return the sap enviroment it is currently on (ex: "QA0")
        if not isinstance(this_result, int):
            this_result = this_result.Info.SystemName
        
        results.append(this_result)
        expected_results.append(case["expected_result"])

    
    print("Unit Testing test_login_sap():\n\t"           "Results: " + str(results) +           "\n\tExpected Results: " + str(expected_results))
    
    assert results == expected_results
    print("open_sap_logon: Success!\n\n") 
    return
#-------------------------------------------------------------------------------------------------------------------------------
def test_enter_transaction_sap():
    """
    Function to test capability of navigating through different transactions
    """
    
    test_cases = [
        {
            "test_case_name" : "Correct transaction",

            "transaction_code": "/nZLES010T",
            "check_field_id": "wnd[0]/tbar[0]/okcd", # ID_FIELD_CUSTOMER_ACCOUNT
            "expected_result" : -4
        },
#         {
#             "test_case_name" : "No authorization",

#             "transaction_code": "me2m",
#             "check_field_id": None,
#             "expected_result" : -6, # User does not have authorization to use the transaction
#         },
#         {
#             "test_case_name" : "Non existent transaction",
            
#             "transaction_code": "4412312fw",
#             "expected_result" : -7, # Transaction does not exist
#         },
    ]
    
    results = []
    expected_results = []
    sap_session, sap_application = pieces.lib_processo.get_running_sap_session()
    for case in test_cases:
        pieces.lib.filelog("Testing for... {}".format(case["test_case_name"]))
        transaction_code = case["transaction_code"]
        check_field_id = case.get("check_field_id", None)
        
        
        this_result = enter_transaction_sap(sap_session,
                                            transaction_code=transaction_code,
                                            check_field_id=check_field_id)

        results.append(this_result)
        expected_results.append(case["expected_result"])

    
    print("Unit Testing enter_transaction_sap():\n\t"           "Results: " + str(results) +           "\n\tExpected Results: " + str(expected_results))
    
    assert results == expected_results
    print("enter_transaction_sap: Success!\n\n")
    return

# permitir os testes de serem rodados somente via Jupyter
if isDebug(__name__):
    test_open_sap_logon()
    test_login_sap()
    test_enter_transaction_sap()


# In[ ]:





# In[ ]:





# In[ ]:




