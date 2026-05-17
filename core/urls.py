from django.urls import path

from . import views

urlpatterns = [
    path("", views.recipe_list, name="recipe_list"),
    path("home/", views.home, name="home"),
    path("recipes/add/", views.recipe_create, name="recipe_create"),
    path("recipes/<int:pk>/", views.recipe_detail, name="recipe_detail"),
    path("recipes/<int:pk>/edit/", views.recipe_edit, name="recipe_edit"),
    path("recipes/<int:pk>/delete/", views.recipe_delete, name="recipe_delete"),
    path("recipes/<int:recipe_pk>/comments/<int:comment_pk>/edit/", views.comment_edit, name="comment_edit"),
    path("recipes/<int:recipe_pk>/comments/<int:comment_pk>/delete/", views.comment_delete, name="comment_delete"),
]
