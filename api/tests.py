from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from .models import Comment, Document, Profile, Project, Task, UserModel
from .utils import generate_file, generate_image


class AuthenticationTestCases(APITestCase):
    def setUp(self):
        self.auth_client = APIClient()
        image = generate_image()
        self.user = UserModel.objects.create_user(
            username="test",
            email="test@gmail.com",
            password="12345",
            password2="12345",
        )
        Profile.objects.create(
            user=self.user,
            profile_picture=image,
            roles="manager",
            contact_number="03001234567",
        )

        self.auth_client.force_authenticate(self.user)

        self.un_auth_client = APIClient()

    def test_signup_api(self):

        image = generate_image()
        data = {
            "username": "test",
            "email": "test@gmail.com",
            "password": "12345",
            "password2": "12345",
            "user_profile.profile_picture": image,
            "user_profile.roles": "manager",
            "user_profile.contact_number": "03001234567",
        }

        response = self.un_auth_client.post(reverse("register"), data)
        response_data = response.json()
        self.assertEqual(
            response_data["error"]["email"][0], "user with this Email already exists."
        )

        image = generate_image()

        data["email"] = "omar@gmail.com"
        data["username"] = "omar"
        data["user_profile.profile_picture"] = image

        response = self.client.post(reverse("register"), data)
        self.assertEqual(response.status_code, 201)

    def test_login_api(self):
        data = {"email": "test@gmail.com", "password": "12345"}

        response = self.un_auth_client.post(reverse("login"), data)
        self.assertEqual(response.status_code, 200)

    def test_logout_api(self):
        login_data = {"email": "test@gmail.com", "password": "12345"}

        login_response = self.un_auth_client.post(reverse("login"), login_data)

        self.assertEqual(login_response.status_code, 200)
        header = {"Authorization": "Bearer " + login_response.data["access"]}
        data = {"refresh": login_response.data["refresh"]}

        response = self.client.post(reverse("logout"), data, headers=header)
        response_data = response.json()
        self.assertEqual(response_data["message"], "User logout successfully")


class ProjectTestCases(APITestCase):
    def setUp(self):
        self.auth_client = APIClient()
        self.un_auth_client = APIClient()
        image = generate_image()
        self.user = UserModel.objects.create_user(
            username="test",
            email="test@gmail.com",
            password="12345",
            password2="12345",
        )
        developer = UserModel.objects.create_user(
            username="test1",
            email="test1@gmail.com",
            password="12345",
            password2="12345",
        )
        Profile.objects.create(
            user=self.user,
            profile_picture=image,
            roles="manager",
            contact_number="03001234567",
        )
        Profile.objects.create(
            user=developer,
            profile_picture=image,
            roles="developer",
            contact_number="03001234567",
        )

        self.auth_client.force_authenticate(self.user)

        project = Project.objects.create(
            title="Test Project",
            description="abc",
            start_date="2021-09-01",
            end_date="2024-09-30",
        )
        project.team_members.add(2)
        project.save()

        self.login_credentials = {"email": "test1@gmail.com", "password": "12345"}

    def test_create_project_api(self):

        data = {
            "title": "Test Project",
            "description": "abc",
            "start_date": "2021-09-01",
            "end_date": "2024-09-30",
            "team_members": [2],
        }

        response = self.auth_client.post("/api/projects/", data)
        self.assertEqual(response.status_code, 201)

    def test_get_project_api(self):

        login_response = self.un_auth_client.post(
            reverse("login"), self.login_credentials
        )

        header = {"Authorization": "Bearer " + login_response.data["access"]}

        response = self.un_auth_client.get("/api/projects/", headers=header)
        response_data = response.json()
        self.assertEqual(len(response_data["projects"]), 1)

    def test_get_project_details_api(self):

        response = self.auth_client.get("/api/projects/1/")
        self.assertEqual(response.status_code, 200)

    def test_update_project_api(self):

        response = self.auth_client.put(
            "/api/projects/1/", {"title": "updated project"}
        )
        response_data = response.json()
        self.assertEqual(response_data["message"], "Project updated successfully")

    def test_delete_project_api(self):

        response = self.auth_client.delete("/api/projects/1/")
        response_data = response.json()
        self.assertEqual(response_data["message"], "Project deleted successfully")


class TaskTestCases(APITestCase):
    def setUp(self):
        self.auth_client = APIClient()
        self.un_auth_client = APIClient()
        image = generate_image()
        self.user = UserModel.objects.create_user(
            username="test",
            email="test@gmail.com",
            password="12345",
            password2="12345",
        )
        developer = UserModel.objects.create_user(
            username="test1",
            email="test1@gmail.com",
            password="12345",
            password2="12345",
        )
        Profile.objects.create(
            user=self.user,
            profile_picture=image,
            roles="manager",
            contact_number="03001234567",
        )
        Profile.objects.create(
            user=developer,
            profile_picture=image,
            roles="developer",
            contact_number="03001234567",
        )

        self.auth_client.force_authenticate(self.user)

        project = Project.objects.create(
            title="Test Project",
            description="abc",
            start_date="2021-09-01",
            end_date="2024-09-30",
        )
        project.team_members.add(2)
        project.save()

        Task.objects.create(
            title="Test Task",
            description="abc",
            status="open",
            project=project,
            assignee=developer,
        )

        self.login_credentials = {"email": "test1@gmail.com", "password": "12345"}

    def test_create_task_api(self):
        login_response = self.un_auth_client.post(
            reverse("login"), self.login_credentials
        )

        self.assertEqual(login_response.status_code, 200)
        header = {"Authorization": "Bearer " + login_response.data["access"]}

        data = {
            "title": "Test Task",
            "description": "abc",
            "status": "open",
            "project": 1,
            "assignee": 2,
        }

        response = self.un_auth_client.post("/api/tasks/", data, headers=header)
        response_data = response.json()
        self.assertEqual(
            response_data["error"], "You do not have permission to perform this action."
        )

        response = self.auth_client.post("/api/tasks/", data)
        response_data = response.json()
        self.assertEqual(response_data["message"], "Task created successfully")

    def test_get_tasks_api(self):
        login_response = self.un_auth_client.post(
            reverse("login"), self.login_credentials
        )

        self.assertEqual(login_response.status_code, 200)
        header = {"Authorization": "Bearer " + login_response.data["access"]}
        response = self.un_auth_client.get("/api/tasks/", headers=header)
        self.assertEqual(response.status_code, 200)

    def test_update_task_api(self):

        response = self.auth_client.put("/api/tasks/1/", {"title": "updated task"})
        response_data = response.json()
        self.assertEqual(response_data["message"], "Task updated successfully")

    def test_get_task_details_api(self):

        response = self.auth_client.get("/api/tasks/1/")
        self.assertEqual(response.status_code, 200)

    def test_delete_task_api(self):

        response = self.auth_client.delete("/api/tasks/1/")
        response_data = response.json()
        self.assertEqual(response_data["message"], "Task deleted successfully")


class TaskAssignTestCase(APITestCase):
    def setUp(self):
        self.auth_client = APIClient()
        self.un_auth_client = APIClient()
        image = generate_image()
        self.user = UserModel.objects.create_user(
            username="test",
            email="test@gmail.com",
            password="12345",
            password2="12345",
        )
        developer = UserModel.objects.create_user(
            username="test1",
            email="test1@gmail.com",
            password="12345",
            password2="12345",
        )
        Profile.objects.create(
            user=self.user,
            profile_picture=image,
            roles="manager",
            contact_number="03001234567",
        )
        Profile.objects.create(
            user=developer,
            profile_picture=image,
            roles="developer",
            contact_number="03001234567",
        )

        self.auth_client.force_authenticate(self.user)

        project = Project.objects.create(
            title="Test Project",
            description="abc",
            start_date="2021-09-01",
            end_date="2024-09-30",
        )
        project.team_members.add(2)
        project.save()

        Task.objects.create(
            title="Test Task",
            description="abc",
            status="open",
            project=project,
            assignee=developer,
        )

        self.login_credentials = {"email": "test1@gmail.com", "password": "12345"}

    def test_task_assign_api(self):

        image = generate_image()

        user3 = UserModel.objects.create_user(
            username="test3",
            email="test3@gmail.com",
            password="12345",
            password2="12345",
        )
        Profile.objects.create(
            user=user3,
            profile_picture=image,
            roles="manager",
            contact_number="03001234567",
        )

        login_response = self.un_auth_client.post(
            reverse("login"), self.login_credentials
        )

        header = {"Authorization": "Bearer " + login_response.data["access"]}

        response = self.un_auth_client.post(
            "/api/tasks/1/assign/", {"assignee": user3.id}, headers=header
        )
        response_data = response.json()
        self.assertEqual(
            response_data["error"], "You do not have permission to perform this action."
        )

        response = self.auth_client.post("/api/tasks/1/assign/", {"assignee": user3.id})
        response_data = response.json()
        self.assertEqual(response_data["message"], "Task assigned successfully")


class DocumentTestCases(APITestCase):
    def setUp(self):
        self.auth_client = APIClient()
        self.un_auth_client = APIClient()
        image = generate_image()
        self.user = UserModel.objects.create_user(
            username="test",
            email="test@gmail.com",
            password="12345",
            password2="12345",
        )
        Profile.objects.create(
            user=self.user,
            profile_picture=image,
            roles="developer",
            contact_number="03001234567",
        )

        self.auth_client.force_authenticate(self.user)

        project = Project.objects.create(
            title="Test Project",
            description="abc",
            start_date="2021-09-01",
            end_date="2024-09-30",
        )
        project.save()

        Document.objects.create(
            name="Test Document",
            description="abc",
            file=generate_file(),
            version=1,
            project=project,
        )

    def test_create_document_api(self):

        data = {
            "name": "Messages.txt",
            "description": "abc",
            "file": generate_file(),
            "version": 1,
            "project": 1,
        }

        response = self.auth_client.post("/api/documents/", data)
        response_data = response.json()
        self.assertEqual(
            response_data["error"]["version"][0],
            "document with this Version already exists.",
        )

        data["version"] = 2
        data["file"] = generate_file()

        response = self.auth_client.post("/api/documents/", data)
        response_data = response.json()
        self.assertEqual(response_data["message"], "Document created successfully")

    def test_get_documents_api(self):

        response = self.auth_client.get("/api/documents/")
        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertEqual(len(response_data["documents"]), 1)

    def test_update_documents_api(self):
        response = self.auth_client.put(
            "/api/documents/1/", {"name": "updated document"}
        )
        response_data = response.json()
        self.assertEqual(response_data["message"], "Document updated successfully")

    def test_get_doc_details_api(self):

        response = self.auth_client.get("/api/documents/2/")
        self.assertEqual(response.status_code, 400)

        response = self.auth_client.get("/api/documents/1/")
        self.assertEqual(response.status_code, 200)

    def test_delete_doc_api(self):
        response = self.auth_client.delete("/api/documents/1/")
        response_data = response.json()
        self.assertEqual(response_data["message"], "Document deleted successfully")


class CommentTestCases(APITestCase):
    def setUp(self):
        self.auth_client = APIClient()
        self.un_auth_client = APIClient()
        image = generate_image()
        self.user = UserModel.objects.create_user(
            username="test",
            email="test@gmail.com",
            password="12345",
            password2="12345",
        )
        Profile.objects.create(
            user=self.user,
            profile_picture=image,
            roles="developer",
            contact_number="03001234567",
        )

        developer = UserModel.objects.create_user(
            username="test1",
            email="test1@gmail.com",
            password="12345",
            password2="12345",
        )
        Profile.objects.create(
            user=developer,
            profile_picture=image,
            roles="developer",
            contact_number="03001234567",
        )

        self.auth_client.force_authenticate(self.user)

        project = Project.objects.create(
            title="Test Project",
            description="abc",
            start_date="2021-09-01",
            end_date="2024-09-30",
        )
        project.save()

        task = Task.objects.create(
            title="Test Task",
            description="abc",
            status="open",
            project=project,
            assignee=developer,
        )
        Comment.objects.create(
            text="This is a test comment", author=self.user, project=project, task=task
        )

        self.login_credentials = {"email": "test1@gmail.com", "password": "12345"}

    def test_create_comment_api(self):
        data = {"text": "This is a test comment", "author": 2, "task": 1, "project": 1}

        response = self.auth_client.post("/api/comments/", data)
        response_data = response.json()
        self.assertEqual(response_data["message"], "Comment created successfully")

    def test_get_all_comments_api(self):
        response = self.auth_client.get("/api/comments/")
        self.assertEqual(response.status_code, 200)

        response.data = response.json()
        self.assertEqual(len(response.data["comments"]), 1)

    def test_get_comment_details_api(self):
        response = self.auth_client.get("/api/comments/2/")
        self.assertEqual(response.status_code, 400)

        response = self.auth_client.get("/api/comments/1/")
        self.assertEqual(response.status_code, 200)

    def test_update_comments_api(self):
        response = self.auth_client.put("/api/comments/1/", {"text": "updated comment"})
        response_data = response.json()
        self.assertEqual(response_data["message"], "Comment updated successfully")

    def test_delete_comment_api(self):

        login_response = self.un_auth_client.post(
            reverse("login"), self.login_credentials
        )
        self.assertEqual(login_response.status_code, 200)

        header = {"Authorization": "Bearer " + login_response.data["access"]}

        response = self.un_auth_client.delete("/api/comments/1/", headers=header)
        response_data = response.json()
        self.assertEqual(
            response_data["error"], "You are not allowed to delete someone's comment"
        )

        response = self.auth_client.delete("/api/comments/1/")
        response_data = response.json()
        self.assertEqual(response_data["message"], "Comment deleted successfully")


class TimelineTestCases(APITestCase):
    def setUp(self):
        self.auth_client = APIClient()
        image = generate_image()
        self.user = UserModel.objects.create_user(
            username="test",
            email="test@gmail.com",
            password="12345",
            password2="12345",
        )
        Profile.objects.create(
            user=self.user,
            profile_picture=image,
            roles="manager",
            contact_number="03001234567",
        )

        self.auth_client.force_authenticate(self.user)

        project = Project.objects.create(
            title="Test Project",
            description="abc",
            start_date="2021-09-01",
            end_date="2024-09-30",
        )
        project.save()

    def test_get_timelines_api(self):
        response = self.auth_client.get("/api/timeline/1/")
        response_data = response.json()
        self.assertEqual(len(response_data["timelines"]), 1)

        self.assertEqual(response.status_code, 200)

    def test_create_timeline_api(self):

        temp_user = UserModel.objects.create_user(
            username="test2",
            email="test2@gmail.com",
            password="12345",
            password2="12345",
        )
        Profile.objects.create(
            user=temp_user,
            profile_picture=generate_image(),
            roles="developer",
            contact_number="03001234567",
        )

        data = {
            "title": "Test Task",
            "description": "abc",
            "status": "open",
            "project": 1,
            "assignee": 2,
        }

        response = self.auth_client.post("/api/tasks/", data)
        self.assertEqual(response.status_code, 201)

        response = self.auth_client.get("/api/timeline/1/")
        response_data = response.json()
        self.assertEqual(len(response_data["timelines"]), 2)


class NotificationTestCases(APITestCase):
    def setUp(self):
        self.auth_client = APIClient()
        self.un_auth_client = APIClient()
        image = generate_image()
        self.user = UserModel.objects.create_user(
            username="test",
            email="test@gmail.com",
            password="12345",
            password2="12345",
        )
        developer = UserModel.objects.create_user(
            username="test1",
            email="test1@gmail.com",
            password="12345",
            password2="12345",
        )
        Profile.objects.create(
            user=self.user,
            profile_picture=image,
            roles="manager",
            contact_number="03001234567",
        )
        Profile.objects.create(
            user=developer,
            profile_picture=image,
            roles="developer",
            contact_number="03001234567",
        )
        user3 = UserModel.objects.create_user(
            username="test1",
            email="test2@gmail.com",
            password="12345",
            password2="12345",
        )
        Profile.objects.create(
            user=user3,
            profile_picture=generate_image(),
            roles="developer",
            contact_number="03001234567",
        )

        self.auth_client.force_authenticate(self.user)

        project = Project.objects.create(
            title="Test Project",
            description="abc",
            start_date="2021-09-01",
            end_date="2024-09-30",
        )
        project.team_members.add(2)
        project.save()

        Task.objects.create(
            title="Test Task",
            description="abc",
            status="open",
            project=project,
            assignee=developer,
        )

        self.login_credentials = {"email": "test2@gmail.com", "password": "12345"}

    def test_get_notification_api(self):
        response = self.auth_client.get("/api/notifications/")
        self.assertEqual(response.status_code, 404)

        response = self.auth_client.post("/api/tasks/1/assign/", {"assignee": 3})
        self.assertEqual(response.status_code, 200)

        login_response = self.un_auth_client.post(
            reverse("login"), self.login_credentials
        )
        self.assertEqual(login_response.status_code, 200)

        header = {"Authorization": "Bearer " + login_response.data["access"]}

        response = self.un_auth_client.get("/api/notifications/", headers=header)
        response_data = response.json()
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response_data["notifications"]), 1)

    def test_mark_notification_api(self):

        response = self.auth_client.post("/api/tasks/1/assign/", {"assignee": 3})
        self.assertEqual(response.status_code, 200)

        response = self.un_auth_client.post(reverse("login"), self.login_credentials)
        self.assertEqual(response.status_code, 200)

        header = {"Authorization": "Bearer " + response.data["access"]}

        response = self.un_auth_client.put("/api/notifications/1/rfrf/", headers=header)
        self.assertEqual(response.status_code, 400)

        response = self.un_auth_client.put("/api/notifications/1/True/", headers=header)
        response_data = response.json()
        self.assertEqual(response_data["message"], "Notification marked as read")

        response = self.un_auth_client.get("/api/notifications/", headers=header)
        response_data = response.json()
        self.assertEqual(response_data["message"], "No notification found")


class GetUserDataTestCase(APITestCase):
    def setUp(self):
        self.auth_client = APIClient()
        self.unauth_client = APIClient()
        image = generate_image()
        self.user = UserModel.objects.create_user(
            username="test",
            email="test@gmail.com",
            password="12345",
            password2="12345",
        )
        Profile.objects.create(
            user=self.user,
            profile_picture=image,
            roles="manager",
            contact_number="03001234567",
        )

        self.auth_client.force_authenticate(self.user)

    def test_get_data_api(self):
        response = self.unauth_client.get("/api/user/")
        self.assertEqual(response.status_code, 401)

        response = self.auth_client.get("/api/user/")
        response_data = response.json()
        self.assertEqual(response_data["message"], "User found")
