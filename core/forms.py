from django import forms

from .models import Comment, Ingredient, Recipe


class RecipeForm(forms.ModelForm):
    image_url = forms.CharField(
        label="Image URL",
        required=False,
        help_text="Leave blank to use a default food image.",
    )

    ingredients_input = forms.CharField(
        label="Ingredients",
        help_text="Enter one ingredient per line or separate them with commas.",
        widget=forms.Textarea(attrs={"rows": 4}),
    )

    class Meta:
        model = Recipe
        fields = ["title", "description", "image_url"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 8}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            ingredient_names = self.instance.ingredients.order_by("name").values_list("name", flat=True)
            self.fields["ingredients_input"].initial = ", ".join(ingredient_names)

    def clean_ingredients_input(self):
        raw_value = self.cleaned_data["ingredients_input"]
        tokens = [
            token.strip()
            for line in raw_value.splitlines()
            for token in line.split(",")
        ]
        ingredients = [token for token in tokens if token]
        if not ingredients:
            raise forms.ValidationError("Add at least one ingredient.")
        return ingredients

    def clean_image_url(self):
        image_url = self.cleaned_data.get("image_url", "").strip()
        return image_url or "/static/images/recipe-default.svg"

    def save(self, commit=True):
        recipe = super().save(commit=False)
        if commit:
            recipe.save()
            ingredient_objects = []
            for ingredient_name in self.cleaned_data["ingredients_input"]:
                ingredient, _ = Ingredient.objects.get_or_create(name=ingredient_name)
                ingredient_objects.append(ingredient)
            recipe.ingredients.set(ingredient_objects)
        return recipe


class RecipeFilterForm(forms.Form):
    ingredients = forms.ModelMultipleChoiceField(
        queryset=Ingredient.objects.none(),
        required=False,
        widget=forms.SelectMultiple,
        label="Filter by ingredients",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ingredients"].queryset = Ingredient.objects.order_by("name")


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 4, "placeholder": "Add a comment..."}),
        }
