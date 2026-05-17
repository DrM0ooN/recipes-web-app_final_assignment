from django.contrib import admin

from .models import Comment, Ingredient, Recipe


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
	search_fields = ["name"]
	ordering = ["name"]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
	list_display = ["title", "owner", "created_at"]
	list_filter = ["created_at", "ingredients"]
	search_fields = ["title", "description"]
	filter_horizontal = ["ingredients"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
	list_display = ["recipe", "author", "created_at"]
	search_fields = ["text", "recipe__title", "author__username"]
