#Automatic 'import pieces' by BPA Deploy - Nose Testing
import pieces

#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from core import *

def trata_erro():
    pieces.lib.ultradebug("\n\n[Step]--> trata_erro")
    
    try:
        app_mkt = pieces.pywinauto.application.Application(backend='uia').connect(title_re='.*issd.*')
        pieces.lib.filelog("Fechando o MKT...")
        app_mkt.kill()
    except pieces.pywinauto.application.findwindows.ElementNotFoundError:
        pass
    
    try:
        app_sci = pieces.pywinauto.application.Application(backend='uia').connect(title_re='.*SCI - Sistema.*')
        pieces.lib.filelog("Fechando o SCI...")
        app_sci.kill()
    except pieces.pywinauto.application.findwindows.ElementNotFoundError:
        pass
    
    pieces.lib.ultradebug("\n\n[Fim Step]--> trata_erro")
    return

def trata_erro_sure():
    pieces.lib.ultradebug("\n\n[Step]--> trata_erro_sure")
    pieces.lib.ultradebug("\n\n[Fim Step]--> trata_erro_sure")
    return

