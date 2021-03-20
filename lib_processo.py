#!/usr/bin/env python
# coding: utf-8

# <h1>Funçoes utilizadas no processo &&@@processName@@&&</h1>

# In[ ]:


import pieces


# <h1>Funcoes Notepad</h1><br>
# 
# <b>escrever_notepad( string_escrever, *, metodo_escrever="123" ):</b><br>
# <p style="text-indent :5em;" > Escreve a str 'string_escrever' na instancia aberta do Notepad. </p>
# 
# <b>fechar_notepad( timeout=5 ):</b><br>
# <p style="text-indent :5em;" > Fecha a(s) instancia(s) abertas dos apps com classname Notepad.</p>
# 
# <b>contar_linhas( timeout=10 ):</b><br>
# <p style="text-indent :5em;" > Captura todo o texto contido no Notepad e conta quantas linhas possuem texto != ''.</p>
# 
# <b>apagar_notepad():</b><br>
# <p style="text-indent :5em;" > Captura todo o conteudo de um Notepad através do Control+A e então deleta.</p>
# 
# <b>ler_notepad():</b><br>
# <p style="text-indent :5em;" > Captura todo o conteudo de um Notepad através do Control+A, Control+C e retorna como uma str.</p>
# 

# In[1]:


def get_running_sap_session():
    """
    Inputs
        username        # str SAP Username
        password        # str SAP Password
        env             # str SAP Connection enviroment ["SAP - QA", "SAPPRD - 01"]
        
    Outputs
        SAP obj         # Success: SAP COM Object
        None            # Success: But SAP not found
        -2              # Error: Could not locate SAPGUI in COM lib (should NOT happen, ever)
    """
    
    pieces.lib.filelog("[[ get_running_sap_session ]]")
    
    #pieces.lib.time.sleep(15)
    #pieces.lib.msgbox("função GET_RUNNIG_SESSION - SAPGUI - A")
    #pieces.lib.time.sleep(10)
    import pygetwindow as gw

    #pieces.lib.time.sleep(5) 
    win = gw.getWindowsWithTitle('Monitor de CTe de Entrada')[0]
    win.activate()
    
    SapGuiAuto = pieces.win32com.client.GetObject('SAPGUI')
    
    if not type(SapGuiAuto) == pieces.win32com.client.CDispatch:
        return -2
    
    # Verifying whether a SAP logon window already exists
    timer = pieces.lib.Timer(10)
    RETURN_TITLE = 0
    sap_exists = False
    try:
        
        #pieces.lib.msgbox("função GET_RUNNIG_SESSION - SAPGUI - B")
        #pieces.lib.time.sleep(5) 
        
        sap_app = pieces.pywinauto.application.Application(backend='uia').connect(class_name='SAP_FRONTEND_SESSION')

        # Get the correct window
        # Can not be hidden (title = "") and can not be "SAP Logon"
        for w in sap_app.windows():
            #pieces.lib.msgbox("função GET_RUNNIG_SESSION - SAPGUI - C - if")
            win.activate()
            #pieces.lib.time.sleep(5) 
            window_title = w.texts()[RETURN_TITLE]
            if not "SAP Logon" in window_title and window_title != "":
                sap_exists = w
                break

        if sap_exists:
            #pieces.lib.msgbox("função GET_RUNNIG_SESSION - SAPGUI - C - focus")
            win.activate()
            sap_app_top_window = sap_exists
            sap_app_top_window.set_focus()
    except pieces.pywinauto.application.findwindows.ElementNotFoundError:
        
        pass

    #pieces.lib.msgbox("função GET_RUNNIG_SESSION - SAPGUI - GETSCRIPTINGENGINE" , timeout=3)
    win.activate()
    
    #pieces.lib.time.sleep(5) 
    application = SapGuiAuto.GetScriptingEngine

    # Return existing SAP if already online
    timer = pieces.lib.Timer(5)
    session = application.ActiveSession
    while session is None and sap_exists and timer.not_expired:
        session = application.ActiveSession
            
    #pieces.lib.msgbox("saindo da função GET_RUNNIG_SESSION - retorno")    
    win.activate()
    
    return session, application
#-------------------------------------------------------------------------------------------------------------------------------
def define_date_plus_interval(starting_date, interval):
    datetime = pieces.lib.datetime
    timedelta = pieces.lib.timedelta
    convert_to_datetime = lambda string_date : datetime(*list(map(int, string_date.split("/"))))
    starting_date_as_datetime = convert_to_datetime("/".join((starting_date.split("/")[::-1])))
    final_date = starting_date_as_datetime + timedelta(int(interval))
    final_date = final_date.strftime("%d.%m.%Y")
    return final_date
#-------------------------------------------------------------------------------------------------------------------------------
#Opens a worksheet via API at websheets Google
def openWebSheet(authFile, worksheet, activeSheet=''):

    # authFile                 =    name of authentication file provided by Google API Service
    # worksheet                =    name of the websheet
    # activeSheet (optional)   =    title of the sheet to be activated and returned. If empty, returns default sheet  
    
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = pieces.ServiceAccountCredentials.from_json_keyfile_name(authFile, scope)
    client = pieces.gspread.authorize(creds)
  
    # Opens the conection
    ws = client.open(worksheet)

    # Checks if the sheet title was passed to the function
    if activeSheet != '':
        return ws.worksheet(activeSheet)      
    
    #Returns the worksheet on the default sheet
    return ws.sheet1

#------------------------------------------------------------------------------------------------------------------------------
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


# <h1>Funções Regras de Negócio</h1><br>
# <b>is_odd( number ):</b><br>
# <p style="text-indent :5em;" > Retorna se um número é impar (True) ou par (False).</p>

# In[5]:


def is_odd(number):
    """
    Inputs:
        number     # Integer ou str que possa ser convertido para uma integer
        
    Retornos:
        True       # 'number' é impar
        False      # 'number' é par
        -1         # 'number' é float OU não pode ser convertido para intenger
    """
    
    # se float ou se não der para converter para int, tipo invalido
    try:
        if isinstance(number, float):
            raise Exception
            
        number = int(number)
    except:
        return -1
    
    return number % 2 == 1


# <h1>Funções Automação Mouse / Manuseio de Arquivos</h1><br>
# 
# <b>ler_arquivo_txt( file_path ):</b><br>
# <p style="text-indent :5em;" > Retorna o conteudo em str de um arquivo de texto (.txt, .json, .py...) localizado no full_path 'file_path'.</p><br>
# 
# <b>dancar_mouse( side="left"/"right", *, timeout=20, travel_time=0.1 ):</b><br>
# <p style="text-indent :5em;" > Realiza uma automação do mouse utilizando o pyautogui em determinado lado da tela (esquerdo/dirieto).</p>
# 
# <img src="images_doc/dancar_mouse.gif" width=640 heigth=400>
# <br>

# In[6]:


def ler_arquivo_txt(file_path):
    """
    Inputs:
        file_path  # Full file path até o arquivo .txt
        
    Retornos:
        str        # Conteudo do arquivo
        -1         # File_path invalido/inexistente
        -2         # TypeError devido a tipo de input invalido: file_path não é uma string ou path
        -3         # Erro desconhecido ao tentar ler o .txt
    """
    
    file_contents = None
    try:
        with open(file_path, encoding='utf-8') as file:
            file_contents = file.read()
    except FileNotFoundError:
        file_contents = -1
    except TypeError:
        file_contents = -2
    except:
        file_contents = -3
    
    return file_contents


def dancar_mouse(side=None, *, timeout=20, travel_time=0.1):
    """
    Inputs:
        side             # Em qual lado (direita/esquerda) o mouse deve se movimentar
                            ['left', 'l', 'e', 'esq', 'esquerda', 'esquerdo']
                            ['right', 'r', 'd', 'dir', 'direita', 'direito']
        timeout          # Tempo permitido para relizar a tarefa
        travel_time      # tempo em segundos para cada deslocamento do mouse
        
    Retornos:
        -1                # Excedeu timeout para realizar a tarefa
        list Points(x,y)  # Todos os pontos (x,y) em que o cursor 'parou' ao longo do percurso
    """
    
    if side is None or not isinstance(side, str):
        pieces.lib.iamlost("dancar_mouse(): Parametro 'side' não especificado ou invalido.")
    
    screen_width = pieces.pyautogui.size().width
    screen_height = pieces.pyautogui.size().height
    mid_screen_width = int(screen_width/2)
    
    if side.lower() in ['left', 'l', 'e', 'esq', 'esquerda', 'esquerdo']:
        side = 'left'
        initial_point = (20, 20)
        right_limit = mid_screen_width
        left_limit = 20
    elif side.lower() in ['right', 'r', 'd', 'dir', 'direita', 'direito']:
        side = 'right'
        initial_point = (mid_screen_width, 20)
        right_limit = screen_width
        left_limit = mid_screen_width
    else:
        pieces.lib.iamlost("dancar_mouse(): Parametro 'side' invalido. Esperado 'left' ou 'right'.")
        
    pieces.pyautogui.moveTo(initial_point[0], initial_point[1])
    current_pos = pieces.pyautogui.position()
    list_pos = []
    
    timer = pieces.lib.Timer(timeout)
    while timer.not_expired:
        
        list_pos.append(current_pos)

        new_x = current_pos[0] + 150 if current_pos[0] + 150 < right_limit else right_limit
        pieces.pyautogui.moveTo(new_x, None, travel_time)

        if new_x >= right_limit:
            new_y = current_pos[1] + 200 if current_pos[1] + 200 < screen_height * 0.8 else int(screen_height * 0.8) + 1
            pieces.pyautogui.moveTo(left_limit, new_y, travel_time)

        current_pos = pieces.pyautogui.position()

        if current_pos[1] > screen_height * 0.8:
            return list_pos
        
        
    return -1
    


# In[ ]:




