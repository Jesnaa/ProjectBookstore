from django.urls import path
from . import views

urlpatterns = [
    path('login/login/register/',views.register,name='register'),
    # path('login/login/register/register/reg',views.reg,name='reg'),
    path('',views.index,name='index'),
    path('login/',views.login,name='login'),
    path('logout/', views.logout, name='logout'),
    path('changepassword/', views.changepassword, name='changepassword'),
     path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    path('resetPassword/', views.resetPassword, name='resetPassword'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('profile/',views.profile,name='profile'),
    path('profile/update', views.profile_update, name='profile_update'),
    path('profile/add_address', views.add_address, name='add_address'),

]
