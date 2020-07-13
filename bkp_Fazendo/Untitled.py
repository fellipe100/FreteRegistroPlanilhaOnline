#!/usr/bin/env python
# coding: utf-8

# In[2]:


def verificado_Dados_Excel():    
    # value --- Texto para procurar na celula
    
    verificador = True
    
    #i = 0
    value = 'Ok'
    
    while (verificador):
        
        try:
            f = open("TestePython123.txt", "w")

            sheet = pieces.lib_processo.openWebSheet("API-leao-RegistroDeFrete-e68a2d5382c4.json","Casos-Dacte","Pendentes") 
            cell = cell_find(sheet,value)
            f.writelines(cell)
            row = sheet.row_values(cell.row)
            f.writelines(row)
           
            
            if(row[0] != ''):
                verificador = False 
           
        except:
            f.writelines("Erro ")
            
            
    return 


# In[ ]:


verificado_Dados_Excel()


# In[ ]:




