from django.urls import path
from organization import views

urlpatterns = [
    path('', views.OrganizationList.as_view()),
    path('<str:org_name>', views.OrganizationDetail.as_view(), name='org-detail'),
    path('<str:org_name>/icon', views.OrganizationIcon.as_view(), name='org-icon'),
    path('<str:org_name>/people/collaborators', views.OrganizationUserList.as_view()),
    path('<str:org_name>/people/collaborators/<str:username>', views.OrganizationUserDetail.as_view(), name='org-user'),
    path('<str:org_name>/apps', views.OrgApplicationList.as_view()),
    path('<str:org_name>/apps/<str:app_name>/icon', views.OrgApplicationIcon.as_view()),
    path('<str:org_name>/apps/<str:app_name>', views.OrgApplicationDetail.as_view()),
]
