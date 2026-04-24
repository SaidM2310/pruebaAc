from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from movies.models import Movie, MovieReview, Person, MovieLike
from movies.forms import MovieReviewForm, MovieCommentForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Collection

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
# Create your views here.
def index(request):
    movies = Movie.objects.all()

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
    review_form = MovieReviewForm()
    print(request) 
    print(movie.title)
    context = {'movie':movie, 'saludo':'welcome', 'review_form':review_form, 'lista':[1,2,3,3,3] }
    return render(request,'movies/movie.html', context=context )


def movie_reviews(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    return render(request,'movies/reviews.html', context={'movie':movie } )


@login_required
def add_to_collection(request, movie_id):
    if request.method == 'POST':
        movie = Movie.objects.get(id=movie_id)

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
