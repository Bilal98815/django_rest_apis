import datetime
from typing import Any

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from .managers import UserManager


def name_matching(val):
    if val == "bilal":
        raise ValidationError("Enter a different name")


def phone_number_validation(val):
    if val[0] != "0":
        raise ValidationError("Invalid phone number")
    if len(val) != 11:
        raise ValidationError("Enter 11 digits!")


def validate_image_size(image):
    try:
        file_size = image.size  # Get file size directly
    except AttributeError:
        file_size = (
            image.file.size
        )  # Fallback to accessing file size through .file if needed

    limit_mb = 4  # Limit in MB
    if file_size > limit_mb * 1024 * 1024:
        raise ValidationError(f"Max size of the file is {limit_mb} MB")


def start_date_validation(val):
    if val > datetime.date.today():
        raise ValidationError("Enter lesser date!")


def end_date_validation(val):
    if val < datetime.date.today():
        raise ValidationError("Enter future date!")


class PhoneNumberField(models.CharField):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["max_length"] = 11
        super().__init__(*args, **kwargs)
        self.validators.append(phone_number_validation)


class UserModel(AbstractUser):
    username = models.CharField(
        verbose_name="Name",
        max_length=255,
        null=True,
        validators=[name_matching],
        unique=False,
    )
    email = models.EmailField(verbose_name="Email", null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    password = models.CharField(verbose_name="Password", max_length=128)
    password2 = models.CharField(verbose_name="Confirm Password", max_length=128)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self) -> str:
        return self.email


class Profile(models.Model):
    ROLES = [("manager", "Manager"), ("qa", "QA"), ("developer", "Developer")]

    profile_picture = models.ImageField(
        verbose_name="Profile Picture",
        upload_to="profile_pics/",
        validators=[validate_image_size],
    )
    roles = models.CharField(verbose_name="Role", max_length=10, choices=ROLES)
    contact_number = PhoneNumberField(verbose_name="Contact number", null=True)
    user = models.OneToOneField(
        UserModel, on_delete=models.CASCADE, related_name="user_profile"
    )

    def __str__(self) -> str:
        return "Profile of " + self.user.username


class Project(models.Model):
    title = models.CharField(verbose_name="Title", max_length=150)
    description = models.TextField(verbose_name="Description")
    start_date = models.DateField(
        verbose_name="Start Date", validators=[start_date_validation]
    )
    end_date = models.DateField(
        verbose_name="End Date", validators=[end_date_validation]
    )
    team_members = models.ManyToManyField(UserModel, related_name="project_members")

    def __str__(self) -> str:
        return "Project: " + self.title


class Task(models.Model):

    STATUS = [
        ("open", "Open"),
        ("review", "Review"),
        ("working", "Working"),
        ("awaiting release", "Awaiting Release"),
        ("waiting qa", "Waiting QA"),
    ]

    title = models.CharField(verbose_name="Title", max_length=100)
    description = models.TextField(verbose_name="Description")
    status = models.CharField(verbose_name="Status", max_length=30, choices=STATUS)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="task_project"
    )
    assignee = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name="task_assignee",
        unique=False,
        null=True,
    )

    def __str__(self) -> str:
        return "Task title: " + self.title


class Document(models.Model):
    name = models.CharField(verbose_name="Name", max_length=100)
    description = models.TextField(verbose_name="Description")
    file = models.FileField(verbose_name="File", upload_to="document_files/")
    version = models.IntegerField(verbose_name="Version", unique=True)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="project_document"
    )

    def __str__(self) -> str:
        return "Document name: " + self.name


class Comment(models.Model):
    text = models.TextField(verbose_name="Text")
    author = models.ForeignKey(
        UserModel, related_name="comment_author", on_delete=models.CASCADE
    )
    created_at = models.DateField(verbose_name="Created at", auto_now_add=True)
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="task_comment"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="project_comment"
    )

    def __str__(self) -> str:
        return "Comment: " + self.text


class Timeline(models.Model):
    EVENT_TYPES = [
        ("created", "Created"),
        ("updated", "Updated"),
        ("deleted", "Deleted"),
    ]

    time = models.DateTimeField(auto_now_add=True, verbose_name="Time")
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="project_timeline"
    )
    event_type = models.CharField(
        max_length=10, choices=EVENT_TYPES, default="created", verbose_name="Event Type"
    )

    def __str__(self) -> str:
        return (
            "Timeline of "
            + self.project.title
            + " "
            + self.event_type
            + " "
            + str(self.time)
        )


class Notification(models.Model):
    text = models.TextField(verbose_name="Text")
    user = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="notification_user"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    mark_read = models.BooleanField(default=False, verbose_name="Mark Read")

    def __str__(self) -> str:
        return "Notification: " + self.text + " for User: " + self.user.email
