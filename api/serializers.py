from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .models import (
    Comment,
    Document,
    Notification,
    Profile,
    Project,
    Task,
    Timeline,
    UserModel,
)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "profile_picture", "roles", "contact_number"]


class UserSerializer(serializers.ModelSerializer):
    user_profile = ProfileSerializer(required=False)

    class Meta:
        model = UserModel
        fields = [
            "id",
            "username",
            "email",
            "created_at",
            "password",
            "password2",
            "user_profile",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "password2": {"write_only": True},
        }

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        profile_data = validated_data.pop("user_profile", None)
        password = validated_data.pop("password")
        validated_data.pop("password2")
        user = UserModel.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        if profile_data:
            p = Profile.objects.create(user=user, **profile_data)
            p.save()
        return user


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        "bad_token": ("Token is not blacklisted"),
    }

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        try:
            refresh = RefreshToken(self.token)
            refresh.blacklist()
        except TokenError:
            self.fail("bad_token")


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "start_date",
            "end_date",
            "team_members",
        ]

    def create(self, validated_data):
        team_members = validated_data.pop("team_members")
        project = Project.objects.create(
            title=validated_data["title"],
            description=validated_data["description"],
            start_date=validated_data["start_date"],
            end_date=validated_data["end_date"],
        )
        project.team_members.set(team_members)
        project.save()
        return project


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "title", "description", "status", "project", "assignee"]

    def create(self, validated_data):
        task = Task.objects.create(**validated_data)
        task.save()
        return task


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "name", "description", "file", "version", "project"]

    def create(self, validated_data):
        document = Document.objects.create(**validated_data)
        document.save()
        return document


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "text", "author", "created_at", "task", "project"]

    def create(self, validated_data):
        comment = Comment.objects.create(**validated_data)
        comment.save()
        return comment


class TimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timeline
        fields = ["id", "project", "event_type", "time"]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "text", "user", "created_at", "mark_read"]
