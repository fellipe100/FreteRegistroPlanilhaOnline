#!/usr/bin/env python
# coding: utf-8

# <h1>Processo RegistroFrete</h1>
# 

# <h1>finalizadocomsucesso</h1>
# 
# Nessa etapa ocorre o fechamento da sessão do SAP
# 
# <h3>Passos finalizadocomsucesso</h3><br>
# • Acessar Sessão<br>
# • Fechar sessão<br>

# In[1]:


from core import *

def finalizadocomsucesso():
    print("\n\n[Step]--> finalizadocomsucesso - INICIO")
    try:
        session, application = pieces.lib_processo.get_running_sap_session()
        enter_transaction_sap(session, "ex", check_field_id=None)
    except:
        pieces.lib.iamlost("Erro ao acessar SAP - finlizadocomsucesso")
    
    print("\n\n[Step]--> finalizadocomsucesso - FINAL")
    
    return


# <h1>finalizadocomsucesso_Sure</h1>
# 
# Sem necessidade, será mantido apenas para geração de logs.
# 
# <h4>Passos finalizadocomsucesso_Sure</h4><br>
# • Geração de Logs<br>

# In[2]:


def finalizadocomsucesso_sure():
    print("\n\n[Step]--> finalizadocomsucesso_Sure - INICIO")
    print("\n\n[Step]--> finalizadocomsucesso_Sure - FINAL")    
    
    
    return


# <h1>Funçoes finalizadocomsucesso</h1>
# 
# Função para fechar a sessão
# 

# In[3]:


from core import *

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


# <h1>Testes e Homologação</h1>
# <br>
# <p>Para fins de desenvolvimento interativo, é possível simular a estrutura do framework (modo Training) e rodar o código do StepName diretamente no Jupyter:</p>

# In[4]:


from core import *

if isDebug(__name__): # somente rodar o codigo no Jupyter
    #finalizadocomsucesso()
    #finalizadocomsucesso_sure()
    
    finalizadocomsucesso()


# <h1>Unit Tests</h1>
# <br>
# <p>Cada função que realiza um trabalho significativo deverá ter seu respectivo teste unitário.
# 
# Em contradição ao jeito que programavamos em .ahk, o "sentido do desenvolvimento de código" agora deverá respeitar a metodologia de TDD (test driven development) - Primeiramente desenha-se  as funções de teste unitário e <b>somente então</b> inicia-se a codificação em si, com o o objetivo de satisfazer os testes unitários.</p>

# In[5]:



    
# permitir os testes de serem rodados somente via Jupyter
if isDebug(__name__):
    pass

    
    


# In[ ]:




