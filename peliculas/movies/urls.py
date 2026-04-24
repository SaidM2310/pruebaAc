from django.urls import path
from .views import *

urlpatterns = [
    path('all/', all_movies),
    path('<int:movie_id>/', movie, name='movie_detail'),
    path('saludo/<int:veces>/', saludo),
    path('register/', register, name='register'),
    path('like/<int:movie_id>/', add_to_collection, name='add_to_collection'),
    path('collections/', collections, name='collections'),
    path('movie_review/add/<int:movie_id>/', add_review),
    path('my-reviews/', my_reviews, name='my_reviews'),
    path('actor/<int:person_id>/', actor_detail, name='actor_detail'),
    path('update-actors/', update_tmdb_ids),
    path('movie_reviews/<int:movie_id>/', movie_reviews, name='movie_reviews'),
    path('', index)
]
