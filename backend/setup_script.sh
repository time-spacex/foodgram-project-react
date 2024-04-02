cd foodgram_backend
python manage.py migrate
python manage.py collectstatic
cp -r /app/foodgram_backend/collected_static/. /backend_static/static/
python manage.py load_ingredients ../data/ingredients.csv
python manage.py load_tags ../data/tags.csv
python manage.py load_users ../data/users.csv
python manage.py load_recipes ../data/recipes.csv