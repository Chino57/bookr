from django.shortcuts import render

def index(request):
    message = "Welcome to Bookr"
    return render(request, "base.html", {"message": message })

def search(request):
    book = request.GET.get("book")
    return render(request, "result.html", {"book": book})