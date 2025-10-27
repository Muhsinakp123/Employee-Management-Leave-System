from django.urls import path

from elms import views

urlpatterns = [
    path('',views.login_View,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('signup/', views.signup, name='signup'),
    path('home/', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # --- Password Reset ---
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password/<int:user_id>/', views.reset_password, name='reset_password'),
    
    path('apply_leave/', views.apply_leave, name='apply_leave'),
    path('leaves/', views.leave_list, name='leave_list'),
    path('leaves/<int:pk>/', views.leave_detail, name='leave_detail'),
    path('leaves/<int:pk>/edit/', views.leave_edit, name='leave_edit'),
    path('leaves/<int:pk>/delete/', views.leave_delete, name='leave_delete'),
    path('admin/leaves/', views.admin_leave_list, name='admin_leave_list'),
    
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('profile/delete/', views.profile_delete, name='profile_delete'),
     
]
