from django.urls import path
from distribute import views

urlpatterns = [
    path('<str:org_name>/apps/<str:app_name>/distribute/packages', views.OrgAppPackageList.as_view()),
    path('<str:org_name>/apps/<str:app_name>/distribute/packages/<int:internal_build>', views.OrgAppPackageDetail.as_view()),
    path('<str:org_name>/apps/<str:app_name>/distribute/releases/env/<env>', views.OrgAppReleaseList.as_view()),
    path('<str:org_name>/apps/<str:app_name>/distribute/releases/<int:release_id>', views.OrgAppReleaseDetail.as_view()),
]
