from django.contrib import admin
from django.urls import path,include

from .import views
	
urlpatterns = [
	path('',views.index,name="index"),
	path('about', views.about, name="AboutUs"),
    path('contact', views.contact, name="ContactUs"),
    path('tracker', views.tracker, name="TrackingStatus"),
    path('search', views.search, name="Search"),
    path('products <int:myid>', views.productView, name="ProductView"),
    path('checkout', views.checkout, name="checkout"),
    path('handlerequest', views.handlerequest, name="HandleRequest"),
	
	# ********************************Authentication****************
	path('auth_registration', views.auth_registration, name="auth_registration"),
    path('auth_save', views.auth_save, name="auth_save"),

    path('auth_login', views.auth_login, name="auth_login"),
    path('auth_login_check', views.auth_login_check, name="auth_login_check"),

    path('auth_logout', views.auth_logout, name="auth_logout"),

    path('reset', views.reset, name="reset"),
    path('reset_pass', views.reset_pass, name="reset_pass"),

    path('welcome',views.welcome,name="welcome"),
    path('delete',views.delete,name="delete"),
    path('edit',views.edit,name="edit"),
    path('update',views.update,name="update"),
   


]