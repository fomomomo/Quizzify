from django.urls import path
from . import views
urlpatterns = [
    path('register/', views.registerPage, name="register"),
	path('login/', views.loginPage, name="login"),  
	path('logout/', views.logoutUser, name="logout"),
    path('quiz-taker/', views.quiz_taker, name="quiz-taker"),
    path('quiz-admin/', views.quiz_admin, name="quiz-admin"),
    path('', views.home, name="home")
]