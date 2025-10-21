from django.urls import path

from api.project.views import MaterialViewSet, ProjectViewSet

urlpatterns = [
    # 프로젝트 관련 API
    path(
        "",
        ProjectViewSet.as_view({"get": "list", "post": "create"}),
        name="project-list-create",
    ),
    path(
        "/<int:project_id>",
        ProjectViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="project-detail",
    ),
    # 학습 자료 관련 API
    path(
        "/materials/<str:material_id>",
        MaterialViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="material-detail",
    ),
    path(
        "/<int:project_id>/materials",
        MaterialViewSet.as_view({"get": "list", "post": "create"}),
        name="material-list-create",
    ),
]
