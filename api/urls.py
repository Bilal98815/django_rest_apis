from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView

from .views import (
    CommentModelViewSet,
    CreateTimelineAPIView,
    DocumentModelViewSet,
    LogoutAPIView,
    NotificationModelViewSet,
    ProjectModelViewSet,
    SignupAPIView,
    TaskAssignModelViewSet,
    TaskModelViewSet,
    UserModelViewSet,
)

router = routers.DefaultRouter()
router.register(r"projects", ProjectModelViewSet, basename="projects")
router.register(r"projects/<id>/", ProjectModelViewSet, basename="project_details")
router.register(r"tasks", TaskModelViewSet, basename="tasks")
router.register(r"tasks/<id>/", TaskModelViewSet, basename="task_details")
router.register(r"documents", DocumentModelViewSet, basename="documents")
router.register(r"documents/<id>/", DocumentModelViewSet, basename="document_details")
router.register(r"comments", CommentModelViewSet, basename="comments")
router.register(r"comments/<id>/", CommentModelViewSet, basename="comment_details")
router.register(r"notifications", NotificationModelViewSet, basename="notifications")

urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("user/", UserModelViewSet.as_view(), name="user_data"),
    path("register/", view=SignupAPIView.as_view(), name="register"),
    # path('login/', view=LoginAPIView.as_view(), name="login"),
    path("logout/", view=LogoutAPIView.as_view(), name="logout"),
    path(
        "tasks/<id>/assign/",
        view=TaskAssignModelViewSet.as_view({"post": "create"}),
        name="task_assign",
    ),
    path("timeline/<id>/", view=CreateTimelineAPIView.as_view(), name="timeline"),
    path(
        "notifications/<id>/<str:mark_read>/",
        view=NotificationModelViewSet.as_view({"put": "update"}),
        name="mark_notifications",
    ),
    path("", include(router.urls)),
]
