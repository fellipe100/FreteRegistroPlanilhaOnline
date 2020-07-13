import inspect
import os
import os.path
import json
import copy
import base64
from ahk import AHK
from datetime import datetime
from datetime import timedelta
from pathlib import Path
import time
import configparser
import core
import requests
import codecs
import random
import re #regex
import subprocess
import psutil
import shutil
from tkinter import messagebox

clear = lambda: os.system('cls')
config = configparser.ConfigParser()
config.read('config.ini')
config.sections()

# Não existe o BPAEngine na folder E/OU .ahk interpreter no path do usuario no windows
drive_letter = os.getcwd()[:1]
path_engine_ahk = drive_letter + ':\\BPAEngine\\BPAEngine.exe'
if not os.path.exists(path_engine_ahk):
    messagebox.showinfo("Atenção", "Missing BPAEngine!\n\nGet it using BPA Deploy (or something else) and install it at " + path_engine_ahk + "\n\nClosing Python.")
    os._exit(0)

engine = AHK(executable_path=path_engine_ahk)
def getEngine():
    return get_ahk_engine()

def get_ahk_engine():
    return engine


def close_process(process_name):
    c_kill = 0
    
    try:
    
        for process in psutil.process_iter(['pid', 'name', 'username']):
            # check whether the process name matches
            if process.name().lower() == process_name.lower():
                filelog("close_process(): Found '{}'. Killing it".format(process_name))
                process.kill()
                c_kill += 1
    except:
        # TODO - not silence it completely?
        pass

    return c_kill


def validate_email(email):
    """
    Inputs
        email         # str - Expected to contain both @ and at least a single dot "." after @ (ex: thiago.p@bpatecnologies.com)
        
    Outputs
        bool True               # Success: 'email' is valid
        bool False              # Warning: 'email' is invalid
        -2                      # Error: 'email' is invalid. Not str.
    """
    
    # debug purposes
    vars_debug = get_passed_parameters(validate_email, locals())
    
    # this is the var to return and should be either True or False (unless return -2) 
    email_is_valid = None
    
    # Input Validation
    if not isinstance(email, str):
        filelog("validate_email({}): Error: 'email' is invalid. Not str.".format(vars_debug))
        return -2
    
    #### Regex explanation:
    # Only a single @ is allowed
    # Domain ending may be of length 2 or 3
    # personal info (substring before @) can't be length 0
    regex_rule = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    email_is_valid = re.search(regex_rule, email) is not None
    
    return email_is_valid 

    
def get_values_config(session, key, *, warn_on_keyerror=True):
    try:
        retrieved_value = config[session][key]
        if retrieved_value.lower() == "true":
            retrieved_value = True
        elif retrieved_value.lower() == "false":
            retrieved_value = False
        elif retrieved_value.strip() == "":
            retrieved_value = "ERROR"

        return retrieved_value

    except KeyError:
        if warn_on_keyerror:
            ultradebug("Key " + str(key) + " nao existe na section '" + str(session) + "' do config.ini. Verificar.")
        return "ERROR"

class http:
    def __init__(self):
        self.header = {}
        self.url = ''
        self.body = ''

    def set_url(self, value):
        self.url = value
        return True

    def set_header(self, key, value):
        self.header[key] = value
        return True

    def set_body(self, value):
        self.body = value
        return True

    def get_header(self, key=''):
        if key == '':
            return self.header
        else:
            return self.header[key]

    def get_body(self):
        return self.body

    def get_url(self):
        return self.url

    def post(self):
        return eval(
            "requests.post('" + self.url + "', data='" + self.body + "', headers=" + json.dumps(self.header) + ")")

    def get(self):
        return eval(
            "requests.get('" + self.url + "',  headers=" + json.dumps(self.header) + ")")

class dateTime:
    def getTime():
        x = datetime.now()
        x = str(x)
        x = x.replace(" ", "T")
        x = x + "Z"
        return x


def read_csv(path, *, delimiter=",", encoding='utf-8', row_start=1, replace_headers=None):
    """
    Inputs
        path               # str, path - Relative or Absolute full path to text file (can be any "readable" extension).
        delimiter          # str - Delimiter that should be used to parse the file (default: ',').
        encoding           # str - The encoding that should be used while reading the file - default: uft-8
        row_start          # int - First row starts as 1. All rows_index < row_start will be ignored.
        replace_headers    # list of str - Use a custom header list instead of whatever is written in the csv.
    Outputs
        dict (can be "")   # Success: Contents of the file parsed into a list of dictonaries.
        -2                 # Error: 'path' is invalid. Not str or path.
        -3                 # Warning: 'path' does not lead to any file.
        -4                 # Error: file found is not "readable".
        -5                 # Error: 'delimiter' is invalid. It can not be an underscore '_' or whitespace ' '
    """
    
    # for debugging purposes
    vars_debug = get_passed_parameters(read_csv, locals())

    try:
        path = str(path)
    except:
        filelog("read_csv({}): Error: 'path' is invalid. Not str or path.".format(vars_debug))
        return -2
    

    if replace_headers is not None and not isinstance(replace_headers, list):
        filelog("read_csv({}): Error: 'replace_headers' is invalid. Not a list.".format(vars_debug))
        return -3
    
    try:
        row_start = int(row_start)
    except:
        filelog("read_csv({}): Error: 'row_start' is invalid. Not int.".format(vars_debug))
        return -4
    
    if delimiter in [" ", "_"]:
        filelog("read_csv({}): Error: 'delimiter' is invalid. It can not be an underscore '_' or whitespace ' '".format(vars_debug))
        return -5

    try:
        with open(path, 'r', encoding=encoding, errors='ignore') as f:
            lines = f.read()
            lines = lines.split("\n")
            lines = lines[:-1] if lines[-1] == "" else lines
            
            for line in lines:
                line.replace("'",'').replace('"','')
            tbl_data = []
            for idx, row in enumerate(lines):
                idx += 1 
                if idx == row_start:
                    if replace_headers is not None:
                        headers = replace_headers
                    else:
                        custom_translation_dict = {
                            " ": "_",
                            "-": "_",
                            '"' : '',
                            "'" : ''
                        }
                        row_without_special_characters = row.lower()
                        row_without_special_characters = str_replace_dict(row_without_special_characters, custom_translation_dict)
                        row_without_special_characters = unidecode.unidecode(row_without_special_characters)

                        headers = row_without_special_characters.split(delimiter)
                    continue
                elif idx < row_start:
                    continue

                this_row_dict = {}
                row = row.replace("'",'').replace('"','')
                this_row_splitted = row.split(delimiter)
                for idx, ele in enumerate(headers):
                    this_row_dict[ele] = this_row_splitted[idx]
                tbl_data.append(this_row_dict)

    except FileNotFoundError:
        filelog("read_csv({}): Warning: 'path' does not lead to any file.".format(vars_debug))
        return -3
    except UnicodeDecodeError as err:
        filelog("read_csv({}): Error: file found is not 'readable'. >> {}".format(vars_debug, err))
        return -4

    return tbl_data

    
def validate_cnpj(cnpj, format_return=True):
    """
    Inputs
        cnpj            # int, str - CNPJ to be tested/validated. May contain special characaters or be pure numeric.
        format_return   # boolean - Whether CNPJ (if valid) should be returned formated (11.222.333/0001-81)
                                    or not (numeric only, 11222333000181)
    Outputs
        str cnpj        # Success: CNPJ is VALID and is returned, formated or not, depending on users choice
        False           # Success: CNPJ is invalid
        -2              # Error: 'cnpj' argument is invalid. Not str.
        
    """
    
    try:
        cnpj = str(cnpj).strip()
    except:
        return -2
    
    cnpj = ''.join([c for c in cnpj if c.isdigit()])

    if len(cnpj) < 14:
        return False

    # new_cnpj = cnpj_without_validation_digits
    new_cnpj = cnpj[:12]

    # Increment new_cnpj with 2 extra digits (so it goes back to len() == 14) based on the validation prod rule
    prod = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    while len(new_cnpj) < 14:
        r = sum([int(x)*int(y) for (x, y) in zip(new_cnpj, prod)]) % 11
        if r > 1:
            f = 11 - r
        else:
            f = 0
        new_cnpj = new_cnpj + str(f)
        prod.insert(0, 6)

    # If the recently created new_cnpj is equal to original input cnpj,
    # It means the original validation digits are correct and therefore input cnpj is valid
    if new_cnpj == cnpj:
        if format_return:
            return "%s.%s.%s/%s-%s" % ( cnpj[0:2], cnpj[2:5], cnpj[5:8], cnpj[8:12], cnpj[12:14] )
        else:
            return cnpj
    return False


# get_file_from_folder() function
#
# Example:   ///////////////////////////////////////////////
# filename = get_file_from_folder(directory=r"C:\prd-SegundaViaBoleto\Boletos_Downloaded", endswith=".pdf", random_pick=True, filename_or_fullpath="filename")
# >> "boleto.pdf"
#
# filename = get_file_from_folder(directory=r"C:\prd-SegundaViaBoleto\Boletos_Downloaded", exact_name="20200326081620.pdf")
# >> C:\prd-SegundaViaBoleto\Boletos_Downloaded\20200326081620.pdf
#
# filename = get_file_from_folder(directory=r"C:\prd-SegundaViaBoleto\Boletos_Downloaded", exact_name="abcdef.pdf")
# >> False
#
# //////////////////////////////////////////////////////////
def get_file_from_folder(directory,
                         *,
                         filename_or_fullpath="fullpath",
                         exact_name=None,
                         startswith="",
                         name_contains="",
                         endswith="",
                         ignore_ext=False,
                         not_exact_name=None,
                         not_startswith="?",
                         not_name_contains="?",
                         not_endswith="?",
                         random_pick=True,
                         minimum_size_in_kb_check=0,
                         timeout_loop=2,
                         timeout_create_file=20):
    """
    Inputs
        filename_or_fullpath      # str [fullpath, filename] - What should be returned, if file is found
        directory                 # str, path - Directory to loop
        exact_name                # str, list or None - Specify a filename (ex: "boleto.pdf") -- If none, any filename will be considered valid
        startswith                # str - If not exact_name, startswith to compare with filename.startswith()
        name_contains             # str - If not exact_name, contains string to compare with "in filename"
        endswith                  # str - If not exact_name, endswith to compare with filename.endswith()
                                        If criteria is 3 "AND"s chained --> startswith.. AND name_contains.. AND endswith..
                                        But any of the 3 (or all 3, if exact_name!!) are optional
        ignore_ext                # bool - Whether or not the filename extension is considered for the criterias
        not_exact_name            # str or list - Filename(s) with .extension (unless 'ignore_ext' is True) to ignore during comparision
        not_startswith            # str - Invert logic for startswith -- Will ignore files whose names fall in these rules
        not_name_contains         # str - Invert logic for name_conains -- Will ignore files whose names fall in these rules
        not_endswith              # str - Invert logic for endswith -- Will ignore files whose names fall in these rules
                                        These are NOT criterias. A filename wont be a match just because it satifies all three "not_"
                                        Instead, these are act like a black-list (won't match any filename containing these rules)
        random_pick               # bool - Incase of multiple matches, if random pick should be applied
        minimum_size_in_kb_check  # str,int,float - Size in kbytes to consider the found_file valid. Useful for download or unzipping activities.
                                            Can be Timeouted by setting 'timeout_create_file' param
        timeout_loop              # -1,float - Time in seconds to search for a file. Set -1 for infinity.
                                            This func will ALWAYS atleast "loop" the folder once, despite this value
        timeout_create_file       # -1,float - Time in seconds. If file is found but its size isn't valid, timeout wait until
                                            filesize meets minimum_size criteria. -1 means infinite loop/Timer
    Outputs
        str file_found            # Success: Either filename or fullpath of the found file is returned
        False                     # Success: No files were found
        -1                        # Error: Timeout to find a file OR for the file to exists (if minimum_size_in_kb_check)
        -2                        # Error: 'filename_or_fullpath' is invalid. Not str.
        -3                        # Error: 'filename_or_fullpath' is invalid. Not amongst the valid options
        -4                        # Error: 'minimum_size_in_kb_check' is invalid. Can not convert to float.
        -5                        # Error: There are conflicting elements that exists in both 'exact_name' and 'not_exact_name' lists
        -2                        # Error: 'exact_name_no_ext' is invalid. Not bool
    """
    
    # for debugging purposes
    vars_debug = get_passed_parameters(get_file_from_folder, locals())

    # Input Validation & treatment
    try:
        filename_or_fullpath = str(filename_or_fullpath).lower()
    except:
        filelog("get_file_from_folder({}):\nError: filename_or_fullpath is invalid. Not str.".format(vars_debug))
        return -2
    
    if filename_or_fullpath in ["file_name", "filename"]:
        filename_or_fullpath = "filename"
    elif filename_or_fullpath in ["full_path", "fullpath"]:
        filename_or_fullpath = "fullpath"
    else:
        filelog("get_file_from_folder({}):\nError: filename_or_fullpath is invalid. Not amongst the valid options".format(vars_debug))
        return -3
    
    # allow either str or list
    if exact_name is not None:
        exact_name = [exact_name] if isinstance(exact_name, str) else exact_name
    if not_exact_name is not None:
        not_exact_name = [not_exact_name] if isinstance(not_exact_name, str) else not_exact_name

    try:
        minimum_size_in_kb_check = float(minimum_size_in_kb_check)
    except:
        filelog("get_file_from_folder({}):\nError: minimum_size_in_kb_check is invalid. Can not convert to float.".format(vars_debug))
        return -4
    
    if exact_name is not None and not_exact_name is not None:
        intersection = set(exact_name).intersection(not_exact_name)
        if len(intersection) > 0:
            filelog("get_file_from_folder({}):\nError: There are conflicting elements that exists in both 'exact_name' and 'not_exact_name' lists >> {}.".format(vars_debug, intersection))
            return -5

    if ignore_ext not in [True, False]:
        filelog("get_file_from_folder({}):\nError: 'exact_name_ignore_ext' is invalid. Expected either True or False. exact_name_ignore_ext >> {}.".format(vars_debug, ignore_ext))
        return -6

    MINIMUM_SIZE_IN_BYTES = minimum_size_in_kb_check * 1000
    timer_main = Timer(timeout_loop)
    enter_while_atleast_once_despite_timeout = True
    while timer_main.not_expired or enter_while_atleast_once_despite_timeout:
        enter_while_atleast_once_despite_timeout = False
        found_filename = False
        random_filename_list = []
        for filename in os.listdir(directory):
            filename_with_ext = filename # to return later
            if ignore_ext:
                # splitext("something.png") -> ["something", ".png"]
                filename = os.path.splitext(filename)[0]

            # check for blacklist exact_name
            if not_exact_name:
                filename_not_on_blacklist = True
                for prohibited_name in not_exact_name:
                    if filename == prohibited_name:
                        filename_not_on_blacklist = False
                        break

                # ignore this file, go for the next
                if not filename_not_on_blacklist:
                    continue

            if exact_name:
                for name in exact_name:
                    if filename == name:
                        found_filename = filename_with_ext
                        random_filename_list.append(found_filename)
            else:
                # Please understand that if NO criterias are given, it will fall in this category too (will pick any file from the folder)
                if name_contains in filename and filename.startswith(startswith) and filename.endswith(endswith):
                    if not_name_contains not in filename and not filename.startswith(not_startswith) and not filename.endswith(not_endswith):
                        found_filename = filename_with_ext
                        random_filename_list.append(found_filename)

        if random_pick and len(random_filename_list) > 0:
            found_filename = random.choice(random_filename_list)
            
        if found_filename:
            found_filename_full_path = os.path.join(directory, found_filename)
            timer_size_file = Timer(timeout_create_file)
            enter_file_size_check_while_once = True
            while enter_file_size_check_while_once or (timer_main.not_expired and timer_size_file.not_expired):
                enter_file_size_check_while_once = False
                if os.path.getsize(found_filename_full_path) >= MINIMUM_SIZE_IN_BYTES:
                    return found_filename if filename_or_fullpath == "filename" else found_filename_full_path

            filelog("get_file_from_folder({}):\nError: Timeout to find a file OR for the file to exists.".format(vars_debug))
            return -1

        # must have delay, otherwise it lags the PC a bit
        time.sleep(1)
            
    return False


# TimerClass
#
# Example:   ///////////////////////////////////////////////
# timer = Timer(5) # duration = 5
#
# while timer.not_expired:
#     # OR ~~~ while not timer.expired:
#
#         # do stuff
#       if should_reset_timer:
#            timer.reset()
#
#       if something_bad_should_exit_loop:
#            timer.explode() # sets duration to 0
#
#       printer("Timer is at :" + str(timer.at))
#
# //////////////////////////////////////////////////////////
class Timer:
    def __init__(self, duration=10):
        self.duration = float(duration)
        self.start = time.perf_counter()
        # print("The timer has started. Self.start: " + str(self.start))

    def reset(self):
        self.start = time.perf_counter()
        # print("The timer has been reset. Self.start: " + str(self.start))

    def explode(self):
        self.duration = 0
        # print("The timer has been force-expired.")

    def increment(self, increment=0):
        self.duration += increment
        # print("The timer has been incremented by " + str(increment) + " seconds")

    @property
    def not_expired(self):
        # duration == -1 means dev wants a infinite loop/Timer
        if self.duration == -1:
            return True
        return False if time.perf_counter() - self.start > self.duration else True

    @property
    def expired(self):
        return not self.not_expired

    @property
    def at(self):
        # print("The timer is running. Self.at: " + str(time.perf_counter() - self.start))
        return time.perf_counter() - self.start


# Thiago:
# Wrapper do Send, %KEYS% do ahk
# interval = tempo[s] sleep entre os Send, %KEYS%
# pause = tempo[s] sleep ADICIONAL após ultimo Send, %KEYS% (substitui a necessidade de uma linha de time.sleep)
def send_keys(chain_of_keys, *, interval=0.05, pause=0, mode="send"):
    if isinstance(chain_of_keys, (str, int)):
        chain_of_keys = [str(chain_of_keys)]

    for command in chain_of_keys:
        if mode.lower() == "send":
            engine.run_script("Send, " + str(command))
        else:
            # Talvez no futuro implementar SendRaw ou outros? Há a necessidade?
            pass

        time.sleep(interval)

    time.sleep(pause)
    return


# Thiago:
# Realiza comparacao entre duas datas
# Output eh um boolean
# Formatting possivel para os inputs (dia-mes-ano, ano-mes-dia, delimitadores)
# 
# Example:   ///////////////////////////////////////////////
# data1 = "14-11-2019"
# print( compara_data(data1, diff=-15, operator="<", input_delimiter="-") )
# --> True
#
# # Explicação:
# # como não foi fornecido uma data2, data2 = Hoje = "30/11/2019"
# # Altera-se data2 com "diff" e "diff_unit (default=days)" --> -15 dias
# # data2 + (-15dias) --> 15/11/2019
# # if (data1 <operator> data2) ?
# # if ("14/11/2019" < "15/11/2019") ? --> True
#
# //////////////////////////////////////////////////////////
def compara_data(data1, *, data2=None, diff=0, operator=None, diff_unit="d", input_delimiter="/", input_format="dma"):
    
    # valida input
    if not isinstance(data1, str):
        iAmLost("PARAMETRO INCORRETO PARA compara_data(data1, ..).\n" \
            "param 'data1' nao eh uma string de data.")
    if data1.find(input_delimiter) == -1:
        return "<data1 INVALIDA (NAO FOI POSSIVEL LOCALIZAR input_delimiter>"
    
    if data2 is None:
        data2 = datetime.now()
        
    try:
        diff > 0 # tem que ser um float ou int
    except:
        iAmLost("PARAMETRO INCORRETO PARA compara_data(.., data2_or_diff).\n" \
            "param 'data2_or_diff' não eh uma data OU int OU float.")
    
    if not diff_unit in ['d', 'days', 'day']:
        iAmLost("PARAMETRO INCORRETO PARA compara_data(.., operator).\n" \
                "param 'diff_unit' não esta entre os permitidos ['d', 'days', 'day']")
                               
    if not operator in ["==", "=", ">", ">=", "<", "<=", "<>", "!="]:
        iAmLost("PARAMETRO INCORRETO PARA compara_data(.., operator).\n" \
                "param 'operator' não esta entre os permitidos ['==', '=', '>', '>=', '<', '<=', '<>', '!=']")
    
    # lambda para format todos os campos como objeto datetime
    convert_to_datetime = lambda string_date : datetime(*list(map(int, string_date.split(input_delimiter))))
    
    # tratar se estiver fora do formato do datetime
    if input_format in ["dma", "dmy"]:
        tmp = []
        # inverter dia com o ano para cada elemento
        for data in [data1, data2]:
            if isinstance(data, str):
                split = data.split(input_delimiter)
                tmp.append(convert_to_datetime(input_delimiter.join((split[2], split[1], split[0]))))
            else:
                tmp.append(data)
        data1, data2 = tmp
        
        
    elif input_format in ["amd", "ymd"]:
        pass
    else:
        iAmLost("PARAMETRO INCORRETO PARA compara_data(.., input_format). Ver doc.")

    # converter datas para objeto datetime
    # data1, data2 = convert_to_datetime(data1), convert_to_datetime(data2)
    
    # adicionar diff a data2 (se existir)
    if diff is not None:
        if diff_unit in ['d', 'days', 'day']:
           diff_unit = "days"
        
        interval = timedelta(**{diff_unit: diff})
        data2 += interval
                               
    # comparar
    comparision_result = None
    if operator in ["==", "="]:
        comparision_result = data1 == data2
    elif operator == ">":
        comparision_result = data1 > data2
    elif operator == ">=":
        comparision_result = data1 >= data2
    elif operator == "<":
        comparision_result = data1 < data2
    elif operator == "<=":
        comparision_result = data1 <= data2

    
    return comparision_result


# Thiago:
# Localiza a data mais recente OU antiga em um array de strings de datas
# Output eh uma unica data (string)
# Formatting possivel para I/O (dia-mes-ano, ano-mes-dia, delimitadores)
#
# Example:   ///////////////////////////////////////////////
# arr = ['22/03/2013', '15/03/2014', '16/02/2015', '17/05/2016', '18/06/2016', '20/08/2017', '24/10/2019']
# print( computa_data(arr, "recente", output_delimiter="-") )
# --> '24-10-2019'
#
# print( computa_data(arr, "antiga", output_delimiter="/") )
# --> '22/03/2013'
#
# //////////////////////////////////////////////////////////
def computa_data(data_arr, recente_ou_antiga, *, input_delimiter="/", output_delimiter="/", input_format="dma",
                 output_format="dma"):
    # Validar Input
    try:
        iter(data_arr)  # tem que ser iterable
        if isinstance(data_arr, str):  # não pode ser uma string
            raise Exception("data_arr == string")
    except TypeError as te:
        iAmLost("PARAMETRO INCORRETO PARA computa_data(data_arr, ..).\n'data_arr' precisa ser uma list ou iterable.")

    if len(data_arr) == 0:
        return "<SEM DATA>"

    if data_arr[0].find(input_delimiter) == -1:
        return "<SEM DATA (input_delimiter não encontrado)>"

    if not recente_ou_antiga.lower() in ["recente", "antiga"]:
        iAmLost("PARAMETRO INCORRETO PARA computa_data(.., recente_ou_antiga). Ver doc.")

    # lambda para format todos os campos como objeto datetime
    convert_to_datetime = lambda string_date: datetime(*list(map(int, string_date.split(input_delimiter))))

    # tratar se estiver fora do formato do datetime
    if input_format in ["dma", "dmy"]:
        tmp = []
        # inverter dia com o ano para cada elemento
        for data in data_arr:
            split = data.split(input_delimiter)
            tmp.append(input_delimiter.join((split[2], split[1], split[0])))
        data_arr = tmp
    elif input_format in ["amd", "ymd"]:
        pass
    else:
        iAmLost("PARAMETRO INCORRETO PARA computa_data(.., input_format). Ver doc.")

    # converter
    data_arr = list(map(convert_to_datetime, data_arr))
    ref_data = data_arr[0]

    # comparar
    for data in data_arr:
        if recente_ou_antiga == "recente":
            ref_data = data if data > ref_data else ref_data
        elif recente_ou_antiga == "antiga":
            ref_data = data if data < ref_data else ref_data
        else:
            # alguma coisa pro futuro?
            pass

    # formatar output
    if output_format in ["dma", "dmy"]:
        ref_data = ref_data.strftime("%d|||%m|||%Y")
    elif output_format in ["amd", "ymd"]:
        ref_data = ref_data.strftime("%Y|||%m|||%d")
    else:
        iAmLost("PARAMETRO INCORRETO PARA computa_data(.., output_format). Ver doc.")

    # formatar output_delimiter
    ref_data = ref_data.replace("|||", output_delimiter)

    return ref_data


def filelog(append_message=None, hard_disable_print=False):
    file_path = Path(file_log_name).absolute()

    append_message = '<Blank Message>' if append_message == None else append_message
    time_now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    full_string = str(time_now) + ' - ' + str(append_message) + "\n"

    # Se for dentro do jupyter, mandar um print tambem
    if not hard_disable_print and core.isdebug("__main__"):
        print(full_string)

    # caso tenha algum caractere especial, converte-lo, para não dar throw exception.
    try:
        with codecs.open(file_path, 'a+', 'utf-8-sig') as out_file:
            out_file.writelines(full_string)
    except UnicodeEncodeError:
        # tentar novamente, mas usando apenas codigo ascii
        full_string = full_string.encode('ascii', errors='ignore').decode('ascii')
        with codecs.open(file_path, 'a+', 'utf-8-sig') as out_file:
            out_file.writelines(full_string)
    except:
        if core.isdebug("__main__"):
            print('Erro ao gravar FileLog(), file:' + str (file_log_name) + ', mensagem -> ' + str(append_message),)
            # Throw Exception handling no caso do arquivo ter sido recem deletado ou afins
            # por enquanto, fazer nada? Apenas nao irá gravar o log

    return


def msgbox(text=None, *, title="Engine Robo BPA", style="", timeout=0):
    translation_table_ahk_python = {"\n": "`n",
                                    "\r": "`r",
                                    "\t": "`t"}

    try:
        text = str(text)
    except:
        text = "WARNING:\n\nInvalid value for parameter 'text'. Could not convert to string."

    if text is None or text == "":
        translated_text = "Please click on OK to proceed."
    else:
        for python_eq, ahk_eq in translation_table_ahk_python.items():
            text = text.replace(python_eq, ahk_eq)

        skip_next_character = False
        translated_text = ''
        for character in text:
            # se for um escaped character em AHK (no caso, ` crase), skip a traducao deste E do proximo caractere
            if skip_next_character or character == '`':
                # Togle do skip_next_character se ele for True
                skip_next_character = False if skip_next_character is True else skip_next_character

                # Skipar o proximo caractere se o atual for uma crase
                skip_next_character = True if character == '`' else skip_next_character

                # Adicionar a crase ou o caractere especial ao texto
                translated_text += character
                continue

            # Somente traduzir o que estourar a tabela ASC (127), para não exceder o limite de tokens numa expression no AHK
            if ord(character) >= 128:
                translated_text = translated_text + '"Chr(' + str(ord(character)) + ')"'
            else:
                translated_text = translated_text + character

    if timeout == 0:
        translated_text = str(translated_text) + '`n`n`n`n(this PopUp has no timeout)'

    string_param = 'MsgBox, % "' + str(style) + '", % "' + str(title) + '", % "' + translated_text + '", ' + str(timeout)
    engine.run_script(string_param)

    return

    
def get_framework_vars(input_fw_json_file, force=False):
    fw = {}
    if os.path.exists(input_fw_json_file) is False:
        fw['rpa'] = {}
        fw['rpa']['status'] = ""
        fw['rpa']['defaultRoute'] = ""
        fw['rpa']['defaultKey'] = ""
        fw['rpa']['observacao'] = ""
        fw['rpa']['statusMessage'] = ""
        fw['rpa']['dataTable'] = ""
        fw['rpa']['brain'] = []
        fw['rpa']['updateVariable'] = []
        fw['rpa']['multiProducer'] = []
        fw['rpa']['piid'] = ""
        fw['rpa']['processId'] = ""

        with open(input_fw_json_file, "w") as file:
            file.write(json.dumps(fw))
    else:
        with open(input_fw_json_file, "r") as file:
            fw = file.read()
            fw = json.loads(fw)

        # Correção dos objetos nulos entre AHK e Python
        fw['rpa']['brain'] = [] if fw['rpa']['brain'] in ["", [], "[]", "{}", {}] else fw['rpa']['brain']

    return fw
    
def searchDuplicates(searching_key, value, key_name):
    returned_value = False
    framework = get_framework_vars(input_fw_json_file)
    if int(len(framework['rpa'][key_name])) == 0:
        return returned_value

    for dict_key in framework['rpa'][key_name]:
        if dict_key['key'] == searching_key:
            dict_key['value'] = value
            returned_value = True

    update_framework_vars(framework)
    return returned_value


def set_default_route(value):
    filelog("-> DefaultRoute Setada: " + value)
    framework = get_framework_vars(input_fw_json_file)
    framework['rpa']['defaultRoute'] = str(value)
    update_framework_vars(framework)
    return True


def set_default_key(value):
    filelog("-> DefaultKey Setada: " + value)
    framework = get_framework_vars(input_fw_json_file)
    framework['rpa']['defaultKey'] = str(value)
    update_framework_vars(framework)
    return True

def set_obs(value):
    filelog("set_obs: {}".format(value))
    framework = get_framework_vars(input_fw_json_file)
    framework['rpa']['observacao'] = str(value)
    update_framework_vars(framework)
    return True


def setStatusMessage(value):
    framework = get_framework_vars(input_fw_json_file)
    framework['rpa']['statusMessage'] = str(value)
    update_framework_vars(framework)
    return True


# Debug 3 em 1:
#   print (para cmd python)
#   msgbox (para jupyter/fw)
#   filelog (para fins de log)
def ultradebug(string=None, title="UltraDebug", timeout=2):
    if core.isdebug("__main__"):
        print(string)

    if string is not None:
        # para não "loggar" um <Blank Message>
        filelog(string)

    msgbox(string, title=title, timeout=timeout)
    return


def set_var_process(key, value):
    value = str(value)
    framework = get_framework_vars(input_fw_json_file)
    if searchDuplicates(key, value, 'brain'):
        filelog("-> set_var_process: Var '" + str(key) + "' UPDATED AS: " + str(value))
        return True

    else:
        filelog("-> set_var_process: Var '" + str(key) + "' SET AS: " + str(value))
        framework['rpa']['brain'].append(
            {'key': key,
             'value': value,
             'piid': framework['rpa']['piid'],
             'processId': framework['rpa']['processId'],
             'created': dateTime.getTime()})

    update_framework_vars(framework)
    return True


def UpdateVariablesProcess(key, value):
    return searchDuplicates(key, value, 'brain')


def insert_multiproducer(key, value):
    value = str(value)
    if searchDuplicates(key, value, 'multiProducer'):
        return True

    filelog("-> set_var_process: Var '" + str(key) + "' SET AS: " + str(value))
    framework = get_framework_vars(input_fw_json_file)
    framework['rpa']['multiProducer'].append(
        {'key': key, 'value': value, 'piid': framework['rpa']['piid'], 'processId': framework['rpa']['processId'],
         'created': dateTime.getTime()})
    update_framework_vars(framework)
    return True


def UpdateVariablesMultiProducer(key, value):
    return searchDuplicates(key, value, 'multiProducer')


def get_var_process(searching_key, *, dont_cast=False):
    """
    Inputs
        searching_key   # str - The variable name to 'get' from brain/local json
        dont_cast       # bol - Whether this func should attempted to cast the return to int/float.
                                If set to 'false', the return will immediately be the original raw str
    Outputs
        str, int, float # Success: The variable contents (int, float, str depending on 'dont_casxt')
        'NOT FOUND'     # Warning: Variable does not exist yet
    """

    returned_value = "NOT FOUND"
    framework = get_framework_vars(input_fw_json_file)
    
    for dict_key in framework['rpa']['brain']:
        if dict_key['key'] == searching_key:
            returned_value = dict_key['value']

    # se for um int ou float, ja retornar com o cast type, senao retornar a string
    if not dont_cast:
        try:
            # é int
            if round(int(float(returned_value)), 0) == float(returned_value):
                returned_value = int(float(returned_value))
            else:
                # é float
                returned_value = float(returned_value)
        except:
            pass

    filelog("-> get_var_process: Var '" + str(searching_key) + "' GET RETURN: " + str(returned_value))
    return returned_value


class BPAFrameworkError(Exception):
    """Base Exception class for FW Exit Errors"""
    # just incase we want to do something fancy with the throws exceptions in the future
    pass

class IAmBrokedExit(BPAFrameworkError):
    """Raised when iambroked() func is called"""
    pass

class StupidUserExit(BPAFrameworkError):
    """Raised when stupiduser() func is called"""
    pass

class IDontKnowExit(BPAFrameworkError):
    """Raised when idontknow() func is called"""
    pass

class IAmLostExit(BPAFrameworkError):
    """Raised when iamlost() func is called"""
    pass


def iamlost(msg=""):
    ultradebug("iAmLost: " + str(msg))
    framework = get_framework_vars(input_fw_json_file)
    framework['rpa']['status'] = 'iAmLost'
    framework['rpa']['errorMessage'] = msg

    try:
        import trata_erro
        msgbox("Iniciando trata_erro.py", timeout=2)
        time.sleep(5) # dar uma chance a pessoa de fechar o ahk.exe caso queira evitar o trata_erro.py
        try:
            trata_erro.trata_erro(msg)
            trata_erro.trata_erro_sure(msg)
        except TypeError:
            trata_erro.trata_erro()
            trata_erro.trata_erro_sure()
    except ModuleNotFoundError:
        pass

    update_framework_vars(framework)
    write_communication()

    # kill python if not on jupyter
    if not core.isdebug("__main__"):
        os._exit(0)
    else:
        # if on jupyter, just raise an exception
        raise IAmLostExit("Killing Jupyter. Reason: {}".format(msg))


def iAmBroked(msg, error):
    framework = get_framework_vars(input_fw_json_file)
    framework['rpa']['status'] = 'iAmBroked'
    framework['rpa']['errorMessage'] = str(msg)
    framework['rpa']['errorLine'] = str(error.get("line", ""))
    framework['rpa']['errorWhat'] = str(error.get("what", ""))
    framework['rpa']['errorWhere'] = str(error.get("function", ""))

    try:
        import trata_erro
        msgbox("Iniciando trata_erro.py", timeout=2)
        time.sleep(5) # dar uma chance a pessoa de fechar o ahk.exe caso queira evitar o trata_erro.py
        try:
            trata_erro.trata_erro(msg)
            trata_erro.trata_erro_sure(msg)
        except TypeError:
            trata_erro.trata_erro()
            trata_erro.trata_erro_sure()
    except ModuleNotFoundError:
        pass

    update_framework_vars(framework)
    write_communication()

    # kill python if not on jupyter
    if not core.isdebug("__main__"):
        os._exit(0)
    else:
        # if on jupyter, just raise an exception
        raise IAmBrokedExit("Killing Jupyter. Reason: {}".format(msg))


def idontknow(msg):
    ultradebug("-> idontknow called: {}".format(msg))
    framework = get_framework_vars(input_fw_json_file)
    framework['rpa']['status'] = 'iDontKnow'
    framework['rpa']['errorMessage'] = msg

    try:
        import trata_erro
        msgbox("Iniciando trata_erro.py", timeout=2)
        time.sleep(5) # dar uma chance a pessoa de fechar o ahk.exe caso queira evitar o trata_erro.py
        try:
            trata_erro.trata_erro(msg)
            trata_erro.trata_erro_sure(msg)
        except TypeError:
            trata_erro.trata_erro()
            trata_erro.trata_erro_sure()
    except ModuleNotFoundError:
        pass

    update_framework_vars(framework)
    write_communication()

    # kill python if not on jupyter
    if not core.isdebug("__main__"):
        os._exit(0)
    else:
        # if on jupyter, just raise an exception
        raise IDontKnowExit("Killing Jupyter. Reason: {}".format(msg))


def stupidUser(msg):
    ultradebug("-> stupiduser called: {}".format(msg))
    framework = get_framework_vars(input_fw_json_file)
    framework['rpa']['status'] = 'stupidUser'
    framework['rpa']['errorMessage'] = msg

    try:
        import trata_erro
        msgbox("Iniciando trata_erro.py", timeout=2)
        time.sleep(5) # dar uma chance a pessoa de fechar o ahk.exe caso queira evitar o trata_erro.py
        try:
            trata_erro.trata_erro(msg)
            trata_erro.trata_erro_sure(msg)
        except TypeError:
            trata_erro.trata_erro()
            trata_erro.trata_erro_sure()
    except ModuleNotFoundError:
        pass
        
    update_framework_vars(framework)
    write_communication()

    # kill python if not on jupyter
    if not core.isdebug("__main__"):
        os._exit(0)
    else:
        # if on jupyter, just raise an exception
        raise StupidUserExit("Killing Jupyter. Reason: {}".format(msg))


def update_framework_vars(framework):
    try:
        os.remove(input_fw_json_file)
    except FileNotFoundError:
        pass
        
    with open(input_fw_json_file, "w") as file:
        file.write(json.dumps(framework))

    return True

def write_communication():
    framework = get_framework_vars(input_fw_json_file)
    try:
        os.remove(output_fw_json_file)
    except FileNotFoundError:
        pass
        
    with open(output_fw_json_file, "w") as file:
        contents = json.dumps(framework)
        file.write(contents)

    if core.isdebug("__main__"):
        file_move(output_fw_json_file, input_fw_json_file, overwrite=True)

    return True


def start_task(process, payload=None):
    """
    Inputs
        process              # str - 
        body                 # json payload - If None, payload will instead be the current multiproducer var table
    Outputs
        status_code          # int - status code of the request
    """

    # for debugging purposes
    vars_debug = get_passed_parameters(start_task, locals())

    bpm_protocol = get_values_config('CONEXAO', 'bpmProtocol')
    bpm_url = get_values_config('CONEXAO', 'ipBpmProd')
    bpm_port_raw = get_values_config('CONEXAO', 'envBpmPort', warn_on_keyerror=False)
    bpm_port = "" if bpm_port_raw == "ERROR" else f":{bpm_port_raw}"
    url = bpm_protocol + '://' + bpm_url + bpm_port + f'/engine-rest/process-definition/key/{process}/start'

    if payload is None:
        payload = convert_json_bpm('brain', get_values_config('CONTROLE', 'nomeProcesso'))

    # check if proxy exists
    proxy_url = get_values_config('CONEXAO', 'urlProxy', warn_on_keyerror=False)
    if proxy_url == "ERROR":
        proxy_dict = None
    else:
        # see if the proxy has credentials
        proxy_username = get_values_config('CONEXAO', 'userProxy', warn_on_keyerror=False)
        proxy_password = get_values_config('CONEXAO', 'passwordProxy', warn_on_keyerror=False)

        if proxy_username != "ERROR" and proxy_password != "ERROR":
            http_credentials_str = f"{proxy_username}:{proxy_password}@"
        else:
            http_credentials_str = ""

        proxy_dict = {
          'http': f'http://{http_credentials_str}{proxy_url}:3128',
          'https': f'https://{http_credentials_str}{proxy_url}:3128',
        }

    dynamic_token = get_values_config('CONEXAO', 'dinamicToken', warn_on_keyerror=False)
    if dynamic_token is True:
        # Get BPM username, password
        bpm_username = get_values_config('CONTROLE', 'userId')
        bpm_password = get_values_config('CONTROLE', 'passwordId')

        # decrypt if needed
        encrypt = get_values_config('SAFE', 'encrypt', warn_on_keyerror=False)
        if encrypt is True:
            # @TODO@ fazer uma logica para não ter que acessar o BPA_Safe sempre?
            bpm_username = bpa_encrypt(bpm_username, "decrypt")
            bpm_password = bpa_encrypt(bpm_password, "decrypt")

        concat_user_password = f'{bpm_username}:{bpm_password}'
        basic_auth = base64.b64encode(concat_user_password.encode()).decode("utf-8") 
    else:
        basic_auth = get_values_config('CONEXAO', 'bpmBasicAuth')

    headers = {'Content-Type': 'application/json',
               'Authorization': f'Basic {basic_auth}'}

    cb = requests.post(url, data=payload, headers=headers, proxies=proxy_dict, verify=False)

    # status_code 200 is expected when successfully starting a new task
    # return info to user if it fails
    if cb.status_code != 200:
        filelog("start_task({}):\nWarning: status_code != 200\nSee more: {}{}".format(vars_debug, cb.status_code, cb.text))

    return cb.status_code


def start_multi_producer():
    # para inicar uma nova task em outro processo basta chamar a função abaixo:
    #   start_multi_producer()
    #   InsertVariablesMultiProducer(key, value) - para inserir variável para o BPM

    task_name = get_values_config('CONTROLE', 'multiProducerTo')
    var_table = convert_json_bpm('multiProducer', get_values_config('CONTROLE', 'multiProducerTo'))
    return start_task(task_name, var_table)


def convert_json_bpm(key_name, processName):
    framework = get_framework_vars(input_fw_json_file)
    obj_bpm_variables = {}
    obj_bpm_variables['variables'] = {}
    obj_bpm_variables['variables'] = {"autoCompletar": {"type": "String", "value": "false"},
                                      "default_key": {"type": "String", "value": ""},
                                      "default_route": {"type": "String", "value": ""},
                                      "default_where": {"type": "String", "value": ""},
                                      "idLicense": {"type": "String", "value": ""},
                                      "ntt_number": {"type": "String", "value": ""},
                                      "obsLogBanco": {"type": "String", "value": ""},
                                      "process_name": {"type": "String",
                                                       "value": processName},
                                      "status_code": {"type": "String", "value": "0"},
                                      "status_message": {"type": "String", "value": ""}}
    for obj_temp in framework['rpa'][key_name]:
        for data_key in obj_temp.keys():
            obj_bpm_variables['variables'][obj_temp['key']] = {'type': 'String', 'value': obj_temp['value']}

    return json.dumps(obj_bpm_variables)



def bpa_safe_get(title_user, *, username_password_or_both="both"):
    """
    Inputs
        title_user                   # str
        username_password_or_both   # str - What this function should return ("username", "password, "both")
                                        Return is always a list, len() can either be 1 or 2.
    Outputs
        list
        -2                          # Error: key '[SAFE] BPASafe' on config.ini is either invalid or non-existent.
        -3                          # Error: key '[SAFE] dataBase' on config.ini is either invalid or non-existent. 
        -4                          # Error: key '[SAFE] password' on config.ini is either invalid or non-existent. 
        -5                          # Error: key '[SAFE] encrypt' on config.ini is either invalid or non-existent. 
        -6                          # Error: key '[SAFE] bpaDecrypt' on config.ini is either invalid or non-existent. 
        -7                          # Error: Could not find BPASafe scripter.
        -8                          # Error: Invalid BPASafe script. Reason unknown.
        -9                          # Error: Incorrect BPASafe password.
        -10                         # Error: Database not found at path as specified in config.ini.
        -11                         # Error: Invalid command line. Reason unknown.
        -12                         # Error: No credentials were found for 'title_user'.
    """

    # for debugging purposes
    vars_debug = get_passed_parameters(bpa_safe_get, locals())

    BPASafe = get_values_config('SAFE', 'BPASafe')
    
    if BPASafe == "ERROR" or BPASafe == "":
        filelog("bpa_safe_get({}): Error: key '[SAFE] BPASafe' on config.ini is either invalid or non-existent.".format(vars_debug))
        return -2
    else:
        # Ve se ja veio com a ultima barra, senao adiciona-la (evitar erro humano desnecessario)
        BPASafe = BPASafe + "\\" if BPASafe[-1] != "\\" else BPASafe

    dataBase = get_values_config('SAFE', 'dataBase')
    if dataBase == "ERROR":
        filelog("bpa_safe_get({}): Error: key '[SAFE] dataBase' on config.ini is either invalid or non-existent.".format(vars_debug))
        return -3

    password = get_values_config('SAFE', 'password')
    if password == "ERROR":
        filelog("bpa_safe_get({}): Error: key '[SAFE] password' on config.ini is either invalid or non-existent.".format(vars_debug))
        return -4

    encrypt = get_values_config('SAFE', 'encrypt')
    if encrypt == "ERROR":
        filelog("bpa_safe_get({}): Error: key '[SAFE] encrypt' on config.ini is either invalid or non-existent.".format(vars_debug))
        return -5

    bpaDecrypt = get_values_config('SAFE', 'bpaDecrypt')
    if bpaDecrypt == "ERROR":
        filelog("bpa_safe_get({}): Error: key '[SAFE] bpaDecrypt' on config.ini is either invalid or non-existent.".format(vars_debug))
        return -6
    else:
        # Ve se ja veio com a ultima barra, senao adiciona-la (evitar erro humano desnecessario)
        bpaDecrypt = bpaDecrypt + "\\" if bpaDecrypt[-1] != "\\" else bpaDecrypt

    # decryptar, se necessario
    if encrypt is True:
        # chamar o BPAEncrypt.exe no modo "decrypt"
        password = bpa_encrypt(password, "decrypt")

    # Inquire what the dev wants - Username, password or both
    cmd_line_variants = []
    if username_password_or_both == "both":
        cmd_line_variants = ["UserName", "Password"]
    else:
        if "username" in username_password_or_both.lower():
            cmd_line_variants.append("UserName")
        if "password" in username_password_or_both.lower():
            cmd_line_variants.append("Password")

    # Run BPASafe for each required credential
    credentials = []
    for value in cmd_line_variants:
        command = '"' + BPASafe + 'KPScript.exe" -c:GetEntryString "' + dataBase + '" -pw:' + password + ' -Field:' + value + ' -ref-Title:"' + title_user + '"'
        # If user pass a VALID PATH, but windows cant locate BPASafe/KPScript
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result_stdout = result.stdout.decode("utf-8")
            result_stderr = result.stderr.decode("utf-8")
        except FileNotFoundError:
            filelog("bpa_safe_get({}): Error: Could not find BPASafe scripter.".format(vars_debug))
            return -7
        
        # if something returns to result_stderr, an error happened
        if result_stderr != '':
            err =  result_stderr.replace("KeePass", "BPASafe")
            filelog("bpa_safe_get({}): Error: Invalid BPASafe script. Reason unknown. Ask for help. Err >> ".format(vars_debug, err))
            return -8

        # Wrong database password
        if "E: The composite key is invalid!" in result_stdout:
            filelog("bpa_safe_get({}): Error: Incorrect BPASafe password.".format(vars_debug))
            return -9

        # Couldnt locate database
        if "Could not find file " in result_stdout and ".kdbx'" in result_stdout:
            filelog("bpa_safe_get({}): Error: Database not found at path as specified in config.ini.".format(vars_debug))
            return -10

        # If no 'OK: Operation completed successfully'. Something is wrong with cmd line
        if not "OK: Operation completed successfully." in result_stdout:
            filelog("bpa_safe_get({}): Error: Invalid command line. Reason unknown. Ask for help. cmdline >> {}".format(vars_debug, command))
            return -11
        
        # If it returns 'OK: Operation completed successfully.' and nothing else, it means 'titleUser' does not exists in the specified database
        if "OK: Operation completed successfully.\r\n" == result_stdout:
            filelog("bpa_safe_get({}): Error: No credentials were found for 'title_user'.".format(vars_debug))
            return -12
        
        credentials.append(result_stdout.split("\n")[0].replace("\r", ""))
    
    return credentials


def bpa_encrypt(data, mode=None):
    """
    Chama o BPAEncrypt.exe nos paths informados no config.ini (primeiro no path do [SAFE]bpaDecrypt, e se não achar, procura no [SAFE]BPASafe)
    Então executa a tarefa do mode="encrypt"/"decrypt", pasasndo "data" como parametro
    """
    
    # Input treatment & validation
    mode = mode.lower() if isinstance(mode, str) else mode
    if mode is None or mode not in ["encrypt", "decrypt"]:
        msgbox("bpa_encrypt(): ERROR\nParameter 'mode' is invalid (must be either 'encrypt or 'decrypt')")
        return "<bpa_encrypt(): ERROR - Invalid 'mode' parameter>"
    
    data = str(data)

    # Procurar pelo arquivo BPAEncrypt.exe na pasta do "bpaDecrypt" conforme indicado no config.ini
    # Se não localizar, tentar novamente, procurnado-o na pasta do executável do BPASafe
    bpa_encrypt_file_name = "BPAEncrypt.exe"
    found_full_path = None
   
    # If we ever insert BPASafe in a default folder for newer enviroments, just add it to "possible_folders"
    bpa_encrypt_path = get_values_config('SAFE', 'bpaDecrypt')
    bpa_safe_path = get_values_config('SAFE', 'BPASafe')
    possible_folders = [bpa_encrypt_path, bpa_safe_path]
    
    found_path = None
    for possible_path in possible_folders:
        if os.path.exists(possible_path + "\\" + bpa_encrypt_file_name):
            found_path = possible_path
            break
            
    if found_path is None:
        msgbox("Não foi possível localizar o BPAEncrypt.\n\nProcurado nas pastas:\n"
                          + "\n".join(possible_folders) +
                          "\n\n\nEm caso de dúvidas, conversar com o coleguinha")
        return "<bpa_encrypt(): ERROR - BPAEncrypt.exe not found>"


    dest_file_name = "tmp_bpa_safe.txt"
    dir_save_file = os.path.join(os.getcwd(), dest_file_name)
    secret_key = "AZXwlrth4b4aBBlTHm5/IDS42MeiFKoo74hijTqXWPo="
    
    if mode == "encrypt":
        command = [bpa_encrypt_file_name, data, dir_save_file]
    elif mode == "decrypt":
        command = [bpa_encrypt_file_name, secret_key, data, dir_save_file]
    else:
        msgbox("bpa_encrypt(): ERROR\nParameter 'mode' is invalid (NOT YET MAPPED)")
        return "<bpa_encrypt(): ERROR - Invalid 'mode' parameter>"
    
    if (os.path.exists(dest_file_name)):
        os.remove(dest_file_name)
    
    # Paramter 'cwd' is a must
    # The way BPAEncrypt was made, it can only be run (on cmdline) when its pointing to its own folder
    FLAG_CREATE_NO_WINDOW = 0x08000000
    result = subprocess.run(command, creationflags=FLAG_CREATE_NO_WINDOW, cwd=found_path, shell=True)

    str_read_file = "<bpa_encrypt(): UNKNOWN ERROR - TEMP FILE WAS NOT CREATED>"
    if (os.path.exists(dest_file_name)):
        with open(dest_file_name, 'r') as file_read_str:
            str_read_file = file_read_str.read().replace("\n", "")
        os.remove(dest_file_name)
            
    return str_read_file

############################################################################
# function that helps with trackability / debugging on the filelog 
# 
# Example:
#
# vars_debug = get_passed_parameters(delete_file_sure, locals())
# filelog("delete_file_sure({}): Error: 'file_path' is invalid. Is not str or path".format(vars_debug))
#
# >> 2020/03/28 04:41:10 - file_delete(file_path='C:\prd-SegundaViaBoleto\Processando-RoboSegundaViaBoleto\process_info_memory', safe_extension_check='', timeout=5):
# Error: 'file_path' is invalid. Path does not contain an extension
#
# TODO : Maybe someday create a @decorator and make this function to be called automatically when a fw lib function is called?
############################################################################
def get_passed_parameters(func_name, local_dict, *, log_func_call=True):
    '''
    Inputs
        func_name         # func - The function itself. NOT A STRING
        local_dict        # dict - The locals() dictionary as within the function
        log_func_call     # bool - Whether this function should annonce on filelog when 'func_name' is called.
                                   Set to False to disable a function that is called repeatedly
    Outputs
        string            # A properly formatted string containing all the parameters (that differs from default values) passed to the func and its values
    '''
    
    # Build a dictionary where keys are from "co_varnames" and values are from either "func.__defaults__" or "func.__kwdefaults__"
    # Example:
    #         func(a, b=2, c=3, *, d=4)
    #           co_varnames = ["a", "b", "c"]
    #     func.__defaults__ = (2,3)      << __defaults__ show only positional args.
    #                                       Only "b" has a default value
    #                                       we can safely assume that 2 belongs to "b" var and no "a", because b is
    #                                       a named argument and the only way to declare a named argument is at the right side
    #                                       of positional non-named args
    #   func.__kwdefaults__ = {'d' : 4}  << __kwdefaults__ is a dict and nicely shows the var_name, var_value
    #
    #   algorithm logic is as follows:
    #         1. get the var names from co_varnames
    #         2. build them into a dict, default value for each key can be None
    #         3. __kwdefaults__ are easy, they are already paired - simple copy the values if keys match
    #         4. for each key from __kwdefaults__, mark the key in the new dict as "visited"
    #         5. for __defaults__, in the new dict get the position of the 1st element "visited"
    #                   (that is, the first element that was given a value from kwdefaults)
    #                   and then populate the rest of the list backwards, marking each key as visited as well
    #         6. Repeat 5 until the __defaults__ is through 
    #
    #         1. str a,b,c,d
    #         2. dict = {"a": None, "b": None, "c": None, "d": None}
    #         3. dict = {"a": None, "b": None, "c": None, "d": 4}
    #         4  visited_list = ["d"]
    #         5. first visited key is 'd', and we have the tuple (2, 3) from __defaults__,
    #                   and we shall populate the remaining of the dict backwards
    #                   starting from the left of the 1st visited element
    #
    #         6.
    # 1st iteration    tuple = (2, 3)       dict = {"a": None, "b": None, "c": None, "d": 4}      visited_list = ["d"]
    #                              ^    >>  dict = {"a": None, "b": None, "c": 3, "d": 4}         visited_list = ["d", "c"]
    #
    # 2nd iteration    tuple = (2, 3)       dict = {"a": None, "b": None, "c": None, "d": 4}      visited_list = ["d", "c"]
    #                           ^       >>  dict = {"a": None, "b": 2, "c": 3, "d": 4}            visited_list = ["d", "c", "b"]
    #
    # no 3rd iteration, tuple is over, same thinking as len(visited_list) == len(__kwdefaults__) + len(__defaults__)
    
    # do a log
    if log_func_call:
        filelog(" [[ {} ]]".format(func_name.__name__))
    
    defaults = func_name.__defaults__
    kwdefaults = func_name.__kwdefaults__
    co_varnames = func_name.__code__.co_varnames
    
    # step 1 & 2
    default_values_dict = {}
    for var_name in co_varnames:
        default_values_dict[var_name] = None
        
    # step 3 & 4
    visited_list = []
    if kwdefaults is not None:
        for key in kwdefaults.keys():
            default_values_dict[key] = kwdefaults[key]
            visited_list.append(key)
            
    # step 5
    if defaults is not None:
        not_visited_yet = []
        for element in default_values_dict:
            if element not in visited_list:
                not_visited_yet.append(element)  # a b c
                
        # give them a value
        for value in defaults[::-1]:
            key_that_will_receive_value = not_visited_yet[-1]
            not_visited_yet.remove(key_that_will_receive_value)
            default_values_dict[key_that_will_receive_value] = value
        
    string = ""
    for key in default_values_dict.keys():
        # if an arg exists in the locals() scope
        if key in local_dict:
            # if its value is different than default (to make string less spammy)
            local_scope_value = local_dict[key]
            if default_values_dict[key] != local_scope_value:
                if isinstance(local_scope_value, str):
                    # For legibility when value is an string
                    local_scope_value = "'{}'".format(local_scope_value)
                    
                # limit the var value to 100 characters, just in very case
                local_scope_value = str(local_scope_value)[:100]
                string += key + "=" + local_scope_value + ", "
    
    # Remove the last ", ""
    if string != "":
        string = string[:-2]

    return string
    

def write_json(path, contents, *, increment_keys=False, overwrite_keys=False, double_check=True, timeout_doublecheck=20):
    """
    Inputs
        path               # str, path - Relative or Absolute full path destination file
        contents           # str, dict, list - This function will always try to write the contents as an json object
                                    Incase a decode error is raised, raw text will be written.
        double_check       # boolean - Function will test itself after each write (redudancy)
                                    Disable if dealing with EXTREMELY HUGE files
    Outputs
        str or dict        # Success: Returning what was written into the file
        -1                 # Error: Timed-out during double check.
        -2                 # Error: 'path' is invalid. Not str or path.
    """

    # for debugging purposes
    vars_debug = get_passed_parameters(write_json, locals())
    try:
        path = str(path)
    except:
        filelog("write_json({}): Error: 'path' is invalid. Not str or path.".format(vars_debug))
        return -2

    # If the user wants to increment keys instead of replacing the whole file
    if increment_keys:
        if os.path.isfile(path):
            with open(path, 'r') as f:
                file_content_str = f.read()
                dict_json = json.loads(file_content_str)

            for key in dict_json.keys():
                if overwrite_keys or contents.get(key, None) is None:
                    contents[key] = dict_json[key]

    with open(path, 'w') as f:
        str_to_write = contents
        try:
            str_to_write = json.dumps(contents)
        except json.JSONDecodeError:
            filelog("write_json({}): Warning: Could not write a valid json due to decode error, file created with raw text.".format(vars_debug))
        f.write(str_to_write)

    if not double_check:
        return str_to_write

    timer = Timer(timeout_doublecheck)
    while timer.not_expired:
        with open(path, 'r') as f:
            file_contents = f.read()
            if file_contents == str_to_write:
                return str_to_write

    filelog("write_json({}): Error: Timed-out during double check.".format(vars_debug))
    return -1

    

def read_json(path, *, raw_text=False):
    """
    Inputs
        path               # str, path - Relative or Absolute full path to text file (can be any "readable" extension)
        raw_text           # bool - Whether the return should be a dictionary or raw_text
    Outputs
        dict (can be "")   # Success: Contents of the file, converted into a dictonary. Empty string means file was empty.
        -2                 # Error: 'path' is invalid. Not str or path.
        -3                 # Warning: 'path' does not lead to any file.
        -4                 # Error: file found is not "readable".
        -5                 # Error: file found, but its contents does not parse to a valid json.
    """
    
    # for debugging purposes
    vars_debug = get_passed_parameters(read_json, locals())

    try:
        path = str(path)
    except:
        filelog("read_json({}): Error: 'path' is invalid. Not str or path.".format(vars_debug))
        return -2
    
    try:
        with open(path, 'r') as f:
            string_content = f.read()
            if string_content == "":
                return string_content
            
            if raw_text:
                contents = string_content
            else:
                contents = json.loads(string_content)
    except FileNotFoundError:
        filelog("read_json({}): Warning: 'path' does not lead to any file.".format(vars_debug))
        return -3
    except UnicodeDecodeError:
        filelog("read_json({}): Error: file found is not 'readable'.".format(vars_debug))
        return -4
    except json.JSONDecodeError:
        filelog("read_json({}): Error: file found, but its contents does not parse to a valid json.".format(vars_debug))
        return -5  
    
    return contents


def file_delete(file_path, *, safe_extension_check="", timeout=5):
    """
    Inputs
        file_path              # str, path - Path leading to the memory .json file
        safe_extension_check   # str - (optional) The extension for double check, just to make sure a file isn't wrongly deleted
    Outputs
        True                   # Success: Memory file deleted (or didn't exist in first place)
        -1                     # Error: Timeout while trying to delete file (shouldnt happen, but hey)
        -2                     # Error: 'file_path' is invalid. Is not str or path
        -3                     # Error: 'safe_extension_check' is Is not str or path
        -4                     # Error: 'file_path' is invalid. Path does not contain an extension
    """
    
    # for debugging purposes
    vars_debug = get_passed_parameters(file_delete, locals())

    # Validate input
    try:
        file_path = str(file_path)
    except:
        filelog("delete_file_sure({}): Error: 'file_path' is invalid. Is not str or path".format(vars_debug))
        return -2
    
    # input treatment
    try:
        safe_extension_check = str(safe_extension_check).replace(".", "")
    except:
        filelog("delete_file_sure({}): 'safe_extension_check' is Is not str or path".format(vars_debug))
        return -3
    
    if safe_extension_check != "":
        if not file_path.endswith("." + safe_extension_check):
            # Maybe the user forgot to end it with .json?...
            new_path = file_path + "." + safe_extension_check
            if os.path.exists(new_path):
                file_path = new_path
            else:
                filelog("delete_file_sure({}): Error: 'file_path' is invalid. Path does not contain an extension".format(vars_debug))
                return -4
        
    timer = Timer(timeout)
    while timer.not_expired:
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            return True
    
    filelog("delete_file_sure({}): Error: Timeout while trying to delete file".format(str(locals())))
    return -1


def file_move(path_from, path_to, *, overwrite=False, attach_suffix_if_overwite=True, minimum_size_in_kb_check=0, timeout=30):
    """
    Moves a file from 'path_from' to 'path_to' with some plus-es
     -> Creates folders 'path_to', recursively, if they dont exist
     -> If 'path_to' is a folder, it will move the file keeping its original name and extension
     -> Can move files between diferent devices/disks
     -> Can figure out the extension of the 'path_from' file, if it is not passed on parameter
     -> Timeout / check for corrupted files (size = 0kb)
     
    Inputs
        path_from                 # str, path - Relative or absolute full path to a file (may ommit extension) 
        path_from                 # str, path - Folder to move the file into or filename (if rename is desired) of destination
        overwrite                 # bool - Whether this function should return an error OR just overwrite in case of path_to
                                        already leads to an existing file
        attach_suffix_if_overwite # bool - True to attach a number suffix (ie: Boleto(1).pdf) if path_to already points to a file
        minimum_size_in_kb_check  # str,int,float - Size in kbytes to consider the newly moved file valid.
                                        Useful to check for corrupted files, etc
                                        Can be Timeouted by setting 'timeout' param
        timeout                   # -1,float - Time in seconds. If file exists but its size isn't valid, timeout
                                        wait until filesize meets the minimum_size criteria. -1 means infinite loop/Timer
    Outputs
        str treated path_to # Success: A treated (full path, with extension) path_to string pointing where the file is now
        -1                  # Error: Timeout during file_move.
        -2                  # Error: 'path_from' does not lead to a file
        -3                  # Error: 'path_from' is invalid. Could not locate a file. Consider specifying a file extension!
        -4                  # Error: 'path_from' is invalid. Function call to get_file_from_folder() failed
        -5                  # Error: 'path_from' is invalid. Unknown error. See lib.py and debug or ask for help
        -6                  # Error: 'path_to' is ambiguous. Do you want to create a few folder and move
                                    OR want move/rename an existing file?
                                    Modify 'path_to' to include "\" at end if new folder or include .ext if rename/move
        -7                  # Error: Can not create the desired folder as specified in 'path_to' because
                                    a file without extension with the same name already exists on the same root folder
        -8                  # Warning: No errors, but file wasn't moved because 'path_from' and 'path_to' are the same
        -9                  # Warning: Moving/renaming the file to 'path_to' would result in an overwrite.
                                    Please use 'overwrite=True' or 'attach_suffix_if_overwite=True' to move it anyway
        -10                 # Error: Invalid combination of 'overwrite' and 'attach_suffix_if_overwite' parameters
    """

    # for debugging purposes
    vars_debug = get_passed_parameters(file_move, locals())
    
    # Input validation & treatment

    # Does the path_from have ext? if no, look for a file with the same name in the same folder
    full_path_filename_with_ext = path_from
    folder, filename_from = os.path.split(path_from)
    path_from_has_ext = os.path.splitext(path_from)[1] != ""
    if not path_from_has_ext:
        # search for the likely filename using get_file_from_folder(), hey! finally some use
        # IF MULTIPLE EXISTS, IT IS UNDEFINED WHICH ONE WILL BE CHOSEN
        # TODO: Return error if multiple matches?
        full_path_filename_with_ext = get_file_from_folder(directory=folder,
                                                           ignore_ext=True,
                                                           exact_name=filename_from,
                                                           timeout_loop=0)
        
        if full_path_filename_with_ext is False:
            # couldnt locate files
            filelog("path_from({}):\nError: 'path_from' is invalid. Could not locate a file. Consider specifying a file extension!".format(vars_debug))
            return -3
        elif isinstance(full_path_filename_with_ext, int):
            filelog("path_from({}):\nError: 'path_from' is invalid. Function call to get_file_from_folder() failed.".format(vars_debug))
            return -4
        elif isinstance(full_path_filename_with_ext, str):
            # all good, found file
            pass
        else:
            # unknown error
            filelog("path_from({}):\nError: 'path_from' is invalid. Unknown error. See lib.py and debug or ask for help.".format(vars_debug))
            return -5

    if not os.path.isfile(full_path_filename_with_ext):
        # couldnt locate files
        filelog("path_from({}):\nError: 'path_from' does not lead to a file.".format(vars_debug))
        return -2
    
    # With path_from fully treated, save "full_path", "filename with ext", "filename without ext", "ext" and 
    treated_path_from_full_path = full_path_filename_with_ext
    treated_path_from_filename_with_ext = os.path.split(full_path_filename_with_ext)[1]
    treated_path_from_filename_without_ext, treated_path_from_ext = os.path.splitext(treated_path_from_filename_with_ext)
        
    # Is path_to a file (rename/simple move) or a folder?
    # It can be ambiguous, therefore some testings are done
    # Rename/simple move:
    #    test  1. path_to ends with an extension (________________.pdf)
    #          2. path_from has no ext ... split filename of path_to is == split filename of path_from
    # Folder:
    #          3. Folder has to already exists (os.path.isdir() is True)
    #          4. path_to ends with a \ (_______________\somefolder\)
    # Else: return -3 : Ambiguous

    folder_or_rename = None
    split_to = os.path.splitext(path_to)
    if split_to[1] != "":
        # test 1
        folder_or_rename = "rename"
    elif not path_from_has_ext and filename_from == split_to[0]:
        # test 2
        folder_or_rename = "rename"
    elif os.path.isdir(path_to):
        # test 3
        folder_or_rename = "folder"
    elif path_to.endswith("\\"):
        # test 4
        folder_or_rename = "folder"
    else:
        # is ambiguous what the user wants
        filelog(("path_from({}):\nError: 'path_to' is ambiguous. Do you want to create a few folder and move" + \
                "OR want move/rename an existing file? Modify 'path_to' to include '\\' at end if new folder" + \
                "or include .ext if rename/move").format(vars_debug))
        return -6
    
    if folder_or_rename == "folder":
        if not os.path.isdir(path_to):
            try:
                os.makedirs(path_to)
            except FileExistsError:
                filelog("path_from({}):\nError: Can not create the desired folder as specified in 'path_to' because a file without extension with the same name already exists on the same root folder.".format(vars_debug))
                return -7
        
        # use the same file name + ext of treated path_from
        treated_path_to = os.path.join(path_to, treated_path_from_filename_without_ext + treated_path_from_ext)
    elif folder_or_rename == "rename":
        treated_path_to = path_to
        
        # does it have extension? if not, include it
        path_to_has_ext = os.path.splitext(path_to)[1] != ""
        if not path_to_has_ext:
            treated_path_to += treated_path_from_ext
    
    if treated_path_from_full_path == treated_path_to:
        # return a warning because very likely that is not what the developer wanted to happen
        filelog("path_from({}):\nWarning: No errors, but file wasn't moved because 'path_from' and 'path_to' are the same".format(vars_debug))
        return -8
    
    # Check for possible overwrite
    if os.path.isfile(treated_path_to):
        if overwrite is False and attach_suffix_if_overwite is False:
            filelog("path_from({}):\nWarning: Moving/renaming the file to 'path_to' would result in an overwrite. Please use 'overwrite=True' or 'attach_suffix_if_overwite=True'".format(vars_debug))
            return -9
        elif overwrite is True:
            pass
        elif overwrite is False and attach_suffix_if_overwite is True:

            # get driver, folder
            path_to_folder = os.path.split(treated_path_to)[0]
            # get filename and ext
            path_to_filename, path_to_ext = os.path.splitext(treated_path_to)

            # build a new (hopefully) unique name
            c = 1
            while c == 1 or os.path.isfile(new_name):
                suffix = " ({})".format(c)
                new_name = os.path.join(path_to_folder, path_to_filename + suffix + treated_path_from_ext)
                c += 1

            treated_path_to = new_name
        else:
            filelog("path_from({}):\nError: Invalid combination of 'overwrite' and 'attach_suffix_if_overwite' parameters".format(vars_debug))
            return -10

    shutil.move(treated_path_from_full_path, treated_path_to)
    
    # Very likely shutil has already some redundancy on it but it doesnt hurt to double check if the file exists
    MINIMUM_SIZE_IN_BYTES = minimum_size_in_kb_check * 1000
    timer = Timer(timeout)
    while timer.not_expired:
        if os.path.exists(treated_path_to) and os.path.isfile(treated_path_to):
            if os.path.getsize(treated_path_to) >= MINIMUM_SIZE_IN_BYTES:
                return treated_path_to
        
    return -1

# se rodar no Jupyter, da KeyError - então assumir 'training'
try:
    race_mode = config['CONTROLE']['raceMode'].lower()
except KeyError:
    race_mode = "training"

# Input Framework > bpatech.txt (se rodando via BPA.exe) ou training_vars (rodando via Jupyter)
# Output Framework > BPAexePythonRet.txt
output_fw_json_file = 'BPAexePythonRet.txt'
if core.isdebug("__main__") or race_mode in ["training", "trainning"]:
    input_fw_json_file = 'training_vars.txt'
    file_log_name = "BPA_FileLog.txt"
else:
    input_fw_json_file = 'bpatech.txt'
    file_log_name = get_values_config('CONTROLE', 'baseLogDir') + "\log_" + get_values_config('CONTROLE',
                    'nomeProcesso') + '_' + f"{datetime.now().day:02d}" + f"{datetime.now().month:02d}" + str(datetime.now().year) + ".txt"

############################################################################
# Pieces: Testando hotkey para stop/pause
if __name__ != "__main__":
    l = [frame.filename for frame in inspect.stack()[:] if not "<" in frame.filename]
    first_caller = l[-1]

    IGNORE_LIST = ["nosetests-script"]

    should_hotkey = True
    for ignore_caller in IGNORE_LIST:
        if ignore_caller in first_caller:
            should_hotkey = False

    if should_hotkey:
        from system_hotkey import SystemHotkey

        def exit_python_by_hk(self, event, hotkey, args=[]):
            ultradebug("User pressed '{}'. Exiting Python.".format(str(hotkey)))
            os._exit(0)

        hk_kill_robo = get_values_config("CONTROLE", "KillRobo", warn_on_keyerror=False)
        hk_kill_robo = 'f10' if hk_kill_robo == "ERROR" else hk_kill_robo

        try:
            hk = SystemHotkey(consumer=exit_python_by_hk)
            hk.register([hk_kill_robo])
        except SystemRegisterError:
            # Hotkey is in use for another python/software on this computer.
            # Right now, we can simply ignore this exception
            pass

############################################################################


################ ALL DEPRECATED FUNCTIONS SHOULD GO HERE
# If the reason for deprecation is due naming conventions, it is ok to not specify explicitly, but otherwise please do it
#
#

def GetValuesConfig(session, key):
    filelog("func 'GetValuesConfig()' is deprecated! Please use 'get_values_config()' instead.")
    return get_values_config(session, key)

def setDefaultRoute(value):
    filelog("func 'setDefaultRoute()' is deprecated! Please use 'set_default_route()' instead.")
    return set_default_route(value)

def setDefaultKey(value):
    filelog("func 'setDefaultKey()' is deprecated! Please use 'set_default_key()' instead.")
    return set_default_key(value)

def setObservacao(value):
    filelog("func 'setObservacao()' is deprecated! Please use 'set_obs()' instead.")
    return bool(1)

# Setting a standart >>(get/set), singular (variable, process) & snake_case
def InsertVariablesProcess(key, value):
    filelog("func 'InsertVariablesProcess()' is deprecated! Please use 'set_var_process()' instead.")
    value = str(value)
    return set_var_process(key, value)

# Setting a standart >>(get/set), singular (variable, process) & snake_case
def GetVariableValueProcess(searching_key):
    filelog("func 'GetVariableValueProcess()' is deprecated! Please use 'get_var_process()' instead.")
    return get_var_process(searching_key)

def iDontKnow(msg):
    # DEPRECATED GetValuesConfig(), usar get_values_config()
    filelog("func 'iDontKnow()' is deprecated! Please use 'idontknow()' instead.")
    return idontknow(msg)

def iAmLost(msg=""):
    return iamlost(msg)

def writeComunication():
    filelog("func 'writeComunication()' is deprecated! Please use 'write_communication()' instead.")
    return write_communication()

def InsertVariablesMultiProducer(key, value):
    filelog("func 'InsertVariablesMultiProducer()' is deprecated! Please use 'insert_multiproducer()' instead.")
    return write_communication()