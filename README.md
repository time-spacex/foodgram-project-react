# praktikum_new_diplom

# команда для загрузки ингредиентов:
python manage.py load_ingredients ../data/ingredients.csv

# команда для загрузки тегов:
python manage.py load_tags ../data/tags.csv

# команда для создания пользователей и их токенов:
python manage.py load_users ../data/users.csv

# Создание пользователей для тестирования сайта:
------------------------------------------------------------------
email пользователя   |   Пароль          |   Является админом
------------------------------------------------------------------
some@mail.com           |   ASDfg123456     |       
another@mail.com        |   ASDfg123456     |       
nyancat@mail.us         |   ASDfg123456     |       
bigboss@mail.ge         |   ASDfg123456     |       Да

# Команда для создания рецептов:

python manage.py load_recipes ../data/recipes.csv
