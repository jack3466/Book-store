from django.shortcuts import render,redirect, get_object_or_404
from .models import  Books, User, BookRent,Buy
from django.shortcuts import render
from django.http import HttpResponse
from bapp import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib import messages
#from django. import index
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Books, User, BookRent,Buy
from paypal.standard.forms import PayPalPaymentsForm
from django.urls import reverse

from django.contrib import messages
from django.views import View

from django.http import JsonResponse
import json
from django.views.generic import DetailView







def base(request):
 # Pass the query string back to the template to display in the search input
    

    return render(request, 'base.html')

def main(request):

    b=Books.objects.all()
    if request.GET.get('q'):
      query = request.GET.get('q') 
      b = Books.objects.filter(title__icontains=query)  

   
    context={'b':b,}
    return render(request,'main.html',context)
from django.db.models import Avg

def detail(request, book_id):
    book = get_object_or_404(Books, pk=book_id)
    reviews = Review.objects.filter(book=book)
    context = {'d': book,'reviews': reviews}
    return render(request, 'detail.html', context)


def form(request):
    return render(request,'form.html')

def returned(request):
    return render(request,'returned.html')





#============================rent longic

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import User  # Import the User model
from .models import Books, BookRent
from django.utils import timezone

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Books, BookRent

def rent_book(request, book_id):
    book = get_object_or_404(Books, pk=book_id)

    if request.method == 'POST':
        user_id = request.POST.get('user')
        email = request.POST.get('email')
        rented_date = request.POST.get('rented_date')
        return_date = request.POST.get('return_date')

        # Perform actions with user_id

        messages.success(request, f"You have successfully rented '{book.title}'. You can now take the book.")
        return redirect('bapp:main')  # Redirect after successful renting

    # Continue with the rest of your GET logic
    return render(request, 'rent_book.html', {'book': book})




def calculate_fine(return_date):
    # Example: Calculate fine as $5 per day for late return
    days_overdue = (timezone.now().date() - return_date).days
    fine_amount = 5 * days_overdue
    return fine_amount

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Books

def book_detail(request, book_id):
    book = Books.objects.get(id=book_id)
    return render(request, 'book_detail.html', {'object': book})

#==========================================return book
import uuid
from django.contrib.auth.decorators import login_required

@login_required
def order(request, book_id):
    try:
        book_id = int(book_id)
    except ValueError:
        # Handle the case where book_id is not a valid integer
        return HttpResponse("Invalid book ID")

    # Get the current user instance
    current_user = request.user

    # Get the book instance based on the provided book_id
    book = Books.objects.get(pk=book_id)

    # Calculate the total amount for the selected book
    total_amount = book.price

    # Create an order for the current user and the selected book
    order = Buy.objects.create(user=current_user, product=book, quantity=1, price=total_amount)
    order.save()

    # PayPal payment dictionary
    paypal_dict = {
        "business": "sb-l7r2e28145955@business.example.com",
        "amount": total_amount,
        "invoice": str(uuid.uuid4()),
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return": request.build_absolute_uri(reverse('bapp:return_view')),
        "cancel_return": request.build_absolute_uri(reverse('bapp:cancel_view')),
        "custom": "premium_plan",
    }

    # Create the PayPal form
    form = PayPalPaymentsForm(initial=paypal_dict)

    # Render the order page with the form
    context = {"form": form, "total": total_amount}
    return render(request, "order.html", context)

def return_view(request):
    return render(request,'done.html')
def cancel_view(request):
    return render(request,'cancel.html')




from django.shortcuts import render
from .models import Review

def book_detail(request, book_id):
    book = Books.objects.get(pk=book_id)
    reviews = Review.objects.filter(book=book)
    is_available = book.book_available
    context = {
        'book': book,
        'reviews': reviews,
        'is_available': is_available
        
    }
    book = get_object_or_404(Books, pk=book)
    # Rest of your view logic goes here
    return render(request, 'book_detail.html', {'book': book})

# views.py

from django.shortcuts import get_object_or_404, redirect
from .models import Review
from .forms import ReviewForm

def edit_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('book_detail', book_id=review.book.id)
    else:
        form = ReviewForm(instance=review)
    return render(request, 'edit_review.html', {'form': form, 'review': review})

def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    if request.method == 'POST':
        review.delete()
        return redirect('book_detail', book_id=review.book.id)
    return render(request, 'delete_review.html', {'review': review})
from django.shortcuts import render, get_object_or_404, redirect
from .models import Books, Review
from .forms import ReviewForm

def add_review(request, book_id):
    book = get_object_or_404(Books, pk=book_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book

            # Use request.user inside the is_valid block
            review.user = request.user if request.user.is_authenticated else None

            review.save()
            return redirect('bapp:main')
    else:
        form = ReviewForm()
    return render(request, 'add_review.html', {'form': form, 'book': book})

from django.contrib import messages
from .forms import RentForm
def rent_book(request, book_id):
    book = get_object_or_404(Books, pk=book_id)
    if request.method == 'POST':
        form = RentForm(request.POST)
        if form.is_valid():
            rent_instance = form.save(commit=False)
            rent_instance.book_id = book_id
            rent_instance.rented_date = form.cleaned_data['rented_date']  # Set the rented_date from the form
            rent_instance.save()

            # Update the book availability
            book = Books.objects.get(pk=book_id)
            book.book_available = False
            book.save()

            messages.success(request, f"You have successfully rented '{book.title}'. You can now take the book.")

            # Redirect to the book detail page or any other appropriate page
            return redirect('bapp:detail', book_id=book_id)

    else:
        form = RentForm()

    return render(request, 'rent_book.html', {'form': form, 'book_id':book_id})




