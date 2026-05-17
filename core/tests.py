from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Comment, Ingredient, Recipe


User = get_user_model()


class AuthTests(TestCase):
	def test_register_logs_user_in_and_redirects_to_recipe_list(self):
		response = self.client.post(
			reverse("register"),
			{
				"username": "alice",
				"password1": "StrongPass123!",
				"password2": "StrongPass123!",
			},
		)

		self.assertRedirects(response, reverse("recipe_list"))
		self.assertTrue(User.objects.filter(username="alice").exists())
		self.assertEqual(int(self.client.session.get("_auth_user_id")), User.objects.get(username="alice").id)

	def test_login_redirects_to_recipe_list(self):
		user = User.objects.create_user(username="bob", password="StrongPass123!")

		response = self.client.post(
			reverse("login"),
			{"username": user.username, "password": "StrongPass123!"},
		)

		self.assertRedirects(response, reverse("recipe_list"))

	def test_logout_redirects_to_recipe_list(self):
		user = User.objects.create_user(username="carol", password="StrongPass123!")
		self.client.force_login(user)

		response = self.client.get(reverse("logout"))

		self.assertRedirects(response, reverse("recipe_list"))


class RecipeTests(TestCase):
	def setUp(self):
		self.owner = User.objects.create_user(username="owner", password="StrongPass123!")
		self.other_user = User.objects.create_user(username="guest", password="StrongPass123!")
		self.flour = Ingredient.objects.create(name="Flour")
		self.sugar = Ingredient.objects.create(name="Sugar")
		self.eggs = Ingredient.objects.create(name="Eggs")

		self.recipe_one = Recipe.objects.create(
			title="Cake",
			description="Mix and bake.",
			owner=self.owner,
		)
		self.recipe_one.ingredients.set([self.flour, self.sugar, self.eggs])

		self.recipe_two = Recipe.objects.create(
			title="Cookies",
			description="Stir and bake.",
			owner=self.owner,
		)
		self.recipe_two.ingredients.set([self.flour, self.sugar])

	def test_recipe_list_is_public_and_orders_by_title(self):
		response = self.client.get(reverse("recipe_list"))

		self.assertContains(response, "Cake")
		self.assertContains(response, "Cookies")
		self.assertLess(response.content.decode().find("Cake"), response.content.decode().find("Cookies"))

	def test_filter_requires_all_selected_ingredients(self):
		response = self.client.get(reverse("recipe_list"), {"ingredients": [self.flour.id, self.eggs.id]})

		self.assertContains(response, "Cake")
		self.assertNotContains(response, "Cookies")

	def test_authenticated_user_can_create_recipe(self):
		self.client.force_login(self.owner)

		response = self.client.post(
			reverse("recipe_create"),
			{
				"title": "Pancakes",
				"description": "Cook on a skillet.",
				"ingredients_input": "Flour, Milk, Eggs",
			},
		)

		recipe = Recipe.objects.get(title="Pancakes")
		self.assertRedirects(response, reverse("recipe_detail", args=[recipe.pk]))
		self.assertEqual(recipe.owner, self.owner)
		self.assertEqual(set(recipe.ingredients.values_list("name", flat=True)), {"Flour", "Milk", "Eggs"})

	def test_recipe_owner_can_edit_and_delete(self):
		self.client.force_login(self.owner)

		edit_response = self.client.post(
			reverse("recipe_edit", args=[self.recipe_one.pk]),
			{
				"title": "Updated Cake",
				"description": "Mix more carefully.",
				"ingredients_input": "Flour, Sugar, Eggs",
			},
		)
		self.assertRedirects(edit_response, reverse("recipe_detail", args=[self.recipe_one.pk]))

		delete_response = self.client.post(reverse("recipe_delete", args=[self.recipe_two.pk]))
		self.assertRedirects(delete_response, reverse("recipe_list"))
		self.assertFalse(Recipe.objects.filter(pk=self.recipe_two.pk).exists())

	def test_non_owner_cannot_edit_or_delete(self):
		self.client.force_login(self.other_user)

		edit_response = self.client.post(
			reverse("recipe_edit", args=[self.recipe_one.pk]),
			{
				"title": "Hacked Cake",
				"description": "Nope.",
				"ingredients_input": "Flour",
			},
		)
		delete_response = self.client.post(reverse("recipe_delete", args=[self.recipe_one.pk]))

		self.assertEqual(edit_response.status_code, 403)
		self.assertEqual(delete_response.status_code, 403)

	def test_authenticated_user_can_comment_on_recipe(self):
		self.client.force_login(self.other_user)

		response = self.client.post(
			reverse("recipe_detail", args=[self.recipe_one.pk]),
			{"text": "Looks great!"},
		)

		self.assertRedirects(response, reverse("recipe_detail", args=[self.recipe_one.pk]))
		self.assertTrue(Comment.objects.filter(recipe=self.recipe_one, author=self.other_user, text="Looks great!").exists())

	def test_comment_author_can_edit_comment(self):
		comment = Comment.objects.create(recipe=self.recipe_one, author=self.other_user, text="Old comment")
		self.client.force_login(self.other_user)

		response = self.client.post(
			reverse("comment_edit", args=[self.recipe_one.pk, comment.pk]),
			{"text": "Updated comment"},
		)

		comment.refresh_from_db()
		self.assertRedirects(response, reverse("recipe_detail", args=[self.recipe_one.pk]))
		self.assertEqual(comment.text, "Updated comment")

	def test_non_author_cannot_edit_comment(self):
		comment = Comment.objects.create(recipe=self.recipe_one, author=self.other_user, text="Old comment")
		self.client.force_login(self.owner)

		response = self.client.post(
			reverse("comment_edit", args=[self.recipe_one.pk, comment.pk]),
			{"text": "Updated comment"},
		)

		comment.refresh_from_db()
		self.assertEqual(response.status_code, 403)
		self.assertEqual(comment.text, "Old comment")

	def test_comment_author_can_delete_comment(self):
		comment = Comment.objects.create(recipe=self.recipe_one, author=self.other_user, text="Delete me")
		self.client.force_login(self.other_user)

		response = self.client.post(reverse("comment_delete", args=[self.recipe_one.pk, comment.pk]))

		self.assertRedirects(response, reverse("recipe_detail", args=[self.recipe_one.pk]))
		self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())

	def test_non_author_cannot_delete_comment(self):
		comment = Comment.objects.create(recipe=self.recipe_one, author=self.other_user, text="Delete me")
		self.client.force_login(self.owner)

		response = self.client.post(reverse("comment_delete", args=[self.recipe_one.pk, comment.pk]))

		self.assertEqual(response.status_code, 403)
		self.assertTrue(Comment.objects.filter(pk=comment.pk).exists())
