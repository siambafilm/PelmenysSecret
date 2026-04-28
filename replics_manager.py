class ReplicksManager:
    """Класс для хранения реплик на русском и английском языках"""
    
    RussianReplicks = [
        # 0
        "*ням-ням-ням*",
        # 1
        "Всё это не то! ",
        # 2
        "На вкус как пенопласт! ",
        # 3
        "Да даже он вкуснее!!! ",
        # 4
        "А вот раньше было…",
        # 5
        "25 лет назад...",
        # 6
        "*ням-ням-ням*",
        # 7
        "Бабушка, твои пельмешки самые-самые вкусные!!!",
        # 8
        "А почему так?",
        # 9
        "Хех",
        # 10
        "А всё дело, внучок, в секретном ингредиенте",
        # 11
        "А что это за ингридиент такой?",
        # 12
        "Потом сам как-нибудь узнаешь...",
        # 13
        "Надо навестить бабушку. ",
        # 14
        "Решено! Отправляюсь во Владивосток!",
        # 15
        "Секрет пельменей",
        # 16
        "Так... Москва-Владивосток...",
        # 17
        "Ох, дорого блин, ну да ладно, что делать..",
        # 18
        "Отправление через час...",
        # 19
        "Неделю спустя..",
        # 20
        "Такс... Осталось найти её дом...",
        # 21
        "Спасибо тебе, внучок!",
        # 22
        "Бабушка, а почему они такие вкусные?",
        # 23
        "Этот ингридиент - моя любовь",
        # 24
        "Как это мило, бабушка ^^",
        # 25
        "Zzz..",
        # 26
        "Интересный какой, спит на работе",
        # 27
        "Ой, смотри-ка, Марин, солнечный какой! Ты к кому, милок?",
        # 28
        "Да это ж, кажется, сынок Люды из пятого! Вылитый!",
        # 29
        "Я... я просто мимо.",
        # 30
        "А, ну ладно! У нас тут сирень как зацвела – душища!",
        # 31
        "И Барсик наш, лежебока, на третьей лавочке развалился. Не наступи на него!",
        # 32
        "Хочешь, загадку загадаю? Что в землю сажаем, всё лето поливаем, а осенью внучки уплетают?",
        # 33
        "Картошку?",
        # 34
        "Деньги?",
        # 35
        "Любовь в банках! Варенье да соленья!",
        # 36
        "Умничка! Чувствуется, из хорошей семьи!",
        # 37
        "На, пирожок с яблоком, домашний. Тёплый ещё! Иди, не задерживай!",
        # 38
        "Ой-ой-ой! Куда это мы собрались?",
        # 39
        "А пропуск формы 7-Г покажете? Или может, удостоверение счастливого человека?",
        # 40
        "Я... мне просто нужно выйти.",
        # 41
        "«Просто выйти»! Ха-ха! Все так говорят!",
        # 42
        "Ладно, шучу. Вижу вы человек приятный. Давайте сыграем: угадаете – пропущу!",
        # 43
        "Что идёт вверх и вниз, но с места не сдвинется ни на сантиметр?",
        # 44
        "Лифт",
        # 45
        "Температура",
        # 46
        "Лестница",
        # 47
        "Молодец! Раз такие дела – вот вам временный пропуск. Только никому не говорите!",
        # 48
        "Извиняй, видимо сегодня не твой день"
    ]
    
    EnglishReplicas = [
        # 0
        "*yum-yum-yum*",
        # 1
        "This is all wrong!",
        # 2
        "Tastes like styrofoam!",
        # 3
        "Even that tastes better!!!",
        # 4
        "But it was better back in the day...",
        # 5
        "25 years ago...",
        # 6
        "*yum-yum-yum*",
        # 7
        "Grandma, your dumplings are the absolute best!!!",
        # 8
        "Why is that?",
        # 9
        "Heh",
        # 10
        "Well, grandson, it's all about the secret ingredient",
        # 11
        "What kind of ingredient is that?",
        # 12
        "You'll find out some other time...",
        # 13
        "I need to visit Grandma.",
        # 14
        "It's decided! I'm going to Vladivostok!",
        # 15
        "Pelmenys` secret",
        # 16
        "So... Moscow to Vladivostok...",
        # 17
        "Oh, that's expensive, damn, oh well, what can you do..",
        # 18
        "Departure in an hour...",
        # 19
        "A week later..",
        # 20
        "So... Now I have to find her house...",
        # 21
        "Thank you, dear grandson!",
        # 22
        "Grandma, why are they so tasty?",
        # 23
        "This ingredient is my love.",
        # 24
        "That's so sweet, grandma ^^",
        # 25
        "Zzz...",
        # 26
        "My, my, sleeping on the job, how interesting",
        # 27
        "Oh, look, Marina, what a sunny young man! Who are you here for, dear?",
        # 28
        "Wait, isn't that Lyuda's boy from the fifth floor? The spitting image!",
        # 29
        "I... I was just passing by.",
        # 30
        "Ah, alright then! Our lilac is in full bloom – such a fragrance!",
        # 31
        "And our lazybones, Barsik the cat, is sprawling on the third bench. Don't step on him!",
        # 32
        "Want me to tell you a riddle? What do we plant in the ground, water all summer, and our granddaughters devour in the fall?",
        # 33
        "Potatoes?",
        # 34
        "Money?",
        # 35
        "Love in jars! Jam and pickles!",
        # 36
        "Clever girl! I can tell you're from a good family!",
        # 37
        "Here, have an apple pie, homemade. Still warm! Go on now, don't linger!",
        # 38
        "Oh, dear, dear! And where might we be off to?",
        # 39
        "May I see your Form 7-G pass? Or perhaps your happy-person identification?",
        # 40
        "I... I just need to get out.",
        # 41
        "'Just get out'! Ha-ha! They all say that!",
        # 42
        "Alright, I'm joking. I can see you're a pleasant person. Let's play a game: guess right – I'll let you pass!",
        # 43
        "What goes up and down but doesn't move an inch from its spot?",
        # 44
        "An elevator",
        # 45
        "Temperature",
        # 46
        "Stairs",
        # 47
        "Well done! Since that's the case – here's a temporary pass for you. Just don't tell anyone!",
        # 48
        "Sorry, looks like it's just not your day"
    ]
    
    @classmethod
    def get_russian_replica(cls, index: int, default: str = "") -> str:
        """Получить русскую реплику по индексу"""
        if 0 <= index < len(cls.RussianReplicks):
            return cls.RussianReplicks[index]
        return default
    
    @classmethod
    def get_english_replica(cls, index: int, default: str = "") -> str:
        """Получить английскую реплику по индексу"""
        if 0 <= index < len(cls.EnglishReplicas):
            return cls.EnglishReplicas[index]
        return default
    
    @classmethod
    def get_replica(cls, index: int, language: str = "russian") -> str:
        """Получить реплику по индексу и языку"""
        if language.lower() == "english":
            return cls.get_english_replica(index)
        return cls.get_russian_replica(index)
    
    @classmethod
    def get_all_russian(cls) -> list:
        """Получить все русские реплики"""
        return cls.RussianReplicks.copy()
    
    @classmethod
    def get_all_english(cls) -> list:
        """Получить все английские реплики"""
        return cls.EnglishReplicas.copy()
    
#using
'''
# Получить конкретную реплику
print(ReplicksManager.get_russian_replica(7))  
# Вывод: "Бабушка, твои пельмешки самые-самые вкусные!!!"

# С выбором языка
print(ReplicksManager.get_replica(7, "english"))  
# Вывод: "Grandma, your dumplings are the absolute best!!!"

# Получить все реплики
all_replicas = ReplicksManager.get_all_russian()

# Проверить количество реплик
print(f"Всего реплик: {len(ReplicksManager.RussianReplicks)}")  # Вывод: 49
'''