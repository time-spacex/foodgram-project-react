# praktikum_new_diplom

# команда для загрузки ингредиентов:
python manage.py load_ingredients ../data/ingredients.csv

# команда для загрузки тегов:
python manage.py load_tags ../data/tags.csv

# команда для создания пользователей и их токенов:
python manage.py load_users ../data/users.csv

# Создание пользователей для тестирования сайта:
------------------------------------------------------------------
Username пользователя   |   Пароль          |   Является админом
------------------------------------------------------------------
user1                   |   ASDfg123456     |       
user2                   |   ASDfg123456     |       
user3                   |   ASDfg123456     |       
user_admin              |   ASDfg123456     |       Да

# Команда для создания рецептов:

python manage.py load_recipes ../data/recipes.csv
