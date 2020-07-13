:: Creating folder, if necessary
mkdir test_xml_jenkins_for_prd 2>nul

:: Deleting previous results"
del /q /f test_xml_jenkins_for_prd\*.xml 2>nul

:: Start Route1-20200713221605
nosetests --with-xunit -v --xunit-file=test_xml_jenkins_for_prd\BPATEST-prepara_ambiente-Route1-20200713221605.xml prepara_ambiente.py
nosetests --with-xunit -v --xunit-file=test_xml_jenkins_for_prd\BPATEST-pesquisaitem-Route1-20200713221605.xml pesquisaitem.py
nosetests --with-xunit -v --xunit-file=test_xml_jenkins_for_prd\BPATEST-entrardacte-Route1-20200713221605.xml entrardacte.py
nosetests --with-xunit -v --xunit-file=test_xml_jenkins_for_prd\BPATEST-finalizadocomsucesso-Route1-20200713221605.xml finalizadocomsucesso.py
nosetests --with-xunit -v --xunit-file=test_xml_jenkins_for_prd\BPATEST-finalizadosemsucesso-Route1-20200713221605.xml finalizadosemsucesso.py
nosetests --with-xunit -v --xunit-file=test_xml_jenkins_for_prd\BPATEST-emailfinalizado-Route1-20200713221605.xml emailfinalizado.py
:: End Route1-20200713221605


pause
