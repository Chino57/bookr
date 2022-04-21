from django.shortcuts import render,get_object_or_404, redirect
from django.contrib import messages
from django.utils.timezone import now

from .models import Book, Review, Contributor, Publisher
from .utils import average_rating

from .forms import SearchForm, PublisherForm, ReviewForm


def index(request):
    return render(request, "base.html")


def book_search(request):
    search_text = request.GET.get("search", "")
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


def review_edit(request, book_pk, review_pk=None):
    book = get_object_or_404(Book, pk=book_pk)
    if review_pk is not None:
        review = get_object_or_404(Review, book_id=book_pk, pk=review_pk)
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

