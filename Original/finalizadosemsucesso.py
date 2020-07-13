#!/usr/bin/env python
# coding: utf-8

# <h1>Processo RegistroFrete</h1>
# 

# <h2>Framework Python BPA</h2>
# 
# Visando melhorar a qualidade de nossos robôs Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

# <h1>finalizadosemsucesso</h1>
# 
# O processo RegistroFrete utiliza do Notepad.<br>
# A abertura da aplicação será feita somente no finalizadosemsucesso, logo a função está declarada neste mesmo pedaço de código.<br>
# Entretanto, a "função de escrever no Notepad" é compartilhada com outros StepNames, por este motivo ela está localizada no lib_processo.ipynb<br><br>
# 
# <h3>Passos finalizadosemsucesso</h3><br>
# • Abrir Notepad;<br>
# • Escrever uma credencial obtida do BPASafe no Notepad.<br>

# In[5]:


from core import *

def finalizadosemsucesso():
    print("\n\n[Step]--> finalizadosemsucesso")

    # fechar o notepad, se estiver aberto
    pieces.lib_processo.fechar_notepad()
    
    # Abrir o Notepad em "modo produção" - Variável no gvars.ipynb
    abriu_notebook = abrir_notepad(pieces.gvars.ambiente)

    # Retorno da abertura da aplicaçao
    pieces.lib.filelog("abriu_notebook:\n\t" + str(abriu_notebook))

    # Tudo OK, podemos continuar com o processo
    if abriu_notebook:
        pieces.lib_processo.escrever_notepad(string_escrever="Credenciais sistema 1:\n", metodo_escrever=3)
        pieces.lib_processo.escrever_notepad(string_escrever=str(pieces.lib.bpa_safe_get('sistema1')))
    else:
        pieces.lib.iAmLost("[RPAReset]|Notepad não abriu corretamente.")
    
    return
     


# <h1>finalizadosemsucesso_Sure</h1>
# 
# Com o Notepad aberto, tentaremos escrever algo para verificar se realmente ele está aberto & responsivo.<br>
# <font color='red'>Atenção:</font> O texto digitado deverá apagado logo após, deixando o Notepad limpo para o processo.<br><br>
# 
# <h4>Passos finalizadosemsucesso_Sure</h4><br>
# • Apagar o conteudo do Notepad.<br>

# In[6]:


def finalizadosemsucesso_sure():
    print("\n\n[Step]--> finalizadosemsucesso_Sure")
    
    # Agora apagar o conteudo do Notepad
    notepad_em_branco = pieces.lib_processo.apagar_notepad()
    print("notepad_em_branco:\n\t" + str(notepad_em_branco))

    # Teste adicional para ver se ta OK a aplicação (ex: alguma atividade pós-login, neste caso, verificar se ta apagado mesmo)
    texto_notepad = pieces.lib_processo.ler_notepad()
    print("texto_notepad:\n\t" + str(texto_notepad))
    
    return


# <h1>Funçoes finalizadosemsucesso</h1>
# 
# Contem a funcão de abrir o notepad.
# 
# <h2>Funcoes Notepad</h2>
# <h3>func: abrir_notepad()</h3>
# <p style="text-indent :5em;" > Procura por uma instancia aberta do notepad. Se nao localizar, inicia uma nova.<br></p>
# 
# <img src="images_doc/notepad_aberto.png" width=640 heigth=400>
# <br>

# In[11]:


def abrir_notepad(ambiente_aplicacao, *, timeout=30):
    """
    Inputs:
        ambiente_aplicacao  #   Str 'prd' ou 'hmg', indicando qual path irá ser utilizado (vide gvars)
        timeout             #   Tempo permitido para abrir o Notepad antes de retornar -1
        
    Retornos:
        -1                  #   Erro: Timeout ao tentar abrir o notepad
        -2                  #   Erro: Path do app não encontrado / invalido
        str window title    #   Sucesso: String contendo o nome do aplicativo    
    """
    
    pieces.lib.filelog("[[ abrir_notepad ]]")
    
    # Validacao do input ambiente
    ambiente_aplicacao = ambiente_aplicacao.lower() if isinstance(ambiente_aplicacao, str) else ambiente_aplicacao
    if (ambiente_aplicacao != 'prd' and ambiente_aplicacao != 'hmg'):
        pieces.lib.msgbox('abrir_notepad: Ambiente invalido -->' + ambiente_aplicacao)
        pieces.lib.iamlost('abrir_notepad: Ambiente invalido -->' + ambiente_aplicacao)

    # Loop com timer de até 10s para abrir notepad (senão False e consequentemente estoura iAmLost)
    timer = pieces.lib.Timer(timeout)
    while timer.not_expired:
        # Nomes que iremos usar como parâmetro para ver se a aplicação abriu corretamente
        win_title = pieces.gvars.notepad_title_prd if ambiente_aplicacao == 'prd' else pieces.gvars.notepad_title_hmg
        
        # Pode ser apenas um nome (string) ou uma list de nomes [string1, string2]
        if isinstance(win_title, str):
            win_title = [win_title]

        for possible_name in win_title:
            try:
                app_notepad = pieces.pywinauto.application.Application(backend='uia').connect(class_name='Notepad')
                app_top_window = app_notepad.top_window()
                app_top_window.set_focus()
                return app_top_window.texts()[0]
            except pieces.pywinauto.application.findwindows.ElementNotFoundError:
                pass
        
        # Senão, abrir a aplicação
        else:
            if ambiente_aplicacao == "prd":
                pieces.lib.filelog("Abrindo NoteBook prd")
                path = pieces.gvars.notepad_path_prd
                pieces.lib.msgbox(path, timeout=1)
                try:
                    app_notepad = pieces.pywinauto.application.Application().start(path)
                except pieces.pywinauto.application.AppStartError:
                    # Não conseguiu abrir o aplicativo, ie: path invalido
                    return -2
            elif ambiente_aplicacao == "hmg":
                pass # @TODO CODE @
            else:
                pieces.lib.msgbox("ambiente '" + ambiente + "' não mapeado ainda")
                
    return -1


# <h1>Testes e Homologação</h1>
# <br>
# <p>Para fins de desenvolvimento interativo, é possível simular a estrutura do framework (modo Training) e rodar o código do StepName diretamente no Jupyter:</p>

# In[8]:


from core import *

if isDebug(__name__): # somente rodar o codigo no Jupyter
    #finalizadosemsucesso()
    #finalizadosemsucesso_sure()
    #print(abrir_notepad('prd'))
    finalizadosemsucesso()


# <h1>Unit Tests</h1>
# <br>
# <p>Cada função que realiza um trabalho significativo deverá ter seu respectivo teste unitário.
# 
# Em contradição ao jeito que programavamos em .ahk, o "sentido do desenvolvimento de código" agora deverá respeitar a metodologia de TDD (test driven development) - Primeiramente desenha-se  as funções de teste unitário e <b>somente então</b> inicia-se a codificação em si, com o o objetivo de satisfazer os testes unitários.</p>

# In[12]:


from core import *


def test_abrir_notepad():
    result = abrir_notepad("prd")
    expected_result = ["Untitled - Notepad", "Sem Título - Bloco de Notas"]

    print("Resultado test_abrir_notepad():\n\t" + str(result))
    assert result in expected_result
    print("test_abrir_notepad: Sucesso!\n\n")  
   
        
def test_escrever_notepad():
    test_string = "Unit Testing"
    pieces.lib_processo.escrever_notepad(string_escrever=test_string)
    result = pieces.lib_processo.ler_notepad()
    expected_result = test_string

    print("Resultado test_escrever_notepad():\n\t" + str(result))
    assert expected_result in result
    print("test_escrever_notepad(): Sucesso!\n\n")  

    
def test_apagar_notepad():
    test_string = "Esta string devera ser apagada!"
    pieces.lib_processo.escrever_notepad(string_escrever=test_string)
    result = pieces.lib_processo.apagar_notepad()
    expected_result = True

    print("Resultado test_apagar_notepad():\n\t" + str(result))
    assert result == expected_result
    print("test_apagar_notepad(): Sucesso!\n\n")  

    
# permitir os testes de serem rodados somente via Jupyter
if isDebug(__name__):
    test_abrir_notepad()
    test_escrever_notepad()
    test_apagar_notepad()

    
    

