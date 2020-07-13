#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import gspread 


# In[ ]:


from oauth2client.service_account import ServiceAccountCredentials


# In[ ]:




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


# In[ ]:


a = openWebSheet("API-leao-RegistroDeFrete-e68a2d5382c4.json","Casos-Dacte","Pendentes")


# In[ ]:


a


# In[ ]:




