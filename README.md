***webjournal*** - это web-приложение для развёртывания сайта текстовых блогов на собственном домене.
В приложении уже реализованы следующие функциональные возможности:

* авторизация пользователей и самостоятельная регистрация аккаунта;
* дифференциация пользователей по группам;
* профиль пользователя и самостоятельное обслуживание аккаунта
(смена пароля, смена e-mail, смена аватара etc.);
* сервис коротких ссылок;
* хостинг картинок;
* инструменты администратора.

Остальной функционал пока в стадии активной разработки.

Порядок запуска приложения в Debian testing/sid:

```
$ mkdir ~/workspace
$ cd ~/workspace
$ git clone git@github.com:jazz4web/webjournal.get
$ cd webjournal
$ sudo apt install $(cat deployment/packages)
$ createdb webjournal
$ psql -d webjournal -f sql/db.sql
$ python3.14 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ tar xvaf deployment/vendor.tar.gz -C webapp/static
$ tar xvaf deployment/images.tar.gz -C webapp/static
$ cp env_template .env
$ ln -s -T ~/workspace/webjournal/webapp/static/vendor/bootstrap/fonts/ webapp/static/fonts
$ python insert_captchas.py
$ python create_root.py
$ python runserver.py
```

Если всё сделали правильно, тест в браузере по адресу **localhost:8000** покажет
стартовую страницу в текущей стадии разработки. Снимки, как ключевые страницы приложения выглядят у меня 
в окне браузера, можно посмотреть в каталоге *screenshots*. Оценить скорость отклика
будущего сайта может каждый желающий. Демонстрационный сайт вероятно будет развёрнут чуть позже
по мере набора критически важных и ключевых возможностей приложения.

***Важно:** webjournal не является коммерческим проектом и распространяется открытым исходным кодом, помочь автору своим безвозмездным и благородным донатом можно по следующим реквизитам...*

1. Российская карта МИР: 2200 2418 7543 1078
2. [Кошелёк yoomoney](https://yoomoney.ru/to/410015590807463)
