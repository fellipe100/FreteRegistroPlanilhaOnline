def isdebug(module=""):
	try:
		# se for fora do jupyter, da except e já cai no False
		type(get_ipython()).__module__.startswith('ipykernel.')

		# se for um import "entre"  jupyters, somente retornar True se for no primeiro nivel
		# Ex: Se rodar "import <notebook>" dentro de outro notebook, irá retornar False
		return module == "__main__"
	except:
		# Estou no framework bpa.exe
		return False


################ ALL DEPRECATED FUNCTIONS SHOULD GO HERE
# If the reason for deprecation is due naming conventions, it is ok to not specify explicitly, but otherwise please do it
def isDebug(module):
    print("func 'isDebug()' is deprecated! Please use 'isdebug()' instead.")


# Imports must be done AFTER funcs definitions due to 'import_ipynb' requiring isdebug()
import lib
import json
from os import path
if isdebug("__main__"):
	import import_ipynb
import pieces
from nose.tools import istest
from nose.tools import nottest

