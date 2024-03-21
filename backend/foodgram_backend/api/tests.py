from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITransactionTestCase
from rest_framework.authtoken.models import Token

from recipes.models import User, Recipe, Ingredient, IngredientsInRecipe, Tag


class RecipesApiTestCase(APITransactionTestCase):
    """Тесты api рецептов."""

    @classmethod
    def setUpClass(cls):
        cls.url = reverse('recipes-list')

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='vi')
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        self.recipe = Recipe.objects.create(
            author=self.user,
            name='Cookie',
            text='Badabada',
            cooking_time=10,
        )
        self.salt = Ingredient.objects.create(
            name='Salt',
            measurement_unit='kg',
        )
        self.recipe_ing = IngredientsInRecipe.objects.create(
            ingredient=self.salt,
            amount=32,
            recipe=self.recipe
        )
        self.tag = Tag.objects.create(name='dinner', color='red')

    def test_smoke(self):
        self.assertTrue(True)

    def test_list(self):
        resp = self.client.get(self.url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        obj = resp.data['results'][0]
        self.assertEqual(obj['name'], self.recipe.name)
        ing = obj['ingredients'][0]
        self.assertEqual(ing.get('id'), self.salt.id)
        self.assertEqual(ing.get('amount'), self.recipe_ing.amount)
        self.assertEqual(ing.get('name'), self.salt.name)

    def test_create_recipe(self):
        data = dict(
            name='Pie',
            text='Create pie',
            ingredients=[{'id': self.salt.id, 'amount': '32'}, ],
            tags=[self.tag.id,],
            cooking_time=10,
        )

        resp = self.client.post(self.url, data=data, format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        ingredients = data.pop('ingredients')
        ing = ingredients[0]
        self.assertEqual(ing.get('id'), self.salt.id)

        tags = data.pop('tags')
        tag_id = tags[0]
        self.assertEqual(tag_id, self.tag.id)

        self.assertTrue(Recipe.objects.filter(**data).exists())
        rec_ing = IngredientsInRecipe.objects.filter(
            amount=ing.get('amount'),
            ingredient=self.salt.id).last()
        self.assertEqual(ing.get('amount'), str(rec_ing.amount))
