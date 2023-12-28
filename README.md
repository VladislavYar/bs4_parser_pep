## Парсер документации Python
### Проект представляет собой парсер:
- статусов PEP
- автора, заголовка и ссылки на статьи в разделах 'What’s New in Python'
- ссылки на документацию, версии и статусы Python
- ссылки на документацию актуальной версии с последующем её скачиванием    
    
Так же имеется возможность вывода данных поиска в виде таблицы(или построчно) в консоль и файл формата CSV.    
    
### Команды:
```
usage: main.py [-h] [-c] [-o {pretty,file}]
               {whats-new,latest-versions,download}

Парсер документации Python

positional arguments:
  {whats-new,latest-versions,download,pep}
                        Режимы работы парсера

optional arguments:
  -h, --help            show this help message and exit
  -c, --clear-cache     Очистка кеша
  -o {pretty,file}, --output {pretty,file}
                        Дополнительные способы вывода данных
```

## Cтек проекта
Python v3.9, BeautifulSoup4
