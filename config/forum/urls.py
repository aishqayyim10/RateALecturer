from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('lecturer/add/', views.add_lecturer, name='add_lecturer'),
    path('lecturer/<int:lecturer_id>/', views.lecturer_detail, name='lecturer_detail'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='forum/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('review/<int:review_id>/comment/', views.add_comment, name='add_comment'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('review/<int:review_id>/upvote/', views.upvote_review, name='upvote_review'),
    path('review/<int:review_id>/downvote/', views.downvote_review, name='downvote_review'),
    path('profile/', views.profile, name='profile'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('lecturer/<int:lecturer_id>/delete/', views.delete_lecturer, name='delete_lecturer'),
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='forum/password_reset.html'), name='password_reset'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='forum/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='forum/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='forum/password_reset_complete.html'), name='password_reset_complete'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('user/<str:username>/', views.public_profile, name='public_profile'),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
]

