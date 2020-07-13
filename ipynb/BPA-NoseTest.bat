:: Creating folder, if necessary
mkdir test_xml_jenkins 2>nul

:: Deleting previous results"
del /q /f test_xml_jenkins\*.xml 2>nul

:: Start Route1-20200625210905
nosetests --with-xunit -v --xunit-file=test_xml_jenkins\BPATEST-pesquisaitem-Route1-20200625210905.xml pesquisaitem.py
:: End Route1-20200625210905


pause
