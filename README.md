Это следующая инкарнация web-приложения для сайта текстовых блогов.

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
$ cp env_template .env
$ ln -s -T ~/workspace/webjournal/webapp/static/vendor/bootstrap/fonts/ webapp/static/fonts
$ python insert_captchas.py
$ python create_root.py
$ python runserver.py
```

Если всё сделали правильно, тест в браузере по адресу localhost:8000 покажет
стартовую страницу в текущей стадии разработки, скрины, как это выглядит у меня, можно посмотреть в каталоге screenshots.
