#Automatic 'import pieces' by BPA Deploy - Nose Testing
import pieces

#!/usr/bin/env python
# coding: utf-8

# <h1>Processo RegistroFretePlanilhaOnline</h1>
# 

# <h1>emailfinalizado</h1>
# 
# O processo RegistroFretePlanilhaOnline utiliza do Notepad.<br>
# A abertura da aplicação será feita somente no emailfinalizado, logo a função está declarada neste mesmo pedaço de código.<br>
# Entretanto, a "função de escrever no Notepad" é compartilhada com outros StepNames, por este motivo ela está localizada no lib_processo.ipynb<br><br>
# 
# <h3>Passos emailfinalizado</h3><br>
# • Abrir Notepad;<br>
# • Escrever uma credencial obtida do BPASafe no Notepad.<br>

# In[1]:


from core import *

def emailfinalizado():
    print("\n\n[Step]--> emailfinalizado")

    
    return
     


# <h1>emailfinalizado_Sure</h1>
# 
# Com o Notepad aberto, tentaremos escrever algo para verificar se realmente ele está aberto & responsivo.<br>
# <font color='red'>Atenção:</font> O texto digitado deverá apagado logo após, deixando o Notepad limpo para o processo.<br><br>
# 
# <h4>Passos emailfinalizado_Sure</h4><br>
# • Apagar o conteudo do Notepad.<br>

# In[2]:


def emailfinalizado_sure():
    print("\n\n[Step]--> emailfinalizado_Sure")
    

    
    return


# <h1>Funçoes emailfinalizado</h1>
# 
# Contem a funcão de abrir o notepad.
# 
# 

# In[3]:


from core import *

def envia_email(all_text_row):
    """
    Função enviar_email:
    
    Entradas:
        arquivo                         # Nome do arquivo em pdf
        
    Retornos:
        receiver_email                  # Email Enviados
    """
    
    pieces.lib.ultradebug("\n\n[Step]--> [ enviar_email ]")
    pieces.lib.filelog("[ enviar_email ]")

    #codigo_cte = all_text_row[3]
    
    sender_email = "bots_inbox@bpatechnologies.com"
    password = 'bpa@1234'
    
#     body = "Caso {} cadastrado".format(codigo_cte)
    body = "TESTE"
    #receiver_email = "melody@bpatechnologies.com"
    receiver_email = "fellipe.pereira@bpatechnologies.com"
    
#     subject = "Caso {}".format(codigo_cte)
    subject = "TESTE"

    # Create a multipart message and set headers
    message = pieces.MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Add body to email
    message.attach(pieces.MIMEText(body, "plain"))
    text = message.as_string()

    # Log in to server using secure context and send email
    context = pieces.ssl.create_default_context()
    with pieces.smtplib.SMTP_SSL("smtp.gmail.com", "465", context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)
    return receiver_email


# <h1>Testes e Homologação</h1>
# <br>
# <p>Para fins de desenvolvimento interativo, é possível simular a estrutura do framework (modo Training) e rodar o código do StepName diretamente no Jupyter:</p>

# In[4]:


from core import *

if isdebug(__name__): # somente rodar o codigo no Jupyter
    #emailfinalizado()
    #emailfinalizado_sure()
    #print(abrir_notepad('prd'))
    emailfinalizado()
#     envia_email("MeuTeste")


# <h1>Unit Tests</h1>
# <br>
# <p>Cada função que realiza um trabalho significativo deverá ter seu respectivo teste unitário.
# 
# Em contradição ao jeito que programavamos em .ahk, o "sentido do desenvolvimento de código" agora deverá respeitar a metodologia de TDD (test driven development) - Primeiramente desenha-se  as funções de teste unitário e <b>somente então</b> inicia-se a codificação em si, com o o objetivo de satisfazer os testes unitários.</p>

# In[5]:


from core import *


    
# permitir os testes de serem rodados somente via Jupyter
if isDebug(__name__):
#     test_abrir_notepad()
#     test_escrever_notepad()
#     test_apagar_notepad()
    pass

    
    


# In[ ]:





# In[ ]:




