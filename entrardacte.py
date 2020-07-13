#Automatic 'import pieces' by BPA Deploy - Nose Testing
import pieces

#!/usr/bin/env python
# coding: utf-8

# <h1>Processo Registro de Frete Planilha Online</h1>
# 

# <h1>entrardacte</h1>
# 
# O processo EntrarDacte efetua a geração da DACTE e do código MIRO no sistema SAP e atualiza a planilha WebSheet.<br><br>
# 
# <h3>Passos entrardacte</h3><br>
# • Para cada pedido com processamento aprovado na lista colatada pelo robô na plataforma WebSheets, é feita a geração da DACTE no sistema SAP<br>
# • Coleta o código MIRO e atualiza a planilha para cada pedido processado<br>
# 

# In[1]:


from core import *

def entrardacte():
    print("\n\n[Step]--> entrardacte - INICIO")
    
    # Não precisa, Fellipe -> estou avaliando...
    session, application = pieces.lib_processo.get_running_sap_session()
    
    
    #VALOR A SER PESQUISADO NA PLANILHA 
    value = "OK"
    refactor_data_dacte(session,value)
    
    pieces.lib.set_default_key("finalizadocomsucesso")
    
    print("\n\n[Step]--> entrardacte - FINAL")
    return



# <h1>Função de Suporte</h1>
# 
# 
# <p> 
#     Recebe as informações da sessão SAP e o valor a ser pesquisado na planilha webSheets.<br>
#     Para cada linha encontrada na planilha com o texto "OK" na coluna Status, o robô efetua a geração da DACTE e criação da MIRO no SAP e atualiza a planilha da seguinte forma:<br>
#     <li>Caso tenha tido sucesso na criação da MIRO, o caso é transferido para a aba Concluidos da planilha e adicionado o numero MIRO na última coluna.</li>
#     <li>Caso tenha ocorrido falha na criação da MIRO, o caso é transferido para a aba Analise_manual da planilha e adicionada a mensagem de erro na última coluna.</li><br>
#     Após efetuar a transferencia do caso para a aba adequada, o robô segue para efetuar o envio do e-mail, da seguinte forma:
#     <li>Se a coluna de Usuario_responsavel do pedido estiver preenchida na planilha, os dados do pedido processado são guardados para envio no final desse modulo, conforme padrão em lote.</li>
#     <li>Se a coluna de Usuario_responsavel do pedido estiver vazia na planilha, os dados do pedido serão enviados individualmente logo após o processamento do caso.</li><br>
#     <b>A cada caso processado, uma nova consulta é feita na planilha</b>
# </p>

# In[2]:


def refactor_data_dacte(session, value):    
    # value --- Texto para procurar na celula
    
    email_lote = [] # Conteudo de lote do e-mail
    
    all_status_dacte = ""
    all_key_process_id = ""
    all_status_dacte_error = ""
    all_key_process_id_error = ""
    
    processing = True
    error_message = None
    
    KEY_ACESS_INDEX = 0
    CTE_INDEX = 3
    USER_INDEX = 25
    
    while (processing):
        
        try:
            pieces.lib.filelog("acessando websheet Pendentes")
            sheet = pieces.lib_processo.openWebSheet("API-leao-RegistroDeFrete-e68a2d5382c4.json","Casos-Dacte","Pendentes") 
#             #Apenas para testes
#             sheet = pieces.lib_processo.openWebSheet('mytest-273716-aaddc43030cc.json', 'meuTeste', 'Pendentes')
            pieces.lib.filelog("Pesquisando valor na planilha Pendentes")
            cell = cell_find(sheet,value)
            
            
            pieces.lib.filelog("linha encontrada")
            row = sheet.row_values(cell.row)
            print("Row:  ",row)
            pieces.lib.filelog("Registrando DACTE para: {}".format(row[KEY_ACESS_INDEX]))
            row[0] = str(row[KEY_ACESS_INDEX])
            
            number_miro = register_dacte(session,row[KEY_ACESS_INDEX])

            pieces.lib.filelog(number_miro)

            if (number_miro.find("Miro Gerada") == 0):
                process_status = "Sucesso"
                row[cell.col-1] = process_status
                row.append(number_miro)
                pieces.lib.filelog("Movendo para Concluidos")
                error_message = move_ok_spreadsheet(row)
                if (error_message is None):
                    sheet.delete_row(cell.row)
                else:
                    sheet.update_cell(cel.row,cel.col,process_status)
                #Populating info for Watch
                if (all_status_dacte == ""):
                    all_status_dacte = "Registrado com sucesso = {}".format(number_miro)
                else:
                    all_status_dacte = all_status_dacte + "|" + "Registrado com sucesso = {}".format(number_miro)

                if (all_key_process_id == ""):
                    all_key_process_id = str(row[CTE_INDEX])
                else:
                    all_key_process_id = all_key_process_id  + "|" + str(row[CTE_INDEX])

                #Prepara e-mail
                if (row[USER_INDEX] == ""):
                    pieces.lib.filelog("Enviando Email Individual")
                    envia_email(row)
                else:
                    pieces.lib.filelog("Preparando Email para Lote")
                    email_lote.append({"resp_user": row[USER_INDEX],
                                      "cte_number": row[CTE_INDEX],
                                      "status": "Miro Gerada com Sucesso"})

            else:
                process_status = "ERRO"
                print(row)
                #row[cell.col-1] = process_status
                #row.append(number_miro)
                #pieces.lib.filelog("Movendo para Analise Manual")
                #error_message = move_failed_spreadsheet(row)
                
                #Modificaçao analise robo
                try_count = 0
                row[26] = process_status
                try:
                    try_count = int(row[28])
                    row[27] = number_miro
                    row[28], try_count = try_count + 1
                except:
#                     print("primeira tentativa")
                    row.append(number_miro)
                    row.append(1)
                if try_count < 5:
                    error_message = move_retry_spreadsheet(row)
                    pieces.lib.filelog("Movendo para Analise Robo")
                else:
                    error_message = move_failed_spreadsheet(row)
                    pieces.lib.filelog("Movendo para Analise Manual")
                #Final modificaçao
                
                if (error_message is None):
                    sheet.delete_row(cell.row)
                else:
                    sheet.update_cell(cel.row,cel.col,process_status)
                #Populating info for Watch
                if (all_status_dacte_error == ""):
                    all_status_dacte_error = "Houve erro ao registrar = {}".format(number_miro)
                else:
                    all_status_dacte_error = all_status_dacte_error + "|" + "Houve erro ao registrar = {}".format(number_miro)

                if (all_key_process_id_error == ""):
                    all_key_process_id_error = str(row[CTE_INDEX])
                else:
                    all_key_process_id_error = all_key_process_id_error  + "|" + str(row[CTE_INDEX])

                #Prepara e-mail
                if (row[USER_INDEX] == ""):
                    pieces.lib.filelog("Enviando Email Individual")
                    envia_email(row)
                    pieces.lib.filelog("Email Individual Enviado")
                else:
                    pieces.lib.filelog("Preparando Email para Lote")
                    email_lote.append({"resp_user": row[USER_INDEX],
                                      "cte_number": row[CTE_INDEX],
                                      "status": "Houve erro ao registrar = {}".format(number_miro)})
                        
        except:
            pieces.lib.filelog("Finalizando planilha")
            processing = False
        
    pieces.lib.set_var_process("processo_chave_id", all_key_process_id)
    pieces.lib.set_var_process("status_dacte", all_status_dacte)
    pieces.lib.set_var_process("processo_chave_id_error", all_key_process_id_error)
    pieces.lib.set_var_process("status_dacte_error", all_status_dacte_error)
    
    #Envia e-mail em lote
    if len(email_lote) > 0:
        pieces.lib.filelog("Enviando e-mail em lote")
        envia_email_lote(email_lote)
        pieces.lib.filelog("E-mail em lote enviado")
    
    retry_manual_rows()

    return


# In[ ]:





# <h1>Funções de acesso ao Google Sheets</h1>
# 
# <h3>func: cell_find(sheet,str=value)</h3>
# 
# <p style="text-indent :5em;" >Recebe a conexão da planilha webSheet e o valor a pesquisado na planilha. Retorna a célula que contém o valor pesquisado ou uma mensagem de erro, se houver.</p>
# 
# <h3>func: move_ok_spreadsheet(array=info)</h3>
# 
# <p style="text-indent :5em;" > Recebe as informações do pedido a ser atualizado na planilha webSheets.<br>
#     Atualiza a aba Concluidos com o pedido já processado, adicionando o codigo MIRO na última coluna.</p>
#     
# <h3>func: move_failed_spreadsheet(array=info)</h3>
# 
# <p style="text-indent :5em;" > Recebe as informações do pedido a ser atualizado na planilha webSheets.<br>
#     Atualiza a aba Analise-manual com o pedido já processado, adicionando a mensagem de erro na última coluna.</p>

# In[3]:


def cell_find(sheet,value):
    #RETORNA A PRIMEIRA CELULA ENCONTRADA COM O VALOR PESQUISADO
    try:
        cell = sheet.find(value)

    except Exception as e:
        return e
    
    return cell

def move_ok_spreadsheet(info):
    error_message = None
    
    try:
        sheet = pieces.lib_processo.openWebSheet("API-leao-RegistroDeFrete-e68a2d5382c4.json","Casos-Dacte","Concluidos") 
        #Apenas para DEV
#         sheet = pieces.lib_processo.openWebSheet('mytest-273716-aaddc43030cc.json', 'meuTeste', 'Concluidos')
        ROW_INDEX = 2 # --------- > New row will be created at this index, pushing any existing rows down 
        sheet.insert_row(info, ROW_INDEX)
        pieces.lib.filelog("Movida")
    except Exception as e:
        pieces.lib.filelog("erro ao mover concluidos")
        error_message = e
    
    #RETURNING VALIDATIONS

    return error_message

def move_failed_spreadsheet(info):
    error_message = None
    try:
        sheet = pieces.lib_processo.openWebSheet("API-leao-RegistroDeFrete-e68a2d5382c4.json","Casos-Dacte","Analise_manual") 
        #Apenas para DEV
#         sheet = pieces.lib_processo.openWebSheet('mytest-273716-aaddc43030cc.json', 'meuTeste', 'Analise_manual')
        ROW_INDEX = 2 # --------- > New row will be created at this index, pushing any existing rows down 
        sheet.insert_row(info, ROW_INDEX)
        pieces.lib.filelog("Movida")

    except Exception as e:
        pieces.lib.filelog("erro ao mover analise")
        error_message = e
    
    #RETURNING VALIDATIONS
    return error_message
    
def move_retry_spreadsheet(info):
    error_message = None
    try:
        sheet = pieces.lib_processo.openWebSheet("API-leao-RegistroDeFrete-e68a2d5382c4.json","Casos-Dacte","Analise_robo") 
        #Apenas para DEV
        #sheet = pieces.lib_processo.openWebSheet('mytest-273716-aaddc43030cc.json', 'meuTeste', 'Analise_robo')
        ROW_INDEX = 2 # --------- > New row will be created at this index, pushing any existing rows down 
        sheet.insert_row(info, ROW_INDEX)
        pieces.lib.filelog("Movida")

    except Exception as e:
        pieces.lib.filelog("erro ao mover analise Robo")
        error_message = e
    
    #RETURNING VALIDATIONS
    return error_message

def retry_manual_rows():
    error_message = None
    final_rows = []
    try:
        sheet_retry = pieces.lib_processo.openWebSheet("API-leao-RegistroDeFrete-e68a2d5382c4.json","Casos-Dacte","Analise_robo") 
        sheet_pending = pieces.lib_processo.openWebSheet("API-leao-RegistroDeFrete-e68a2d5382c4.json","Casos-Dacte","Pendentes") 
        #Apenas para DEV
        #sheet_retry = pieces.lib_processo.openWebSheet('mytest-273716-aaddc43030cc.json', 'meuTeste', 'Analise_robo')
        #sheet_pending = pieces.lib_processo.openWebSheet('mytest-273716-aaddc43030cc.json', 'meuTeste', 'Pendentes')
        
        all_info = sheet_retry.get_all_values()
#         print(all_info)
        ROW_INDEX = 2 # --------- > New row will be created at this index, pushing any existing rows down 
        for row in all_info:
            if row[0] == "chave de acesso":
                pass
            else:
                row[26] = "OK"
                final_rows.append(row)
                sheet_retry.delete_row(2)
        #Envia todas as linhas para Pendentes
        sheet_pending.append_rows(final_rows)

    except Exception as e:
        pieces.lib.filelog("erro ao mover para Pendente")
        error_message = e
    
    #RETURNING VALIDATIONS
    return error_message


# <h1>entrardacte_Sure</h1>
# 
# Sem necessidade, esse módulo será mantido apenas para geração de logs.
# 
# <h4>Passos entrardacte_Sure</h4><br>
# • Geração de Logs<br>

# In[4]:


def entrardacte_sure():
    print("\n\n[Step]--> entrardacte_Sure - INICIO")
    print("\n\n[Step]--> entrardacte_Sure - FINAL")
    
    return


# <h1>Funçoes entrardacte</h1>
# 
# Contem a função que efetiva a geração da DACTE no sistema SAP e a função que atualiza a planilha WebSheets.
# 
# <h3>func: register_dacte(str=case_for_register)</h3>
# <p style="text-indent :5em;" > Recebe uma string com o código de 44 digitos, pesquisa esse código no sistema SAP, seleciona o pedido encontrado e seleciona a opção Gerar DACTE. Após a geração da DACTE, o código MIRO é gerado pelo sistema.<br>
# <br> A função retorna o código MIRO gerado </p>
# 
# <!-- <img src="images_doc/notepad_aberto.png" width=640 heigth=400> -->
# <br>
# 
# <h3>func: setup_clean_fields_SAP(session)</h3>
# <p style="text-indent :5em;" > Limpa os campo de parâmetro de busca na tela de pesquisa de casos</p>
# 
# 
# 
# 
# <!-- <img src="images_doc/notepad_aberto.png" width=640 heigth=400> -->
# <br>

# In[5]:


# from email.mime.text import MIMEText

def register_dacte(session,case_for_register):
    try:
        setup_clean_fields_SAP(session)
        #cola a chave do caso para pesquisar
        session.findById("wnd[0]/usr/txtS_CTEID-LOW").text = case_for_register
        #Pressiona o botaao de pesquisa
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        #seleciona a unica linha
        session.findById("wnd[0]/usr/cntlCONTAINER_100/shellcont/shell").selectedRows = "0"
        #Pressiona o botao para gerar a DACTE
        session.findById("wnd[0]/tbar[1]/btn[18]").press()
        #Coletando o numero da miro
        number_miro = session.findById("wnd[1]/usr/txtMESSTXT1").text
        print(number_miro)
        pieces.lib.filelog("numero miro {}".format(number_miro))
        #Fechando o pop-up
        session.findById("wnd[1]/tbar[0]/btn[0]").press()
        #retornar para a tela anterior
        session.findById("wnd[0]/tbar[0]/btn[3]").press()
        setup_clean_fields_SAP(session)
    except Exception as e:
        try:
            error_message = session.findById("wnd[1]/usr/txtMESSTXT1").text
            
            #Checking for blocker_user
            try:
                block_user = session.findById("wnd[1]/usr/txtMESSTXT2").text
                error_message = error_message + " " + block_user
                pieces.lib.filelog(error_message)
            except:
                pass
            
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
#             pieces.lib.set_var_process("processo_chave_id", case_for_register)
#             pieces.lib.set_var_process("status_dacte", error_message)
            return error_message
        except:
            error_message = "erro desconhecido"
#             pieces.lib.set_var_process("processo_chave_id", case_for_register)
#             pieces.lib.set_var_process("status_dacte", error_message)
            return error_message
            
    return number_miro

def setup_clean_fields_SAP(session):
    #limpa os campos para uma nova consulta
    pieces.lib_processo.enter_transaction_sap(session,"/nZLES010T")
    session.findById("wnd[0]/usr/chkP_PENDE").selected = False
    session.findById("wnd[0]/usr/chkP_ASSO").selected = False
    session.findById("wnd[0]/usr/chkP_SIMU").selected = True
    session.findById("wnd[0]/usr/chkP_ERRO").selected = False
    session.findById("wnd[0]/usr/chkP_GERA").selected = False
    session.findById("wnd[0]/usr/chkP_MANUAL").selected = False
    session.findById("wnd[0]/usr/chkP_REJEIT").selected = False
    session.findById("wnd[0]/usr/chkP_CANCEL").selected = False
    session.findById("wnd[0]/usr/chkP_ERRSEF").selected = False
    session.findById("wnd[0]/usr/ctxtS_DT_CR-LOW").text = ""
    session.findById("wnd[0]/usr/ctxtS_DT_CR-HIGH").text = ""
    return session

#----------------------------------------------------------------------


# <h1>Funções para envio de email</h1>
# 
# <h3>func: envia_email(array=all_text_row)</h3>
# 
# <p style="text-indent :5em;" > Efetua o envio individual do caso processado não estejam associados com um responsável na planilha webSheets para o e-mail "centraldefretes@leaoalimentosebebidas.com.br"</p>
# 
# <h3>func: envia_email_lote(array=all_text_content)</h3>
# 
# <p style="text-indent :5em;" > Efetua o envio de em lote dos casos processados associados com um responsável na planilha webSheets para o e-mail "centraldefretes@leaoalimentosebebidas.com.br"</p>
# 

# In[6]:



from core import *

def envia_email(all_text_row):
    """
    Função enviar_email:
    
    Entradas:
        arquivo                         # Nome do arquivo em pdf
        
    Retornos:
        receiver_email                  # Email Enviados
    """
    
    pieces.lib.ultradebug("\n\n[Step]--> [ enviar_email_individual ]")
    pieces.lib.filelog("[ enviar_email_individual ]")

    codigo_cte = all_text_row[3]
    codigo_cte = str(codigo_cte)
    status_miro = all_text_row[-1]
    status_miro = str(status_miro)
#     pieces.lib.msgbox(codigo_cte)

    info = "Caso {} Registrado: <br> {}".format(codigo_cte, status_miro)
    
    sender_email = "bots_inbox@bpatechnologies.com"
    password = 'bpa@1234'
    
    teste1 = "Caso "
    teste2 = codigo_cte + " cadastrado"

    html = """    <html>
      <body>
        <p>
           {}
        </p>
      </body>
    </html>
    """.format(info)
    
    title = "Caso Registrado {}".format(codigo_cte)
    footer = "Essa mensagem foi enviada automaticamente."
    
    body = footer
#     receiver_email = "melody@bpatechnologies.com"
    receiver_email = "centraldefretes@leaoalimentosebebidas.com.br"
    subject = title

    # Create a multipart message and set headers
    message = pieces.MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    part1 = pieces.MIMEText(html, "html")
    message.attach(part1)
        
    # Add body to email
    message.attach(pieces.MIMEText(body, "html"))
    text = message.as_string()

    # Log in to server using secure context and send email
    context = pieces.ssl.create_default_context()
    with pieces.smtplib.SMTP_SSL("smtp.gmail.com", "465", context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)
    
    pieces.lib.filelog("Email enviado com sucesso")
    return receiver_email

#----------------------------------------


def envia_email_lote(all_text_content):
    """
    Função enviar_email:
    
    Entradas:
        arquivo                         # Nome do arquivo em pdf
        
    Retornos:
        receiver_email                  # Email Enviados
    """
    
    pieces.lib.ultradebug("\n\n[Step]--> [ enviar_email_lote ]")
    pieces.lib.filelog("[ enviar_email_lote ]")

    qtd_cases = len(all_text_content)
    qtd_cases = str(qtd_cases)
    list = ""
    for case in all_text_content:

        row = (str(case["resp_user"]) + " - CT-e: " + str(case["cte_number"]) + " - " +
               "Status: " + str(case["status"]) +
               "<br>")
        list = list + row
    

    
    sender_email = "bots_inbox@bpatechnologies.com"
    password = 'bpa@1234'
    
    
    html = """<html>
  <body>
    <p>Lista de Casos Processados:<br>
       <br>
       {}
    </p>
  </body>
</html>
""".format(list)
    

        
    title = "Casos Processados em Lote: {}".format(qtd_cases)
    footer = "Essa mensagem foi enviada automaticamente"

    body = footer
#     receiver_email = "melody@bpatechnologies.com"
    receiver_email = "centraldefretes@leaoalimentosebebidas.com.br"
    subject = title

    # Create a multipart message and set headers
    message = pieces.MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    part1 = pieces.MIMEText(html, "html")
    message.attach(part1)
        
    # Add body to email
    message.attach(pieces.MIMEText(body, "html"))
    text = message.as_string()

    # Log in to server using secure context and send email
    context = pieces.ssl.create_default_context()
    with pieces.smtplib.SMTP_SSL("smtp.gmail.com", "465", context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)
    
    pieces.lib.filelog("envia_email_lote -- FINAL")
    return receiver_email


# <h1>Testes e Homologação</h1>
# <br>
# <p>Para fins de desenvolvimento interativo, é possível simular a estrutura do framework (modo Training) e rodar o código do StepName diretamente no Jupyter:</p>

# In[7]:


from core import *

if isdebug(__name__):    # somente rodar o codigo no Jupyter
    #entrardacte()
    #entrardacte_sure()
    entrardacte()
    
    


# <h1>Unit Tests</h1>
# <br>
# <p>Cada função que realiza um trabalho significativo deverá ter seu respectivo teste unitário.
# 
# Em contradição ao jeito que programavamos em .ahk, o "sentido do desenvolvimento de código" agora deverá respeitar a metodologia de TDD (test driven development) - Primeiramente desenha-se  as funções de teste unitário e <b>somente então</b> inicia-se a codificação em si, com o o objetivo de satisfazer os testes unitários.</p>

# In[8]:


from core import *
# import gspread 
# from oauth2client.service_account import ServiceAccountCredentials

def test_move_ok_spreadsheet():
    test_cases = [{"test_name": "tarefa_correta",
                   "info": ["Unit","Test","01"],
                   "expected_result": [None, ["Unit","Test", "01"]]
                  }]
    
    ROW_INDEX = 2
    results = []
    expected_results = []
    
    for test_case in test_cases:
        #opening connection to websheets
        sheet_concluded = pieces.lib_processo.openWebSheet("API-leao-RegistroDeFrete-e68a2d5382c4.json","Casos-Dacte","Concluidos") #file on folder src/ipynb
        
        #Apenas para DEV
#         sheet_concluded = pieces.lib_processo.openWebSheet('mytest-273716-aaddc43030cc.json', 'meuTeste', 'Concluidos')
        
        
        #executing tested function
        error_message = move_ok_spreadsheet(test_case["info"])
        
        #Consulting rows
        new_row = sheet_concluded.row_values(ROW_INDEX)
            
        results.append([error_message, new_row])
        
        #Deleting tested row
        sheet_concluded.delete_row(ROW_INDEX)
        
        expected_results.append(test_case["expected_result"])  

    print("unity test: {}".format(move_ok_spreadsheet.__name__))
    print("results {}".format(results))
    print("expected_results {}".format(expected_results))

    assert results == expected_results

    print("Teste bem sucedido")
    return
    
    
def test_move_failed_spreadsheet():
    test_cases = [{"test_name": "tarefa_correta",
                   "info": ["Unit","Test","02"],
                   "expected_result": [None, ["Unit","Test", "02"]]
                  }]
    
    ROW_INDEX = 2
    results = []
    expected_results = []
    
    for test_case in test_cases:
        #opening connection to websheets
        sheet_concluded = pieces.lib_processo.openWebSheet("API-leao-RegistroDeFrete-e68a2d5382c4.json","Casos-Dacte","Analise_manual") #file on folder src/ipynb
        
        #Apenas para DEV
#         sheet_concluded = pieces.lib_processo.openWebSheet('mytest-273716-aaddc43030cc.json', 'meuTeste', 'Analise_manual')
            
        #executing tested function
        error_message = move_failed_spreadsheet(test_case["info"])
        
        #Consulting rows
        new_row = sheet_concluded.row_values(ROW_INDEX)
            
        results.append([error_message, new_row])
        
        #Deleting tested row
        sheet_concluded.delete_row(ROW_INDEX)
        
        expected_results.append(test_case["expected_result"])  

    print("unity test: {}".format(move_failed_spreadsheet.__name__))
    print("results {}".format(results))
    print("expected_results {}".format(expected_results))

    assert results == expected_results

    print("Teste bem sucedido")
    return

# permitir os testes de serem rodados somente via Jupyter
if isdebug(__name__):
    test_move_ok_spreadsheet()
    test_move_failed_spreadsheet()
    pass


# In[ ]:




