from django.urls import path
from application import views

urlpatterns = [
    path('', views.ApplicationList.as_view()),
    path('<str:app_name>', views.ApplicationDetail.as_view()),
    # path('<str:app_name>/install', views.install),
    path('<str:app_name>/icon', views.ApplicationIcon.as_view()),
    path('<str:app_name>/people/collaborators', views.ApplicationUserList.as_view()),
    path('<str:app_name>/people/collaborators/<str:username>', views.ApplicationUserDetail.as_view()),
]
