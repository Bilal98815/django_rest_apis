from django.test import TestCase

from ..models import (
    Comment,
    Document,
    Notification,
    Profile,
    Project,
    Task,
    Timeline,
    UserModel,
)
from ..utils import generate_file, generate_image


class UserModelTestCases(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            username="testuser",
            email="testuser@gmail.com",
            password="password123",
            password2="password123",
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, "testuser@gmail.com")
        self.assertEqual(self.user.username, "testuser")
        self.assertTrue(self.user.check_password("password123"))

        user = UserModel.objects.create_user(
            username="testuser2",
            email="test2@gmail.com",
            password="12345",
            password2="12345",
        )

        self.assertEqual(user.email, "test2@gmail.com")

    def test_user_string_representation(self):
        self.assertEqual(str(self.user), "testuser@gmail.com")

    def test_delete_user(self):
        self.user.delete()
        self.assertEqual(UserModel.objects.count(), 0)


class ProfileTestCase(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            username="testuser",
            email="testuser@gmail.com",
            password="password123",
            password2="password123",
        )

        self.profile = Profile.objects.create(
            user=self.user,
            profile_picture=generate_image(),
            roles="developer",
            contact_number="01234567890",
        )

    def test_profile_creation(self):
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.roles, "developer")
        self.assertEqual(str(self.profile.contact_number), "01234567890")

    def test_profile_string_representation(self):
        self.assertEqual(str(self.profile), "Profile of testuser")

    def test_profile_picture_upload(self):
        self.assertTrue("test_image" in self.profile.profile_picture.url)


class ProjectTestCase(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            username="testuser",
            email="testuser@gmail.com",
            password="password123",
            password2="password123",
        )
        self.project = Project.objects.create(
            title="Test Project",
            description="Test Description",
            start_date="2021-09-01",
            end_date="2024-09-30",
        )
        self.project.team_members.add(self.user)

    def test_project_creation(self):
        self.assertEqual(self.project.title, "Test Project")

    def test_project_string_representation(self):
        self.assertEqual(str(self.project), "Project: Test Project")

    def test_date_matching(self):
        self.assertTrue(self.project.start_date < self.project.end_date)

    def test_project_team_members(self):
        team_members = self.project.team_members.all()
        self.assertEqual(len(team_members), 1)
        self.assertIn(self.user, team_members)

    def test_remove_team_member(self):
        self.project.team_members.remove(self.user)
        self.assertNotIn(self.user, self.project.team_members.all())


class TaskTestCase(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            username="testuser",
            email="testuser@gmail.com",
            password="password123",
            password2="password123",
        )
        self.project = Project.objects.create(
            title="Test Project",
            description="Test Description",
            start_date="2021-09-01",
            end_date="2024-09-30",
        )
        self.task = Task.objects.create(
            title="Test Task",
            description="Test Task Description",
            status="open",
            project=self.project,
            assignee=self.user,
        )

    def test_task_creation(self):
        self.assertEqual(self.task.title, "Test Task")
        self.assertEqual(self.task.description, "Test Task Description")
        self.assertEqual(self.task.status, "open")
        self.assertEqual(self.task.project, self.project)
        self.assertEqual(self.task.assignee, self.user)

    def test_task_string_representation(self):
        self.assertEqual(str(self.task), "Task title: Test Task")

    def test_task_without_assignee(self):
        task = Task.objects.create(
            title="Task without Assignee",
            description="Description",
            status="open",
            project=self.project,
            assignee=None,
        )
        self.assertIsNone(task.assignee)


class DocumentTestCase(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
            password2="password123",
        )
        self.project = Project.objects.create(
            title="Test Project",
            description="Test Description",
            start_date="2021-09-01",
            end_date="2024-09-30",
        )
        self.document = Document.objects.create(
            name="Test Document",
            description="Test Document Description",
            file=generate_file(),
            version=1,
            project=self.project,
        )

    def test_document_creation(self):
        self.assertEqual(self.document.name, "Test Document")
        self.assertEqual(self.document.description, "Test Document Description")
        self.assertEqual(self.document.version, 1)
        self.assertEqual(self.document.project, self.project)

    def test_document_string_representation(self):
        self.assertEqual(str(self.document), "Document name: Test Document")

    def test_update_document(self):
        self.document.version = 2
        self.assertEqual(self.document.version, 2)

    def test_delete_document(self):
        self.document.delete()
        self.assertEqual(Document.objects.count(), 0)


class CommentTestCase(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            username="testuser",
            email="testuser@gmail.com",
            password="password123",
            password2="password123",
        )
        self.project = Project.objects.create(
            title="Test Project",
            description="Test Description",
            start_date="2021-09-01",
            end_date="2024-09-30",
        )
        self.task = Task.objects.create(
            title="Test Task",
            description="Test Task Description",
            status="open",
            project=self.project,
            assignee=self.user,
        )
        self.comment = Comment.objects.create(
            text="Test Comment", author=self.user, task=self.task, project=self.project
        )

    def test_comment_creation(self):
        self.assertEqual(self.comment.text, "Test Comment")
        self.assertEqual(self.comment.author, self.user)
        self.assertEqual(self.comment.task, self.task)
        self.assertEqual(self.comment.project, self.project)

    def test_comment_string_representation(self):
        self.assertEqual(str(self.comment), "Comment: Test Comment")

    def test_update_comment(self):
        self.comment.text = "Updated Comment"
        self.assertEqual(self.comment.text, "Updated Comment")

    def test_delete_comment(self):
        self.comment.delete()
        self.assertEqual(Comment.objects.count(), 0)


class TimelineTestCase(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            username="testuser",
            email="testuser@gmail.com",
            password="password123",
            password2="password123",
        )
        self.project = Project.objects.create(
            title="Test Project",
            description="Test Description",
            start_date="2021-09-01",
            end_date="2024-09-30",
        )
        self.timeline = Timeline.objects.create(
            project=self.project, event_type="created"
        )

    def test_timeline_creation(self):
        self.assertEqual(self.timeline.project, self.project)
        self.assertEqual(self.timeline.event_type, "created")

    def test_timeline_string_representation(self):
        self.assertEqual(
            str(self.timeline),
            f"Timeline of {self.project.title} created {self.timeline.time}",
        )

    def test_new_timeline(self):
        Task.objects.create(
            title="Test Task",
            description="Test Task Description",
            status="open",
            project=self.project,
            assignee=self.user,
        )

        self.assertEqual(Timeline.objects.count(), 3)


class NotificationTestCase(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
            password2="password123",
        )
        self.project = Project.objects.create(
            title="Test Project",
            description="Test Description",
            start_date="2021-09-01",
            end_date="2024-09-30",
        )
        self.task = Task.objects.create(
            title="Test Task",
            description="Test Task Description",
            status="open",
            project=self.project,
            assignee=self.user,
        )
        self.notification = Notification.objects.create(
            text="Test Notification", user=self.user
        )

    def test_notification_creation(self):
        self.assertEqual(self.notification.text, "Test Notification")
        self.assertEqual(self.notification.user, self.user)
        self.assertFalse(self.notification.mark_read)

    def test_notification_string_representation(self):
        self.assertEqual(
            str(self.notification),
            f"Notification: Test Notification for User: {self.user.email}",
        )

    def test_mark_notification_as_read(self):
        self.notification.mark_read = True
        self.assertTrue(self.notification.mark_read)

    def test_task_assignment_notification(self):
        user = UserModel.objects.create_user(
            username="testuser",
            email="newuser@example.com",
            password="password123",
            password2="password123",
        )
        self.task.assignee = user
        self.task.save()
        self.assertEqual(Notification.objects.count(), 2)
