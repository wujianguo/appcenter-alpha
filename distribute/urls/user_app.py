from django.urls import path
from distribute import views

urlpatterns = [
    path('<str:app_name>/distribute/packages', views.UserAppPackageList.as_view()),
    path('<str:app_name>/distribute/packages/<int:internal_build>', views.UserAppPackageDetail.as_view()),
    path('<str:app_name>/distribute/releases', views.UserAppReleaseList.as_view()),
    path('<str:app_name>/distribute/releases/env/<env>', views.UserAppReleaseList.as_view()),
    path('<str:app_name>/distribute/releases/<int:release_id>', views.UserAppReleaseDetail.as_view()),
]
