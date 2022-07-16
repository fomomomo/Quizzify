from django.shortcuts import render, redirect 
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import authenticate, login, logout

from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

# Create your views here.
from .models import *
from .forms import CreateUserForm
from .decorators import unauthenticated_user, allowed_users, admin_only


@unauthenticated_user
def registerPage(request):

	form = CreateUserForm()
	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')
			is_quiz_admin =request.POST.get('is_staff')
			name = 'quiz_admin'if is_quiz_admin else'quiz_taker'
			group = Group.objects.get(name=name)
			user.groups.add(group)

			messages.success(request, 'Account was created for ' + username)

			return redirect('login')
		

	context = {'form':form}
	return render(request, 'frontend/register.html', context)

@unauthenticated_user
def loginPage(request):

	if request.method == 'POST':
		username = request.POST.get('username')
		password =request.POST.get('password')

		user = authenticate(request, username=username, password=password)

		if user is not None:
			login(request, user)
			return redirect('home')
		else:
			messages.info(request, 'Username OR password is incorrect')

	context = {}
	return render(request, 'frontend/login.html', context)

def logoutUser(request):
	logout(request)
	return redirect('login')

@login_required(login_url='login')
@admin_only
def home(request):
	# orders = Order.objects.all()
	# customers = Customer.objects.all()

	# total_customers = customers.count()

	# total_orders = orders.count()
	# delivered = orders.filter(status='Delivered').count()
	# pending = orders.filter(status='Pending').count()

	context = {'orders':{}, 'customers':{},
	'total_orders':0,'delivered':0,
	'pending':0 }

	return render(request, 'frontend/dashboard.html', context)

def quiz_taker(request):
	context = {}
	return render(request, 'frontend/quiz_taker.html', context)

@login_required(login_url='login')
@admin_only
def quiz_admin(request):
	context = {}
	return render(request, 'frontend/quiz_admin.html', context)