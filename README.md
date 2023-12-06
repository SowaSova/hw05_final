# hw05_final

[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)

# Проект социальной сети YATUBE
Социальная сеть блогеров с возможностью создавать посты, оставлять комментарии к ним и подписываться на понравившихся авторов.

### Технологии
- Python 3.7
- Django 2.2.16

### Запуск проекта в dev-режиме
- Склонировать репозиторий и перейти в него
```sh
git clone git@github.com:SowaSova/yatube.git
```
- Установка и запуск виртуального окружения
```sh
python -m venv venv
```
- Установка из файла requirements.txt
```sh
pip install -r requirements.txt
```
- Перейти в папку с именем проекта `yatube`
```sh
cd yatube/
```
- Провести миграции
```sh
python manage.py migrate
```
- Активировать сервер
```sh
python manage.py runserver
```
