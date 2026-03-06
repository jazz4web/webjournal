USERNAME_PATTERN = r'^[A-ZА-ЯЁa-zа-яё][A-ZА-ЯЁa-zа-яё0-9\-_.]{2,15}$'

class G:
    def __init__(self):
        self.pariah = "Изгои"
        self.reader = "Читатели"
        self.readerpro = "Читатели+"
        self.commentator = "Комментаторы"
        self.commentatorpro = "Комментаторы+"
        self.blogger = "Писатели"
        self.bloggerpro = "Писатели+"
        self.keeper = "Хранители"
        self.keeperpro = "Хранители+"
        self.root = "Администраторы"

    def weigh(self, group):
        if group == self.pariah:         ##Запрет на вход в сервис
            return 0
        if group == self.reader:         ##Чтение, Профиль, Лента, Лайки
            return 15
        if group == self.readerpro:      ##+Приваты
            return 30
        if group == self.commentator:    ##+Комментарии
            return 45
        if group == self.commentatorpro: ##+Ссылки
            return 50
        if group == self.blogger:        ##+Дизлайки, Свой блог, Объявления
            return 100
        if group == self.bloggerpro:     ##+Хостинг картинок
            return 150
        if group == self.keeper:         ##+Смена группы другим
            return 200
        if group == self.keeperpro:      ##+Блокирование статей
            return 250
        if group == groups.root:         ##Без ограничений
            return 255

    def default_group(self):
        return self.blogger

    def default_groups(self):
        return tuple(item for item in self.groups()
                     if 15 <= self.weigh(item) <= 150)

    def keeper_groups(self):
        return tuple(item for item in self.groups()
                     if self.weigh(item) <= 150)

    def groups(self):
        a = self.__dict__
        return tuple(a[key] for key in a)


groups = G()
