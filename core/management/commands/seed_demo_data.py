from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.models import Comment, Ingredient, Recipe


class Command(BaseCommand):
    help = "Seed demo users, ingredients, recipes, and comments for browser testing."

    def handle(self, *args, **options):
        User = get_user_model()
        demo_user, _ = User.objects.get_or_create(username="demo")
        demo_user.set_password("demo12345")
        demo_user.save()

        guest_user, _ = User.objects.get_or_create(username="guest")
        guest_user.set_password("guest12345")
        guest_user.save()

        ingredients = {}
        for name in ["Flour", "Eggs", "Milk", "Sugar", "Butter", "Salt", "Vanilla"]:
            ingredient, _ = Ingredient.objects.get_or_create(name=name)
            ingredients[name] = ingredient

        recipes = [
            {
                "title": "Classic Pancakes",
                "description": "Mix the wet ingredients, fold in the dry ingredients, and cook on a hot skillet until golden.",
                "image_url": "/static/images/pancakes.png",
                "ingredient_names": ["Flour", "Eggs", "Milk", "Sugar", "Butter"],
            },
            {
                "title": "Simple Sugar Cookies",
                "description": "Cream butter and sugar, add the dry ingredients, then bake until the edges are lightly golden.",
                "image_url": "/static/images/Sugar_cookies.png",
                "ingredient_names": ["Flour", "Sugar", "Butter", "Eggs", "Vanilla"],
            },
        ]

        for recipe_data in recipes:
            recipe, created = Recipe.objects.get_or_create(
                title=recipe_data["title"],
                defaults={
                    "description": recipe_data["description"],
                    "owner": demo_user,
                    "image_url": recipe_data["image_url"],
                },
            )
            if not created:
                recipe.description = recipe_data["description"]
                recipe.owner = demo_user
                recipe.image_url = recipe_data["image_url"]
                recipe.save()

            recipe.ingredients.set([ingredients[name] for name in recipe_data["ingredient_names"]])

            if not recipe.comments.exists():
                Comment.objects.create(
                    recipe=recipe,
                    author=guest_user,
                    text="This looks great. I want to try it soon.",
                )

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
