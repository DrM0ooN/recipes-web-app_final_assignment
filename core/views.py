from django.contrib import messages
from django.contrib.auth import login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, RecipeFilterForm, RecipeForm
from .models import Comment, Recipe


def home(request):
    return redirect("recipe_list")


def recipe_list(request):
    form = RecipeFilterForm(request.GET or None)
    recipes = Recipe.objects.select_related("owner").prefetch_related("ingredients")

    if form.is_valid():
        for ingredient in form.cleaned_data["ingredients"]:
            recipes = recipes.filter(ingredients=ingredient)

    return render(
        request,
        "recipe_list.html",
        {
            "recipes": recipes.distinct().order_by("title"),
            "filter_form": form,
        },
    )


def recipe_detail(request, pk):
    recipe = get_object_or_404(
        Recipe.objects.select_related("owner").prefetch_related("ingredients", "comments__author"),
        pk=pk,
    )
    comments = recipe.comments.select_related("author").order_by("created_at")

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect(f"/login/?next={request.path}")

        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.recipe = recipe
            comment.author = request.user
            comment.save()
            messages.success(request, "Comment added.")
            return redirect("recipe_detail", pk=recipe.pk)
    else:
        comment_form = CommentForm()

    return render(
        request,
        "recipe_detail.html",
        {
            "recipe": recipe,
            "comments": comments,
            "comment_form": comment_form,
        },
    )


@login_required
def comment_edit(request, recipe_pk, comment_pk):
    recipe = get_object_or_404(Recipe, pk=recipe_pk)
    comment = get_object_or_404(Comment, pk=comment_pk, recipe=recipe)

    if comment.author != request.user:
        return HttpResponseForbidden("You can only edit your own comments.")

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Comment updated.")
            return redirect("recipe_detail", pk=recipe.pk)
    else:
        form = CommentForm(instance=comment)

    return render(
        request,
        "comment_form.html",
        {
            "form": form,
            "page_title": "Edit Comment",
            "submit_label": "Save Comment",
            "recipe": recipe,
            "comment": comment,
        },
    )


@login_required
def comment_delete(request, recipe_pk, comment_pk):
    recipe = get_object_or_404(Recipe, pk=recipe_pk)
    comment = get_object_or_404(Comment, pk=comment_pk, recipe=recipe)

    if comment.author != request.user:
        return HttpResponseForbidden("You can only delete your own comments.")

    if request.method == "POST":
        comment.delete()
        messages.success(request, "Comment deleted.")
        return redirect("recipe_detail", pk=recipe.pk)

    return render(request, "comment_confirm_delete.html", {"recipe": recipe, "comment": comment})


@login_required
def recipe_create(request):
    if request.method == "POST":
        form = RecipeForm(request.POST)
        if form.is_valid():
            form.instance.owner = request.user
            recipe = form.save(commit=True)
            messages.success(request, "Recipe created.")
            return redirect("recipe_detail", pk=recipe.pk)
    else:
        form = RecipeForm()

    return render(
        request,
        "recipe_form.html",
        {
            "form": form,
            "page_title": "Add Recipe",
            "submit_label": "Create Recipe",
        },
    )


@login_required
def recipe_edit(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if recipe.owner != request.user:
        return HttpResponseForbidden("You can only edit your own recipes.")

    if request.method == "POST":
        form = RecipeForm(request.POST, instance=recipe)
        if form.is_valid():
            form.save(commit=True)
            messages.success(request, "Recipe updated.")
            return redirect("recipe_detail", pk=recipe.pk)
    else:
        form = RecipeForm(instance=recipe)

    return render(
        request,
        "recipe_form.html",
        {
            "form": form,
            "page_title": "Edit Recipe",
            "submit_label": "Save Changes",
        },
    )


@login_required
def recipe_delete(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if recipe.owner != request.user:
        return HttpResponseForbidden("You can only delete your own recipes.")

    if request.method == "POST":
        recipe.delete()
        messages.success(request, "Recipe deleted.")
        return redirect("recipe_list")

    return render(request, "recipe_confirm_delete.html", {"recipe": recipe})


def login_view(request):
    return LoginView.as_view(template_name="registration/login.html")(request)


def logout_view(request):
    auth_logout(request)
    return redirect("recipe_list")


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("recipe_list")
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {"form": form})
