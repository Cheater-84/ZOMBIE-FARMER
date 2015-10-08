# -*- coding: utf-8 -*-

from engine.game_types import Item, CraftItem, BuyItem, ValentItem


class Params(object):

    exclude_players = []

    # Показывать отсутствующих на ферме
    show_away_zombiefarm_players = 0    # Не заходили в игру 24 дня (максимум что можно определить)
    
    # Задействованные локальные модули
    switch_local_players_bot = 1        # Модуль загрузки друзей
    switch_local_box_bot = 1            # Модуль открывания своих сундуков, чемоданов
    switch_local_brain_bot = 1          # Модуль закапывания соседей, работы с мозгами
    switch_local_buff_bot = 0           # Модуль активации бонусов
    switch_local_builder_bot = 0        # Модуль строительства построек
    switch_local_collection_bot = 0     # Модуль обмена коллекций
    switch_local_cook_bot = 1           # Модуль поваров
    switch_local_craft_bot = 1          # Модуль крафтинга
    switch_local_daily_bot = 0          # Модуль разовой ежедневной работы
    switch_local_digger_bot = 1         # Модуль рыбаков и кладоискателей
    switch_local_fir_bot = 0            # Модуль забора пряников из-под ёлочек
    switch_local_gift_bot = 1           # Модуль приема подарков
    switch_local_knock_bot = 0          # Модуль для забора стуков в ваши постройки
    switch_local_location_bot = 1       # Модуль перехода по островам
    switch_local_magic_bot = 0          # Модуль вырубки волшебными палочками
    switch_local_plant_bot = 1          # Модуль посадки растений
    switch_local_resource_bot = 0       # Модуль добычи ресурсов дровосеками и камнетесами
    switch_local_roulette_bot = 1       # Модуль кручения рулеток
    switch_local_send_bot = 0           # Модуль для пересылки ресурсов на другой аккаунт
    switch_local_storage_bot = 0        # Модуль для работы со своим складом, продажи ресурсов
    switch_local_decoration_bot = 0     # Модуль для убирания на склад декора
    switch_local_trader_bot = 0         # Модуль торговцев
    switch_local_blackjack_bot = 0      # Модуль игры в блэкджек
    switch_local_buy_bot = 0            # Модуль покупки на рынке
    switch_local_valent_bot = 0         # Модуль открытия подарков на День Святого Валентина
    switch_local_pickup_bot = 1         # Модуль подбора дропа
    switch_local_monster_bot = 1        # Модуль работы с чудовищем
    switch_local_manual_bot = 0         # Модуль для разового выполнения и отладки
    switch_local_want_bot = 0           # Модуль который ставит в хотелку нужные предметы
    switch_local_mission_bot = 0        # Модуль который проходит квесты
    switch_local_place_bot = 0          # Модуль который заставляет карту объектами

    # Выбираем какие бонусы активировать при необходимости и возможности
    digger_buff = 0                     # Супер-поиск
    cook_buff = 0                       # Минутка поваров
    gain_buff = 0                       # Супер-добыча
    harvest_buff = 0                    # Супер-урожай
    travel_buff = 1                     # Проездной

    # Выбираем какие платные рулетки крутить
    apple_roulette_1 = 0                # Яблочный автомат за 5 яблок
    apple_roulette_2 = 0                # Яблочный автомат за 1 компот
    cherry_roulette_1 = 0               # Вишневый автомат за 5 вишни
    cherry_roulette_2 = 0               # Вишневый автомат за 1 джем
    mandarin_roulette_1 = 0             # Мандариновый автомат за 5 мандарин
    mandarin_roulette_2 = 0             # Мандариновый автомат за 1 мармелад
    lemon_roulette_1 = 0                # Лимонный автомат за 5 лимонов
    lemon_roulette_2 = 0                # Лимонный автомат за 1 микс

    stork_roulette = 1                  # Аист за 15 малины
    taverna_roulette_1 = 0              # Таверна верхняя рулетка (со своими наворотами)
    soldier_roulette = 1                # Солдат за 1 глазной суп
    casino_roulette = 1                 # Казино (со своими наворотами)
    fortune_roulette_1 = 1              # Зомби-фортуна за 5 фишек
    egg_roulette = 1                    # Крутить рулетку в яйцах

    # Товары, чье количество показывается при старте
    show_count_on_start = [
        u'@SHOVEL_EXTRA',               # Лопаты
        u'@CR_666',                     # Бозоны Хиггса
        u'C_42',                        # Изумрудная коллекция
        u'C_36'                         # Японская коллекция
    ]

    # Аккаунты для пересылки товаров, коллекций
    send_accounts = [u'219467070']

    # Сообщение при отправке товаров, коллекций
    send_account_msg = u''

    # Пересылать равными количествами элементы коллекций
    # Работает если в пересылке указан только min
    # 1 - отсылать равными количествами,
    # 0 - все что есть до указанного минимума по каждому элементу
    send_equal_parts_collection = 0

    # Список аккаунтов, которым первым будут под елки класться пряники и удобряться деревья
    premium_accounts = []

    # Принимать платные подарки
    apply_buy_gift = 0

    # Принимать подарки от премиум-соседей
    apply_premium_account_gift = 1

    # Разрешить создавать изумрудку в обсерватории(только полными коллекциями)
    allow_craft_emerald_collection = 1

    # разрешенные типы растений для мгновенных удобрений
    fertilized_plant_types = [u'@ZOLIAN1', u'@ZOLIAN2']

    # Разрешенные типы деревьев для удобрения
    # u'@FT_APPLE', u'@FT_LEMON', u'@FT_CHERRY', u'@FT_MANDARINE', u'@FT_EYE', u'@FT_SKULL'
    fertilized_tree_types = []

    # Разрешенные типы деревьев для покупки на место старых
    rebuy_fruit_tree_types = [u'@FT_MANDARINE', u'@FT_EYE', u'@FT_SKULL', u'@FT_APPLE', u'@FT_CHERRY']

    # Солить рецепты йодированной солью
    allow_cook_speedup = 0

    # Лимит на кладку пряников 1 человеку (0 - Без лимита)
    fir_limit = 5
    
    # Сколько корзин заполнять у поваров (1-3)
    cook_receipts = 3

    # Кому не класть пряники под елку, перечислить ID (Например: u'12345678')
    exclude_fir = []
    
    # Богатства, которые должны быть полностью открыты со склада(кроме тех, что нужно ставить!!!)
    wealth_types = [
        u'@WEALTH_ROLL', u'@WEALTH_CASKET', u'@WEALTH_BOTTLE', u'@WEALTH_ROLL', u'@WEALTH_SKULL',
        u'@WEALTH_VASE', u'@WEALTH_BOWL', u'@WEALTH_FLAG', u'@WEALTH_SEQ', u'@WEALTH_WOODPALM', u'@WEALTH_WHITEM',
        u'@WEALTH_MARBLE', u'@WEALTH_BLACKM', u'@WEALTH_DUBLON_1', u'@WEALTH_DUBLON_2', u'@WEALTH_DUBLON_3',
        u'@WEALTH_DUBLON_4', u'@WEALTH_DUBLON_5', u'@WEALTH_DIAMOND', u'@WEALTH_AMETIST', u'@WEALTH_AQUAMARINE',
        u'@WEALTH_EMERALD', u'@WEALTH_CONE', u'@WEALTH_MITTENS', u'@WEALTH_PITCHER', u'@WEALTH_LARGEBARREL',
        u'@WEALTH_POISON', u'@WEALTH_SWORD', u'@SNOW_APPLE_PACK', u'@SNOW_CHERRY_PACK', u'@SNOW_MANDARIN_PACK'
    ]

    # Объекты которые не стоит достраивать боту-строителю
    exclude_buildings = [
        u'@B_BUCKET', u'@B_UN_02', u'@B_UN_03', u'@B_UN_04', u'@B_UN_05', u'@B_UN_06', u'@B_UN_07',
        u'@B_TRAMP_01', u'@B_TRAMP_02', u'@B_TRAMP_03', u'@B_TRAMP_04', u'@B_TRAMP_05', u'@B_TRAMP_06', u'@B_TRAMP_07'
    ]

    # Объекты под которыми не роем при поиске кладов
    exclude_treasure_dig_types = [
        u'fruitTree', u'plant', u'base', u'Slag', u'building', u'halloweenPrize', u'pickupBox'
    ]

    # Сколько платных мозгов поддерживать через крафтинг в Останкино
    buyed_brains_count = 0

    # Что ставить в свою хотелку
    wish_list = []
    
    # Что зарядить разово в торга для крупного обмена. give - отдаем, want - получаем
    # mega_exchanges = [{
    #     u'give': [{u'item': u'@C_29', u'count': 100}],
    #     u'want': [{u'item': u'@C_34', u'count': 10000}]
    # }]
    # Если список пустой, то ничего не ставим в торга, только перезарядка тем что уже там стоит
    mega_exchanges = []

    # ------------------------------------------------------------------------------------------------ #
    # ПОД ЧЕМ КОПАЕМ У ДРУЗЕЙ
    # ------------------------------------------------------------------------------------------------ #
    dig_items = {
        0: [u'@DS_SYMBOL_E', u'@D_SYMBOL_E', u'@D_ARBOR', u'@D_JAPAN_ARBOR'],
        1: [u'@D_UMBRELLA1_1', u'@D_BALLOON_BLUE2', u'@D_BALLOON_RED2'],
        2: [u'@SCASTLE_GIRL', u'@D_TIN_SOLDIER1', u'@D_TRAIN_1', u'@D_TRAIN_2', u'@D_TRAIN_3', u'@D_TRAIN_4'],
        3: [u'@D_HAND1'],
        4: [u'@B_FLAG_MILAN'],
        5: [u'@B_PISA', u'@D_OLYMPIAD_STATUE', u'@D_FLAG_OLIMPIADA'],
        6: [u'@D_CLOWN', u'@D_BEAR1'],
        7: [u'@B_NYTREE', u'@B_SNOWMAN', u'@B_MAYA', u'@D_CLOCKTOWER', u'@D_LIGHT', u'@D_LIGHTA',
            u'@D_OLYMPIAD_STATUE', u'@B_FLAG_OLIMPIADA', u'@SC_TEAM_GRAVE_WITH_BRAINS', u'@SC_TEAM_GRAVE',
            u'@D_POOL', u'@D_HAND1'],
        8: [u'@B_ELEPHANT', u'@B_ELEPHANT_CASH', u'@D_OLYMPIAD_STATUE', u'@B_FLAG_OLIMPIADA', u'@D_PINKHEART2',
            u'@D_PINKHEART1', u'@D_STONEHEART2', u'@D_STONEHEART1', u'@SC_MG3', u'@SC_MG2', u'@SC_MG1',
            u'@SC_MW2', u'@SC_MW1', u'@SC_MW3', u'@SC_MB1', u'@SC_MB2', u'@SC_MB3', u'@SC_OAK7', u'@SC_OAK6',
            u'@SC_OAK5', u'@SC_PALM1', u'@SC_PALM2', u'@SC_PALM3', u'@SC_SEQ2', u'@SC_SEQ1'],
        9: [u'@SC_GUARD_GRAVE_WITH_BRAINS', u'@SC_GUARD_GRAVE', u'@B_HEART', u'@D_LEADER', u'@D_VILLA', u'@B_BAVARIA',
            u'@B_MANSION', u'@D_POOL', u'@D_FLOWER1', u'@D_CLOUDS2', u'@D_CLOUDS1', u'@D_CLOUDS', u'@D_ELEPHANT_GOLD',
            u'@D_GUILDHALL', u'@D_IDOL_SM', u'@D_IDOL_M', u'@D_IDOL'],
        10: [u'@D_BALLOONS'],
        11: [u'@D_GATE', u'@D_SAKURASMALL', u'@D_REDTREE', u'@D_CONIFER', u'@D_STATUETTE'],
        12: [u'@B_POOL', u'@B_WHITEHOUSE', u'@B_BUSINESS', u'@B_SHIP', u'@D_SYMBOL_I_BEL', u'@DS_SYMBOL_I_BEL',
             u'@D_SYMBOL_U_NESKL', u'@DS_SYMBOL_U_NESKL', u'@D_FLOWER4_WHITE', u'@D_FLOWER4_YELLOW', u'@D_IDOL2',
             u'@B_VAN_ICE_CREAM'],
        13: [u'@B_JAPAN_LAKE', u'@B_EIFFEL', u'@B_JAPAN'],
        14: [u'@D_VALRIGHT'],
        15: [u'@D_PLATFORM', u'@D_PLATFORM_2', u'@D_BOOT_SEREBRO']
    }

    # ------------------------------------------------------------------------------------------------ #
    # ЧТО ИЩЕМ В ТОРГАХ У СОСЕДЕЙ
    # ------------------------------------------------------------------------------------------------ #
    trader_goods = {
        0: [u'@C_36'],
        1: [u'@C_48'],
        2: [u'@C_35'],
        3: [u'@C_37'],
        4: [u'@C_29'],
        5: [u'@C_42']
    }

    # ----------------------------------------------------------------------------------------------- #
    # КВЕСТЫ                                                                                          #
    # ----------------------------------------------------------------------------------------------- #
    # chapter_help             Первые шаги              # chapter_busya             Трудяга и Буся    #
    # chapter_new_year1        За ёлочкой               # chapter_lyalya            Урок химии        #
    # chapter_love             Любовь Зомби             # chapter_pirate            Поднять паруса    #
    # chapter_ufo              Пришельцы на ферме       # chapter_sabbath           Шабаш             #
    # chapter_medal            Медаль                   # chapter_thanksgiving      День Благодарения #
    # chapter_marathon         Марафон                  # chapter_winter_quests     Выпал снег        #
    # chapter_halloween        Изумрудный город         # chapter_oops              Загадка Упса      #
    # chapter_new_year2        Новый год                # black_sign                Чёрная метка      #
    # chapter_admiral          Адмирал                  # black_sign1               Чёрная метка      #
    # chapter_stork            Дерево любви             # black_sign2               Чёрная метка      #
    # chapter_easter           Пасхальная корзина                                                     #
    # chapter_sand             Замки из песка                                                         #
    # chapter_diamond          Алмазная девочка                                                       #
    # chapter_tin_soldier      Стойкий солдатик                                                       #
    # chapter_three_pigs       Три друга                                                              #
    # ----------------------------------------------------------------------------------------------- #

    # Квесты которые нужно проходить(за зомбаксы)
    allow_chapters = [
        u'@chapter_new_year1', u'@chapter_ufo', u'@chapter_halloween', u'@chapter_new_year2 ', u'@chapter_admiral',
        u'@chapter_stork', u'@chapter_sand', u'@chapter_pirate', u'@chapter_oops'
    ]

    # ----------------------------------------------------------------------------------------------- #
    # ОСТРОВА                                                                                         #
    # ----------------------------------------------------------------------------------------------- #
    # Бесплатные                                    # Платные                                         #
    # ---------------------------------------       # ----------------------------------------------- #
    # main		        Домашний остров             # isle_01		    Секретный                     #
    # isle_03		    Остров Любви                # isle_small		Остров Маленькой ёлочки       #
    # isle_02		    Остров Майя                 # isle_star		    Звёздный                      #
    # isle_x		    Остров Х                    # isle_large		Остров Большой ёлки           #
    # isle_faith		Остров Веры                 # isle_moon		    Лунный                        #
    # isle_hope		    Остров Надежды              # isle_giant		Остров Гигантов               #
    # isle_scary		Страшный                    # isle_xxl		    Остров Огромной ёлки          #
    # isle_alpha		Альфа                       # isle_desert		Необитаемый остров            #
    # isle_omega		Омега                                                                         #
    # isle_sand		    Песочный                                                                      #
    # isle_polar		Остров Полярной ночи        # ----------------------------------------------- #
    # isle_wild		    Дремучий                    # Подземелия                                      #
    # isle_mobile		Мобильный остров            # ----------------------------------------------- #
    # isle_ufo		    Остров НЛО                  # un_01             Подножье                      #
    # isle_dream		Остров Мечты                # un_02		        Пещеры Зу                     #
    # isle_scarecrow    Пик Админа                  # un_03	            Мексиканский каньон           #
    # isle_elephant		Ужасный остров              # un_04 	        Копи царя Зомби               #
    # isle_emerald		Город-призрак               # un_05		        Нижнее днище                  #
    # isle_light		Вишневый остров             # un_06		        Бездна                        #
    # isle_monster		Остров Чудовища             # un_07		        Хрустальный                   #
    # isle_gnome		Остров гномов               # un_08		        Мраморная пещера              #
    # isle_halloween    Лысая гора                  # un_09		        Склад хакера                  #
    # ----------------------------------------------------------------------------------------------- #

    # Острова на которые не заходим
    exclude_locations = [
        u'isle_gnome', u'@exploration_isle1_random' u'@exploration_isle2_random' u'@exploration_isle3_random'
        u'@exploration_snow1' u'@exploration_isle1_1' u'@exploration_isle4_random' u'@exploration_snow2'
        u'@exploration_empty' u'@exploration_glade' u'@exploration_furry1' u'@exploration_furry2'
        u'@exploration_furry3' u'@exploration_tropic1' u'@exploration_tropic2' u'@exploration_isle_un1_1'
        u'@exploration_isle_un1_2' u'@exploration_isle_un1_3' u'@exploration_sports1' u'@exploration_sports2'
        u'@exploration_sweet1' u'@exploration_sports3' u'@isle_halloween' u'@isle_paper' u'@isle_football'
        u'@exploration_solar' u'@isle_coffee_plantation' u'@exploration_wonderland1' u'@exploration_wonderland2'
        u'@exploration_isle_un1_4' u'@exploration_atlantis_1' u'@exploration_atlantis_2' u'@exploration_helloween'
        u'@exploration_butterfly' u'@exploration_atlantis_3' u'@exploration_atlantis_4' u'@exploration_atlantis_5'
        u'@exploration_grotto' u'@exploration_crystal' u'@exploration_silverland' u'@exploration_steel'
        u'@exploration_crater' u'@exploration_starzy' u'@exploration_starpass' u'@exploration_sanctuary'
        u'@exploration_independent_asteroid_random'
    ]

    # Остров, где копаем клады
    treasure_location = u'isle_moon'

    # Остров, где крадем мешочки
    stolen_island = u'main'

    # Список островов, где вырубаем палочками-выручалочками
    allow_magic_locations = []

    # Список островов, где нужно убрать на склад весь декор
    allow_move_decoration_locations = [
        u'isle_faith', u'isle_scary', u'isle_small', u'isle_01', u'isle_star', u'isle_large', u'isle_moon',
        u'isle_giant', u'isle_xxl', u'isle_ufo', u'isle_dream', u'isle_elephant', u'isle_desert', u'isle_emerald',
        u'isle_scarecrow', u'isle_03', u'isle_02', u'isle_x', u'isle_faith', u'isle_light',
        u'isle_hope', u'isle_alpha', u'isle_omega', u'isle_sand', u'isle_polar', u'isle_wild', u'isle_mobile',
        u'isle_monster', u'isle_gnome', u'isle_halloween'
    ]

    # ----------------------------------------------------------------------------------------------- #
    # КОЛЛЕКЦИИ                                                                                       #
    # ----------------------------------------------------------------------------------------------- #
    # C_1       Звёздная коллекция                  # C_25      Пляжная коллекция                     #
    # C_2       Луксорская коллекция                # C_26      Коллекция Майя                        #
    # C_3       Байкерская коллекция                # C_27      Секретная коллекция                   #
    # C_4       Коллекция знаков                    # C_28      Гипер-коллекция                       #
    # C_5       Ручная коллекция                    # C_29      Коллекция Хэллоуин                    #
    # C_6       Обувная коллекция                   # C_30      Президентская коллекция               #
    # C_7       Очень страшная коллекция            # C_31      Зимняя коллекция                      #
    # C_8       Строительная коллекция              # C_32      Подземельная коллекция                #
    # C_9       Столовая коллекция                  # C_33      Любовная коллекция                    #
    # C_10      Редкая коллекция                    # C_34      Адская коллекция                      #
    # C_11      Автомобильная коллекция             # C_35      Райская коллекция                     #
    # C_12      Туристическая коллекция             # C_36      Японская коллекция                    #
    # C_13      Домашняя коллекция                  # C_37      Школьная коллекция                    #
    # C_14      Коллекция игрушек                   # C_38      Пиратская коллекция                   #
    # C_15      Ёлочная коллекция                   # C_39      Коллекция рыбака                      #
    # C_16      Коллекция Белого кролика            # C_40      Военная коллекция                     #
    # C_17      Коллекция Цветов                    # C_41      Футбольная коллекция                  #
    # C_18      Коллекция Деда Мороза               # C_42      Изумрудная коллекция                  #
    # C_19      Коллекция Анти-зомби                # C_43      Песочная коллекция                    #
    # C_20      Коллекция Брендов                   # C_44      Коллекция Котят                       #
    # C_21      Весенняя коллекция                  # C_45      Коллекция Щенков                      #
    # C_22      Тинейджерская коллекция             # C_46      Тропическая коллекция                 #
    # C_23      Коллекция компа                     # C_47      Плохая коллекция                      #
    # C_24      Морская коллекция                   # C_48      Коллекция палача                      #
    # ----------------------------------------------------------------------------------------------- #

    # Что обменивать или пересылать из коллекций
    # Указывается минимум который должен остаться на складе
    # Количество сколько обменивать за раз
    changed_colls = [
        Item(name=u'C_2', min=100),
        Item(name=u'C_7', min=100),
        Item(name=u'C_13', min=100),
        Item(name=u'C_24', min=100),
        Item(name=u'C_25', min=100),
        Item(name=u'C_26', min=100),
        Item(name=u'C_27', min=500),
        Item(name=u'C_28', min=500),
        Item(name=u'C_30', min=500),
        Item(name=u'C_31', min=500),
        Item(name=u'C_32', min=500),
        Item(name=u'C_33', min=500),
        Item(name=u'C_35', min=500),
        Item(name=u'C_37', min=500),
        Item(name=u'C_50', min=500),
        Item(name=u'C_19', min=500),
        Item(name=u'C_17', min=500),
        Item(name=u'C_21', min=100)
    ]

    # Что продавать со склада
    # Указывается минимум который должен остаться на складе
    sell_items = [
        Item(name=u'@CR_07', min=500),              # Гвозди
        Item(name=u'@CR_18', min=500000),           # Мрамор
        Item(name=u'@CR_37', min=500),              # Кварц
        Item(name=u'@CR_38', min=500),              # Черный мрамор
        Item(name=u'@CR_43', min=500),              # Компас
        Item(name=u'@CR_65', min=500000),              # Фольга
        Item(name=u'@CR_66', min=500000),              # Лампочка
        Item(name=u'@CR_75', min=500),              # Книги
        Item(name=u'@CR_80', min=500),              # Подушка
        Item(name=u'@CR_83', min=500),              # Язь
        Item(name=u'@CR_26', min=2500000),             # Снежок
        Item(name=u'@CR_11', min=250000),             # Доска
        Item(name=u'@CR_01', min=250000),             # Цемент
        Item(name=u'@CR_10', min=50000),             # Желтая краска
        Item(name=u'@CR_29', min=500),             # Огонь
        Item(name=u'@CR_101', min=100),             # Чертовщина
        Item(name=u'@S_45', min=100000),                # Зомбильоны
        Item(name=u'@S_46', min=20000),              # Маракасы
        Item(name=u'@S_47', min=100000),                # Красные драконы
        Item(name=u'@S_48', min=100),                # Спиральки
        Item(name=u'@S_49', min=1000000),                # Светляки
        Item(name=u'@S_50', min=100)                 # Желтые тюльпаны
    ]

    # Что пересылаем на свой аккаунт
    send_items = [Item(name=u'@CR_66', count=1)]

    # Бесплатные подарки
    free_gifts = [
        # u'@CR_31',  # Любовь
        u'@CR_06',  # Металл
        u'@CR_16',  # Шестерня
        u'@CR_40',  # Капля
        u'@CR_25',  # Стекло
        u'@CR_11',  # Доска
        u'@CR_44',  # Мир
        u'@CR_70',  # Время
        u'@CR_01',  # Цемент
        u'@CR_97'   # Рогатка
    ]

    # Сообщение с которым отсылаются бесплатные подарки
    free_msg = u''

    # Подарки тем, кто ниже 80 уровня, и не пропадает из игры больше чем на 3 дня
    low_level_gifts = []

    # Сообщение, с которым отсылается сообщение тем кто ниже 80 уровня
    low_level_msg = u''

    # Список ID соседей ниже 80 уровня которым не дарим подарки
    exclude_low_level = []

    # ----------------------------------------------------------------------------------------------- #
    # СЕМЕНА                                                                                          #
    # ----------------------------------------------------------------------------------------------- #
    # P_01      Черника                 # P_30      Сон-трава                                         #
    # P_02      Подсолнух               # P_31      Росянка дикая                                     #
    # P_03R     Клевер                  # P_32      Капуста                                           #
    # P_04      Баклажан                # P_33      Чёрная рука                                       #
    # P_05      Тыква                   # P_34      Белая рука                                        #
    # P_06      Костируза               # P_35      Ананас                                            #
    # P_07      Кактус                  # P_36      Тростник                                          #
    # P_08      Чеснок                  # P_37      Клубника                                          #
    # P_09      Гипносолнух             # P_38      Картошка                                          #
    # P_10      Рожь                    # P_39      Мозговница                                        #
    # P_11      Горох                   # P_40      Костяная нога                                     #
    # P_12      Бамбук                  # P_41      Виноград                                          #
    # P_13      Кукуруза                # P_44      Яблочный мак                                      #
    # P_14R     Тыквахелл               # P_45      Зомбильон                                         #
    # P_15      Лилия                   # P_46      Маракас                                           #
    # P_21      Волчья ягода            # P_47      Красный дракон                                    #
    # P_22      Мухомор                 # P_48      Спиралька                                         #
    # P_23      Глазной горох           # P_49      Светляк                                           #
    # P_24      Мак                     # P_50      Жёлтый тюльпан                                    #
    # P_25      Лук                     # P_57      Малина                                            #
    # P_26      Перец Чили              # P_58      Арбуз                                             #
    # P_27      Алые розы               # P_59      Рамбутан                                          #
    # P_28      Смородина               # P_60      Клеверфон                                         #
    # P_29      Помидоры                # P_61      Плансолнух                                        #
    # ----------------------------------------------------------------------------------------------- #

    # Что сажать, по островам и со своими лимитами
    seed_items_dict = {
        u'other': [Item(name=u'P_08', max=100000), Item(name=u'P_15', max=100000)],
        u'un_01': [Item(name=u'P_45')],
        u'un_03': [Item(name=u'P_46')],
        u'un_04': [Item(name=u'P_47')],
        u'un_05': [Item(name=u'P_48')],
        u'un_06': [Item(name=u'P_49')],
        u'un_07': [Item(name=u'P_50')],
        u'un_08': [Item(name=u'P_46')],
        u'un_09': [Item(name=u'P_49')]
    }

    # ----------------------------------------------------------------------------------------------- #
    # РЕЦЕПТЫ                                                                                         #
    # ----------------------------------------------------------------------------------------------- #
    # RECIPE_01		Гипномак                        # RECIPE_29		Розовая краска                    #
    # RECIPE_02		Клеверхелл                      # RECIPE_30		Чернила                           #
    # RECIPE_03		Росянка острая                  # RECIPE_31		Сталь                             #
    # RECIPE_04		Черника с косточкой             # RECIPE_32		Зомбаксид                         #
    # RECIPE_05		Грибная текила                  # RECIPE_33		Валенок                           #
    # RECIPE_06		Черепки в томате                # RECIPE_34		Овощная бочка                     #
    # RECIPE_07		Волчий штык                     # RECIPE_35		Палочка-выручалочка               #
    # RECIPE_08		Глазная настойка                # RECIPE_36		Шоколад                           #
    # RECIPE_09		Чесночная лилия                 # RECIPE_37		Слёзы зомби                       #
    # RECIPE_10		Сонный качан                    # RECIPE_38		Акварель                          #
    # RECIPE_11		Гипносон                        # RECIPE_39		Альбом                            #
    # RECIPE_12		Хеллия                          # RECIPE_40		Так себе по Человековедению       #
    # RECIPE_13		Глазная росянка                 # RECIPE_41		Корректор                         #
    # RECIPE_14		Волчья кость                    # RECIPE_42		Нормально в Зомбологии            #
    # RECIPE_15		Голова-гриб                     # RECIPE_43		Букет                             #
    # RECIPE_16		Сонхелл                         # RECIPE_44		Хорошо по Человековедению         #
    # RECIPE_17		Сонная росянка                  # RECIPE_45		Хорошо по Зомбологии              #
    # RECIPE_18		Волчья пасть                    # RECIPE_46		Шпаргалка                         #
    # RECIPE_19		Волчиум                         # RECIPE_47		Зомбология на отлично             #
    # RECIPE_20		Зомбиум                         # RECIPE_48		Человековедение на отлично        #
    # RECIPE_21		Баклажадина                     # RECIPE_49		Медаль зомби                      #
    # RECIPE_22		Гарбузики                       # RECIPE_50		Компот                            #
    # RECIPE_23		Японский горох                  # RECIPE_51		Вишнёвый джем                     #
    # RECIPE_24		Черничный крендель              # RECIPE_52		Лимонный микс                     #
    # RECIPE_25		Золотая пыль                    # RECIPE_53		Мармелад                          #
    # RECIPE_26		Кукурузные палочки              # RECIPE_54		Глазной суп                       #
    # RECIPE_27		Белая краска                    # RECIPE_55		Чертовщина                        #
    # RECIPE_28		Синяя краска                    # RECIPE_56		Песок                             #
    # ----------------------------------------------------------------------------------------------- #

    # Рецепты для поваров
    recipes = [
        Item(name=u'RECIPE_36'), Item(name=u'RECIPE_50')
    ]

    # Список для автоматического крафтинга
    crafts = [
        # CraftItem(building=u'@B_BUSINESS', craft_id=0, count=100),
        # CraftItem(building=u'@B_EYE', craft_id=0),
        # CraftItem(building=u'@B_UNIVERSITY_EMERALD2', craft_id=0, count=100),
        # CraftItem(building=u'@B_MILL_EMERALD2'),
        # CraftItem(building=u'@B_LIGHT_EMERALD2'),
        # CraftItem(building=u'@B_VAN_ICE_CREAM', craft_id=0, count=1, signal=u'travel_buff')
    ]

    # Mode =
    # 0 - Покупать и вырубать палочками-выручалочками(count не задаем, он определяется свободными палочками)
    # 1 - Покупать и продавать
    # 2 - Покупать и сразу открывать(для подарков на День Святого Валентина и схожих)
    # 3 - Покупать и прятать на склад (для зомбиков)
    # 4 - Просто купить

    buy_items = [
        BuyItem(mode=0, item=u'@UN_LANTERN_A', location=u'un_08', x=19L, y=25L),
        BuyItem(mode=1, item=u'@D_TRACK_BAMBOO_1', count=300, location=u'isle_moon', x=12L, y=44L),
        BuyItem(mode=2, item=u'@VALENT_GIFT_BOX6', count=50, location=u'main', x=69L, y=48L),
        BuyItem(mode=0, item=u'@UN_FERN', location=u'un_09', x=14L, y=22L),
        BuyItem(mode=3, item=u'@SC_FISHER_GRAVE_BRAINER', count=700, location=u'isle_giant', x=36L, y=26L),
        BuyItem(mode=3, item=u'@SC_TRADER_GRAVE_WITH_BRAINS', count=100, location=u'isle_giant', x=36L, y=26L),
        BuyItem(mode=4, item=u'@F_RED_BIG', count=100, location=u'main'),
        BuyItem(mode=4, item=u'@RED_SPEEDUPER3', count=10000)
    ]

    # Открытие подарков подарков со дн святого валентина
    valent_gifts = [
        ValentItem(item=u'@MARCH_GIFT_BOX1', location=u'isle_03', x=16L, y=62L)
    ]

    # При сборе статистики посещать у каждого будет эти острова
    statistic_islands = [
        u'main', u'isle_03', u'isle_02', u'isle_x', u'isle_faith', u'isle_hope'
    ]
