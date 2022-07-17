from django.shortcuts import render, redirect 
from django.http import HttpResponse
from django.http import JsonResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .forms import QuizForm, QuestionForm
from django.forms import inlineformset_factory
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

# Create your views here.
from .models import *
from .forms import CreateUserForm
from .decorators import unauthenticated_user, allowed_users, admin_only

import secrets


def index(request):
    
    quiz = Quiz.objects.all()
    context = {'quiz' : quiz, 'user_type': '(Quiz Admin)' if request.user.is_staff else '(User)'}
    return render(request, "frontend/index.html", context=context)


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
			return redirect('index')
		else:
			messages.info(request, 'Username OR password is incorrect')

	context = {}
	return render(request, 'frontend/login.html', context)

def logoutUser(request):
	logout(request)
	return redirect('login')


def add_quiz(request):
    if request.method=="POST":
        form = QuizForm(data=request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.code = secrets.token_urlsafe(8)
            quiz.save()
            obj = form.instance
            return redirect('index')
    else:
        form=QuizForm()
    return render(request, "frontend/add_quiz.html", {'form':form})

def add_question(request):
    questions = Question.objects.all()
    questions = Question.objects.filter().order_by('-id')
    if request.method=="POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, "frontend/add_question.html")
    else:
        form=QuestionForm()
    return render(request, "frontend/add_question.html", {'form':form, 'questions':questions})

def delete_question(request, myid):
    question = Question.objects.get(id=myid)
    if request.method == "POST":
        question.delete()
        return redirect('/add_question')
    return render(request, "frontend/delete_question.html", {'question':question})


def add_options(request, myid):
    question = Question.objects.get(id=myid)
    QuestionFormSet = inlineformset_factory(Question, Answer, fields=('content','correct', 'question'), extra=4)
    if request.method=="POST":
        formset = QuestionFormSet(request.POST, instance=question)
        if formset.is_valid():
            formset.save()
            alert = True
            return render(request, "frontend/add_options.html", {'alert':alert})
    else:
        formset=QuestionFormSet(instance=question)
    return render(request, "frontend/add_options.html", {'formset':formset, 'question':question})
    

def results(request, myid):
    marks_all = Marks_Of_User.objects.all()
    context = []
    
    for marks in marks_all:
        mark = {'quiz': {}, 'user': '', 'score': 0}
        if(marks.quiz.id==myid):
            mark['quiz'] = marks.quiz
            mark['user'] = marks.user
            mark['score'] = marks.score
            context.append(mark)
    return render(request, "frontend/results.html", {'marks':context})

def delete_result(request, myid):
    marks = Marks_Of_User.objects.get(id=myid)
    if request.method == "POST":
        marks.delete()
        return redirect('/results')
    return render(request, "frontend/delete_result.html", {'marks':marks})

@login_required(login_url = '/login')
def quiz(request, myid):
    quiz = Quiz.objects.get(id=myid)
    return render(request, "frontend/quiz.html", {'quiz':quiz})

def quiz_data_view(request, myid):
    quiz = Quiz.objects.get(id=myid)
    questions = []
    for q in quiz.get_questions():
        answers = []
        for a in q.get_answers():
            answers.append(a.content)
        questions.append({str(q): answers})
    return JsonResponse({
        'data': questions,
        'time': quiz.time,
    })


def save_quiz_view(request, myid):
    if request.is_ajax():
        questions = []
        data = request.POST
        data_ = dict(data.lists())

        data_.pop('csrfmiddlewaretoken')

        for k in data_.keys():
            print('key: ', k)
            question = Question.objects.get(content=k)
            questions.append(question)

        user = request.user
        quiz = Quiz.objects.get(id=myid)

        score = 0
        marks = []
        correct_answer = None

        for q in questions:
            a_selected = request.POST.get(q.content)

            if a_selected != "":
                question_answers = Answer.objects.filter(question=q)
                for a in question_answers:
                    if a_selected == a.content:
                        if a.correct:
                            score += 1
                            correct_answer = a.content
                    else:
                        if a.correct:
                            correct_answer = a.content

                marks.append({str(q): {'correct_answer': correct_answer, 'answered': a_selected}})
            else:
                marks.append({str(q): 'not answered'})
     
        Marks_Of_User.objects.create(quiz=quiz, user=user, score=score)
        
        return JsonResponse({'passed': True, 'score': score, 'marks': marks})