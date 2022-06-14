from django.shortcuts import render,get_object_or_404, redirect
from django.contrib import messages
from django.utils.timezone import now
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.exceptions import PermissionDenied

from .models import Book, Review, Contributor, Publisher
from .utils import average_rating

from .forms import SearchForm, PublisherForm, ReviewForm, BookMediaForm
from io import BytesIO
from PIL import Image
from django.core.files.images import ImageFile


def is_staff_user(user):
    return user.is_staff


def index(request):
    return render(request, "base.html")


def book_search(request):
    search_text = request.GET.get("search", "")
    search_history = request.session.get('search_history', [])
    form = SearchForm(request.GET)
    books = set()

    if form.is_valid() and form.cleaned_data["search"]:
        search = form.cleaned_data["search"]
        search_in = form.cleaned_data.get("search_in") or "title"
        if search_in == "title":
            books = Book.objects.filter(title__icontains=search)
        else:
            fname_contributors = Contributor.objects.filter(first_names__icontains=search)
            for contributor in fname_contributors:
                for book in contributor.book_set.all():
                    books.add(book)
        lname_contributors = Contributor.objects.filter(last_names__icontains=search)
        for contributor in lname_contributors:
            for book in contributor.book_set.all():
                book.add(book)
        if request.user.is_authenticated:
            search_history.append([search_in, search])
            request.session['search_history'] = search_history
    elif search_history:
        initial = dict(search=search_text, search_in=search_history[-1][0])
        form = SearchForm(initial=initial)
    return render(request, "reviews/search-results.html", {"form": form, "search_text": search_text, "books": books})


def book_list(request):
    books = Book.objects.all()
    book_list = []
    for book in books:
        reviews = book.review_set.all()
        if reviews:
            book_rating = average_rating([review.rating for review in reviews])
            number_of_reviews = len(reviews)
        else:
            book_rating = None
            number_of_reviews = 0
        book_list.append({'book': book, 'book_rating': book_rating, 'number_of_reviews': number_of_reviews})

    context = {'book_list': book_list}

    return render(request, 'reviews/books_list.html', context)


def book_detail(request,pk):
    book = get_object_or_404(Book,pk=pk)
    reviews = book.review_set.all()
    if reviews:
        book_rating = average_rating([review.rating for review in reviews])
        context = {"book": book, "book_rating": book_rating, "reviews": reviews}
    else:
        context = {"book": book, "book_rating": None, "reviews": None }

    if request.user.is_authenticated:
        max_viewed_books_length = 10
        viewed_books = request.session.get('viewed_books', [])
        viewed_book = [book.id, book.title]
        if viewed_book in viewed_books:
            viewed_books.pop(viewed_books.index(viewed_book))
        viewed_books.insert(0, viewed_book)
        viewed_books = viewed_books[:max_viewed_books_length]
        request.session['viewed_books'] = viewed_books
    return render(request, 'reviews/book_details.html', context)


def form_example(request):
    initial = {"email": "user@example.com"}
    if request.method == "POST":
        form = OrderForm(request.POST, initial=initial)
    else:
        form = OrderForm(initial=initial)

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            for name, value in form.cleaned_data.items():
                print("{}: ({}) {}".format(name, type(value), value))

    return render(request, "reviews/form-example.html", {"method": request.method, "form": form})


@user_passes_test(is_staff_user)
def publisher_edit(request, pk=None):
    if pk is not None:
        publisher = get_object_or_404(Publisher, pk=pk)
    else:
        publisher = None
    if request.method == "POST":
        form = PublisherForm(request.POST, instance=publisher)
        if form.is_valid():
            updated_publisher = form.save()
            if publisher is None:
                messages.success(request, "Publisher \"{}\" was created.".format(updated_publisher))
            else:
                messages.success(request, "Publisher \"{}\" was updated.".format(updated_publisher))
            return redirect("publisher_edit", updated_publisher.pk)
    else:
        form = PublisherForm(instance=publisher)
        return render(request, "reviews/instance-form.html", {"instance": publisher,"model_type": "Publisher", "form": form})


@login_required
def review_edit(request, book_pk, review_pk=None):
    book = get_object_or_404(Book, pk=book_pk)
    if review_pk is not None:
        review = get_object_or_404(Review, book_id=book_pk, pk=review_pk)
        user = request.user
        if not user.is_staff and review.creator.id != user.id:
            raise PermissionDenied
    else:
        review = None

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)

        if form.is_valid():
            updated_review = form.save(False)
            updated_review.book = book
            if review is None:
                messages.success(request,"Review for \"{}\" was created".format(book))
            else:
                updated_review.date_edited = now()
                updated_review.save()
                messages.success(request, "Review for \"{}\" was updated".format(book))
            return redirect("book_detail", book_pk)

    else:
        form = ReviewForm(instance=review)

    return render(request, "reviews/instance-form.html", {"instance": review, "model_type": "Review", "form": form,
                                                          "related_model_type": Book, "related_instance": book})


@login_required
def book_media(request,pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        form = BookMediaForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            book = form.save(False)
            cover = form.cleaned_data.get("cover")
            if cover:
                image = Image.open(cover)
                image.thumbnail((300, 300))
                image_data = BytesIO()
                image.save(fp=image_data, format=cover.image.format)
                image_file = ImageFile(image_data)
                book.cover.save(cover.name, image_file)
                book.save()
                messages.success(request, "Book \"{}\" was successfully updated".format(book))
            return redirect("book_detail", pk)
    else:
        form = BookMediaForm(instance=book)
    return render(request, "reviews/instance-form.html", {"form": form, "instance": book, "model_type": "Book"})
