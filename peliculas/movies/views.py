from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from movies.models import Movie, MovieReview, Person, MovieLike
from movies.forms import MovieReviewForm, MovieCommentForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Collection
from .models import MovieReview
from django.shortcuts import render, get_object_or_404
from .models import Person, Movie
import requests
from .models import Person
from django.shortcuts import redirect, get_object_or_404
from .models import Collection, Movie



@login_required
def my_reviews(request):
    reviews = MovieReview.objects.filter(user=request.user)

    return render(request, 'movies/my_reviews.html', {
        'reviews': reviews
    })
    
def all_movies(request):
    movies = Movie.objects.all().order_by('title')

    grouped = {}

    for movie in movies:
        letter = movie.title[0].upper()

        if letter not in grouped:
            grouped[letter] = []

        grouped[letter].append(movie)

    grouped = dict(sorted(grouped.items()))

    liked_movies = []

    if request.user.is_authenticated:
        liked_movies = MovieLike.objects.filter(
    user=request.user,
    like=1
).values_list('movie_id', flat=True)

    context = {
    'grouped_movies': grouped,
    'liked_movies': liked_movies
    }

    return render(request,'movies/allmovies.html', context)


def index(request):
    movies = Movie.objects.all().order_by('-release_date')

    liked_movies = []

    if request.user.is_authenticated:
        liked_movies = MovieLike.objects.filter(
            user=request.user,
            like=True
        ).values_list('movie_id', flat=True)

    context = {
        'movies': movies,
        'liked_movies': liked_movies
    }

    return render(request, 'movies/index.html', context)



def saludo(request, veces):
    saludo = 'Hola ' * veces
    personas = Person.objects.all()
    context = { 'saludo':saludo, 'lista':personas }
    return render(request,'movies/saludo.html', context=context )

def movie(request, movie_id):
    movie = Movie.objects.get(id=movie_id)

    movie_genres = movie.genres.all()

    all_movies = Movie.objects.exclude(id=movie_id)

    recommendations = []

    
    for m in all_movies:
        common = m.genres.filter(id__in=movie_genres).count()

        if common >= 2:
            recommendations.append(m)

  
    if len(recommendations) < 5:
        for m in all_movies:
            if m in recommendations:
                continue

            common = m.genres.filter(id__in=movie_genres).count()

            if common >= 1:
                recommendations.append(m)

            if len(recommendations) >= 5:
                break

    recommendations = recommendations[:5]

    return render(request, 'movies/movie.html', {
        'movie': movie,
        'recommendations': recommendations
    })


def movie_reviews(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    return render(request,'movies/reviews.html', context={'movie':movie } )


@login_required
def add_to_collection(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    # evitar duplicados
    if not Collection.objects.filter(user=request.user, movie=movie).exists():
        Collection.objects.create(user=request.user, movie=movie)

    return redirect(request.META.get('HTTP_REFERER', '/movies/'))

@login_required
def collections(request):
    items = Collection.objects.filter(user=request.user)

    return render(request, 'movies/collections.html', {
        'items': items
    })

def add_review(request, movie_id):
    form = None
    movie = Movie.objects.get(id=movie_id)
    if request.method == 'POST':
        form = MovieReviewForm(request.POST)
        if form.is_valid():
            rating = form.cleaned_data['rating']
            title  = form.cleaned_data['title']
            review = form.cleaned_data['review']
            movie_review = MovieReview(
                    movie=movie,
                    rating=rating,
                    title=title,
                    review=review,
                    user=request.user)
            movie_review.save()
            return HttpResponseRedirect(status=204,
                                headers={'HX-Trigger': 'listChanged'})
    else:
        form = MovieReviewForm()
        return render(request,
                  'movies/movie_review_form.html',
                  {'movie_review_form': form, 'movie':movie})
    


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            return render(request, 'movies/register.html', {
                'error': 'El usuario ya existe'
            })
        
        user = User.objects.create_user(username=username, password=password)
        user.save()

        return redirect('/users/login')


    return render(request, 'movies/register.html')



def actor_detail(request, person_id):
    person = Person.objects.get(id=person_id)

    api_key = "7fa3832690bdd23227468d436596dc4e" 


    url = f"https://api.themoviedb.org/3/person/{person.tmdb_id}?api_key={api_key}&language=en-US"
    response = requests.get(url)
    data = response.json()

    credits_url = f"https://api.themoviedb.org/3/person/{person.tmdb_id}/movie_credits?api_key={api_key}&language=en-US"
    credits_response = requests.get(credits_url)
    credits_data = credits_response.json()

    known_for = credits_data.get("cast", [])[:5]

    my_movies = Movie.objects.filter(credits=person)

    return render(request, 'movies/actor_detail.html', {
        'person': person,
        'data': data,
        'known_for': known_for,
        'my_movies': my_movies
    })

def update_tmdb_ids(request):
    api_key = "7fa3832690bdd23227468d436596dc4e"

    persons = Person.objects.filter(tmdb_id__isnull=True)

    for person in persons:
        url = f"https://api.themoviedb.org/3/search/person?api_key={api_key}&query={person.name}"

        response = requests.get(url)
        data = response.json()

        results = data.get("results")

        if results:
            person.tmdb_id = results[0]["id"]  
            person.save()

    return HttpResponse("Actores actualizados")