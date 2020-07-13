import pieces
import lib
import sys
import json
import os
import traceback
import os.path
from os import path
import logging
from datetime import datetime
import io

# Necessario para assegurar que nenhum charmap fora do utf-8 quebre o cmd do windows (ex: print com caractere especial do MKT)
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')

logging.basicConfig(filename=lib.file_log_name)

# Deve ser enviado por argumento a função que será executada naquele momento
#   > O argumento deverá se parecer como o exemplo abaixo:
#    >> pieces.PreparaAmbiente.PreparaAmbiente()
#        >> pieces - é o lugar onde deverá está todos os includes que o python irá executar
#        >> PreparaAmbiente - função a ser executada pelo python

try:
    execute = "pieces." + sys.argv[1] + "()"
    lib.filelog("----- Executando: " + execute + " ----- Len(sys.argv) = " + str(len(sys.argv)))
    eval(execute)
    lib.filelog("----- Fim Exec: " + execute + " -----")
except Exception as e:
    lib.filelog("\n\n")
    lib.filelog("-"*75)
    lib.filelog("----- Exception ao executar: " + execute + " -----")
    logging.error(e, exc_info=True)
    exc_type, exc_value, exc_traceback = sys.exc_info()

    print("*** print_tb:")
    lib.filelog(repr(traceback.extract_tb(exc_traceback, limit=1)))
    print("*** print_exception:")
    # exc_type below is ignored on 3.5 and later
    traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2)

    print("*** print_exc:")
    traceback.print_exc(limit=2)
    lib.filelog("*** format_exc, first and last line:")
    formatted_lines = traceback.format_exc().splitlines()
    lib.filelog(formatted_lines[0])
    lib.filelog(formatted_lines[-1])
    lib.filelog("*** format_exception:")

    lib.filelog(repr(traceback.extract_tb(exc_traceback)))
    lib.filelog("*** format_tb:")
    lib.filelog(repr(traceback.format_tb(exc_traceback)))
    lib.filelog(f"*** tb_lineno: {exc_traceback.tb_lineno}")
    lib.filelog("-"*75)
    lib.filelog("\n\n")
    err = {
        "line": exc_traceback.tb_lineno,
        "what": repr(traceback.format_tb(exc_traceback)),
        "function": execute,
    }
    lib.iAmBroked(f"Erro desconhecido executar o pieces: {execute}", err)

# Se chegou aqui, significa sucesso
# quando iAmLost/iAmBroked/iDontKnow, o Python "se mata" e não chegaria aqui
lib.write_communication()
