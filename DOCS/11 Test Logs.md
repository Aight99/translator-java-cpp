<!--
Провести тестирование проекта и на его основе создать документ Test Logs. 
На основе непройденных тестов создать перечень задач для исправления найденных ошибок например, 
дополнить документ Code Issue List. Документы разместить в репозитории.
-->

# Тестирование проекта

## Тесты для подсистемы «Пользовательский интерфейс»

Тест TEST_UI_001
	
	Тестируемые требования: REQ_UI_001
Описание теста…

Тестируемая версия продукта: номер версии из GitHub
Ожидаемый результат: Показано 5 опций меню
Видимый результат: Показано 5 опций меню
Резюме: Тест пройден


Тест TEST_UI_002
	
	Тестируемые требования: REQ_UI_002
	Описание теста…
	
Тестируемая версия продукта: номер версии из GitHub
Ожидаемый результат: Показано 2 всплывающих окна
Видимый результат: Показано 1 всплывающее окно
Резюме: Тест НЕ пройден


## Тесты для подсистемы «Модуль синтаксического анализа»

Тест TEST_SY_001

    Тестируемые требования: SY_001
    Проверка работоспособности подсистемы на работу с основными арифметическими операциями. На вход подаётся файл с кодом, в котором создаются две переменные типа int: а = 5 и b = 2. Далее они используются в формуле (3 + (a - 1)) * b / 2.

    Тестируемая версия продукта: 1.0.1
    Ожидаемый результат: Дерево разбора
    Видимый результат: Дерево разбора
    Резюме: Тест пройден

Тест TEST_SY_002

    Тестируемые требования: SY_001
    Проверка работоспособности подсистемы на работу с несколькими пользовательскими методами. На вход подаётся файл с кодом, в котором объявлены два метода: до метода main и после него.
    
    Тестируемая версия продукта: 1.0.1
    Ожидаемый результат: Дерево разбора
    Видимый результат: Сообщение о синтаксической ошибке в строке 15
    Резюме: Тест не пройден

Тест TEST_SY_003

    Тестируемые требования: SY_002
    Проверка корректности сообщения при ошибке с недостающей точкой с запятой. На вход подаётся файл, в котором не хватает точки с запятой на 6 строке.
    
    Тестируемая версия продукта: 1.0.1
    Ожидаемый результат: Сообщение о синтаксической ошибке в строке 7
    Видимый результат: Сообщение о синтаксической ошибке в строке 7
    Резюме: Тест пройден

Тест TEST_SY_004

    Тестируемые требования: SY_002
    Проверка корректности сообщения при ошибке с отсутствующей в грамматике конструкцией языка. На вход подаётся файл, в котором не хватает скобок в блоке условного оператора в 4 строке.
    
    Тестируемая версия продукта: 1.0.1
    Ожидаемый результат: Сообщение о синтаксической ошибке в строке 4
    Видимый результат: Сообщение о синтаксической ошиб