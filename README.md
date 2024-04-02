# praktikum_new_diplom

# команда для загрузки ингредиентов:
python manage.py load_ingredients ../data/ingredients.csv

# команда для загрузки тегов:
python manage.py load_tags ../data/tags.csv

# команда для создания пользователей и их токенов:
python manage.py load_users ../data/users.csv

# Пользователи для тестирования сайта:
-------------------------------------------------------------------------------------
username        |    email пользователя      |   Пароль          |   Является админом
-------------------------------------------------------------------------------------
user1           |    some@mail.com           |   ASDfg123456     |       
user2           |    another@mail.com        |   ASDfg123456     |       
user3           |    nyancat@mail.us         |   ASDfg123456     |       
user_admin      |    bigboss@mail.ge         |   ASDfg123456     |       Да

# Команда для создания рецептов:

python manage.py load_recipes ../data/recipes.csv

# Адрес сайта для проверки дипломной работы:

https://taski-masaski.ru/