from django.contrib.auth import get_user_model, login
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .models import Comment, Document, Notification, Project, Task, Timeline
from .permissions import IsManager
from .serializers import (
    CommentSerializer,
    DocumentSerializer,
    LogoutSerializer,
    NotificationSerializer,
    ProjectSerializer,
    TaskSerializer,
    TimelineSerializer,
    UserSerializer,
)
from .utils import format_error

# from django. get_object_or_404


User = get_user_model()


# Create your views here.
class SignupAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status_code": 201,
                        "user": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                {"error": format_error(serializer.errors), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            user = User.objects.filter(email=request.data["email"]).first()
            if user is None:
                return Response(
                    {
                        "error": "User does not exist",
                        "status_code": 404,
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            if user.password != request.data["password"]:
                return Response(
                    {
                        "error": "Invalid password",
                        "status_code": 400,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            login(request, user)
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "message": "User logged in successfully",
                    "status_code": 200,
                    "user": UserSerializer(user).data,
                    "access_token": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            return Response(
                {"message": "User logout successfully", "status_code": 200},
                status=status.HTTP_200_OK,
            )
        except TokenError as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )


# from pdb import set_trace; set_trace()
class ProjectModelViewSet(ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()

    def get_permissions(self):
        if self.action in ["create", "update", "destroy"]:
            self.permission_classes = [IsManager]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(
                data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status_code": 201,
                        "message": "Project created successfully",
                        "project": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                {"error": format_error(serializer.errors), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def list(self, request, *args, **kwargs):
        try:
            projects = Project.objects.all()
            filtered_projects = []
            for project in projects:
                if request.user in project.team_members.all():
                    filtered_projects.append(project)
            serializer = self.serializer_class(filtered_projects, many=True)
            if serializer.data != []:
                return Response(
                    {"status_code": 200, "projects": serializer.data},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"status_code": 404, "message": "No project found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def retrieve(self, request, *args, **kwargs):
        try:
            project = self.get_object()
            serializer = self.serializer_class(project)
            return Response(
                {"status_code": 200, "project": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Project.DoesNotExist:
            return Response(
                {"status_code": 404, "message": "No project found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            kwargs["partial"] = True
            project = self.get_object()
            serializer = self.serializer_class(project, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status_code": 200,
                        "message": "Project updated successfully",
                        "project": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"error": format_error(serializer.errors), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Project.DoesNotExist:
            return Response(
                {"status_code": 404, "message": "No project found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        try:
            project = self.get_object()
            project.delete()
            return Response(
                {"status_code": 200, "message": "Project deleted successfully"},
                status=status.HTTP_200_OK,
            )
        except Project.DoesNotExist:
            return Response(
                {"status_code": 404, "message": "No project found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )


class TaskModelViewSet(ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    def get_permissions(self):
        if self.action in ["create", "update", "destroy"]:
            self.permission_classes = [IsManager]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(
                data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status_code": 201,
                        "message": "Task created successfully",
                        "task": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            return Response(
                {"error": format_error(serializer.errors), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def list(self, request, *args, **kwargs):
        try:
            user = request.user
            tasks = Task.objects.filter(assignee=user)
            serializer = self.serializer_class(tasks, many=True)
            if serializer.data != []:
                return Response(
                    {"status_code": 200, "tasks": serializer.data},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"status_code": 404, "message": "No task found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def retrieve(self, request, *args, **kwargs):
        try:
            task = self.get_object()
            serializer = TaskSerializer(task)
            return Response(
                {"status_code": 200, "task": serializer.data}, status=status.HTTP_200_OK
            )
        except Task.DoesNotExist:
            return Response(
                {"status_code": 404, "message": "No task found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            task = self.get_object()
            serializer = TaskSerializer(task, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status_code": 200,
                        "message": "Task updated successfully",
                        "task": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"error": format_error(serializer.errors), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Task.DoesNotExist:
            return Response(
                {"status_code": 404, "message": "No task found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        try:
            task = self.get_object()
            task.delete()
            return Response(
                {"status_code": 200, "message": "Task deleted successfully"},
                status=status.HTTP_200_OK,
            )
        except Task.DoesNotExist:
            return Response(
                {"status_code": 404, "message": "No task found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )


class TaskAssignModelViewSet(ModelViewSet):
    permission_classes = [IsManager]
    queryset = Task.objects.all()
    lookup_field = "id"

    def create(self, request, *args, **kwargs):
        try:
            task = self.get_object()
            if request.data["assignee"]:
                serializer = TaskSerializer(task, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(
                        {
                            "status_code": 200,
                            "message": "Task assigned successfully",
                            "task": TaskSerializer(task).data,
                        },
                        status=status.HTTP_200_OK,
                    )
                return Response(
                    {"error": format_error(serializer.errors), "status_code": 400},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"error": "Assignee is required", "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Task.DoesNotExist:
            return Response(
                {"status_code": 404, "message": "No task found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )


class DocumentModelViewSet(ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DocumentSerializer
    queryset = Document.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status_code": 201,
                        "message": "Document created successfully",
                        "project": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                {"error": format_error(serializer.errors), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def list(self, request, *args, **kwargs):
        try:
            documents = Document.objects.all()
            serializer = self.serializer_class(documents, many=True)
            if serializer.data != []:
                return Response(
                    {"status_code": 200, "documents": serializer.data},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"status_code": 404, "message": "No document found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def retrieve(self, request, *args, **kwargs):
        try:
            document = self.get_object()
            serializer = DocumentSerializer(document)
            return Response(
                {"status_code": 200, "document": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Document.DoesNotExist:
            return Response(
                {"status_code": 404, "message": "No document found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            document = self.get_object()
            serializer = DocumentSerializer(document, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status_code": 200,
                        "message": "Document updated successfully",
                        "document": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"error": format_error(serializer.errors), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Document.DoesNotExist:
            return Response(
                {"status_code": 404, "message": "No document found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        try:
            document = self.get_object()
            document.delete()
            return Response(
                {"status_code": 200, "message": "Document deleted successfully"},
                status=status.HTTP_200_OK,
            )
        except Document.DoesNotExist:
            return Response(
                {"status_code": 404, "message": "No document found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CommentModelViewSet(ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status_code": 201,
                        "message": "Comment created successfully",
                        "comment": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                {"error": format_error(serializer.errors), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def list(self, request, *args, **kwargs):
        try:
            comments = Comment.objects.all()
            serializer = self.serializer_class(comments, many=True)
            if serializer.data != []:
                return Response(
                    {"status_code": 200, "comments": serializer.data},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"status_code": 404, "message": "No comment found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def retrieve(self, request, *args, **kwargs):
        try:
            comment = self.get_object()
            serializer = CommentSerializer(comment)
            return Response(
                {"status_code": 200, "comment": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Comment.DoesNotExist:
            return Response(
                {"status_code": 404, "message": "No comment found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            comment = self.get_object()
            user = request.user
            if comment.author == user:
                serializer = CommentSerializer(comment, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(
                        {
                            "status_code": 200,
                            "message": "Comment updated successfully",
                            "comment": serializer.data,
                        },
                        status=status.HTTP_200_OK,
                    )

                return Response(
                    {"error": format_error(serializer.errors), "status_code": 400},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {
                    "error": "You are not allowed to update someone's comment",
                    "status_code": 400,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Comment.DoesNotExist:
            return Response(
                {"status_code": 404, "message": "No comment found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        try:
            comment = self.get_object()
            user = request.user
            if comment.author == user:
                comment.delete()
                return Response(
                    {"status_code": 200, "message": "Comment deleted successfully"},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {
                    "error": "You are not allowed to delete someone's comment",
                    "status_code": 400,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Comment.DoesNotExist:
            return Response(
                {"status_code": 404, "message": "No comment found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CreateTimelineAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TimelineSerializer

    def get(self, request, *args, **kwargs):
        try:
            timelines = Timeline.objects.filter(project__id=kwargs["id"])
            if timelines:
                serializer = self.serializer_class(timelines, many=True)
                return Response(
                    {"status_code": 200, "timelines": serializer.data},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"status_code": 404, "message": "No timeline found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )


class NotificationModelViewSet(ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Notification.objects.all()
    lookup_field = "id"

    def list(self, request, *args, **kwargs):
        try:
            notifications = Notification.objects.filter(
                user__id=request.user.id, mark_read=False
            )
            if notifications:
                seriazlier = NotificationSerializer(notifications, many=True)
                return Response(
                    {"status_code": 200, "notifications": seriazlier.data},
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"status_code": 404, "message": "No notification found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            notification = self.get_object()
            mark_read = kwargs["mark_read"].lower()
            if mark_read == "true":
                notification.mark_read = True
            elif mark_read == "false":
                notification.mark_read = False
            else:
                return Response(
                    {"error": "Invalid mark read value", "status_code": 400},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            notification.save()
            return Response(
                {"status_code": 200, "message": "Notification marked as read"},
                status=status.HTTP_200_OK,
            )
        except Notification.DoesNotExist:
            return Response(
                {"status_code": 404, "message": "No notification found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserModelViewSet(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            if user:
                serializer = UserSerializer(user)
                return Response(
                    {
                        "status_code": 200,
                        "message": "User found",
                        "user": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"status_code": 404, "message": "No user found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "status_code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )
