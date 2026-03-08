Это следующая инкарнация web-приложения для [сайта](https://sphnx.ru/)
текстовых блогов.

Порядок запуска приложения в Debian testing/sid:

```
$ mkdir ~/workspace
$ cd ~/workspace
$ git clone git@github.com:jazz4web/webjournal.get
$ cd webjournal
$ sudo apt install $(cat deployment/packages)
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ tar xvaf deployment/vendor.tar.gz -C webapp/static
$ cp env_template .env
$ mkdir webapp/static/generic
$ python create_root.py
$ python runserver.py
```

Если всё сделали правильно, тест в браузере по адресу localhost:8000 покажет
стартовую страницу в текущей стадии разработки.
