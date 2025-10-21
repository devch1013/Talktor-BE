from django.urls import path
from api.project.views import SubjectViewSet, MaterialViewSet

urlpatterns = [
    # 과목 관련 API
    path(
        "subjects/",
        SubjectViewSet.as_view({"get": "list", "post": "create"}),
        name="subject-list-create",
    ),
    path(
        "subjects/<int:pk>/",
        SubjectViewSet.as_view({
            "get": "retrieve",
            "put": "update",
            "patch": "partial_update",
            "delete": "destroy"
        }),
        name="subject-detail",
    ),

    # 학습 자료 관련 API
    path(
        "materials/",
        MaterialViewSet.as_view({"get": "list", "post": "create"}),
        name="material-list-create",
    ),
    path(
        "materials/<int:pk>/",
        MaterialViewSet.as_view({
            "get": "retrieve",
            "put": "update",
            "patch": "partial_update",
            "delete": "destroy"
        }),
        name="material-detail",
    ),
]
