from django.conf import settings
from django.db import models


class Ingredient(models.Model):
	name = models.CharField(max_length=120, unique=True)

	class Meta:
		ordering = ["name"]

	def __str__(self):
		return self.name


class Recipe(models.Model):
	title = models.CharField(max_length=200)
	description = models.TextField()
	image_url = models.CharField(max_length=500, blank=True, default="/static/images/recipe-default.svg")
	owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recipes")
	ingredients = models.ManyToManyField(Ingredient, related_name="recipes", blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["title"]

	def __str__(self):
		return self.title


class Comment(models.Model):
	recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="comments")
	author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
	text = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["created_at"]

	def __str__(self):
		return f"Comment by {self.author} on {self.recipe}"
