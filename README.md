***webjournal*** - это web-приложение для развёртывания сайта текстовых блогов на собственном домене.
В приложении реализованы все функциональные возможности, необходимые для ведения текстовых блогов:

* авторизация пользователей и самостоятельная регистрация аккаунта;
* дифференциация пользователей по группам;
* профиль пользователя и самостоятельное обслуживание аккаунта
(смена пароля, смена e-mail, смена аватара etc.);
* сервис коротких ссылок;
* хостинг картинок;
* сервис черновиков;
* сервис объявлений;
* главное меню с ключевыми ссылками;
* сервис приватных сообщений;
* сервис древовидных комментариев в топиках блогов;
* метки по ключевым словам;
* лайки/дизлайки, подписки, друзья;
* инструменты администратора.

Порядок запуска приложения в Debian testing/sid:

```
$ mkdir ~/workspace
$ cd ~/workspace
$ git clone https://github.com/jazz4web/webjournal.git
$ cd webjournal
$ sudo apt install $(cat deployment/packages)
$ createdb webjournal
$ psql -d webjournal -f sql/db.sql
$ python3.14 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ tar xvaf deployment/vendor.tar.gz -C webapp/static
$ tar xvaf deployment/images.tar.gz -C webapp/static
$ ln -s -T ~/workspace/webjournal/webapp/static/vendor/bootstrap/fonts/ webapp/static/fonts
$ cp env_template .env
$ python insert_captchas.py
$ python create_root.py
$ python runserver.py
```

Если всё сделали правильно, тест в браузере по адресу **localhost:8000** покажет
стартовую страницу в текущей стадии разработки. Снимки экрана, как ключевые страницы приложения выглядят у меня 
в окне браузера, можно посмотреть в каталоге *screenshots*. Оценить скорость отклика
будущего сайта может каждый желающий.

Проект закрыт. Всех благодарю за внимание.
