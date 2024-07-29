from django.contrib import admin

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

admin.site.register(UserModel)
admin.site.register(Project)
admin.site.register(Profile)
admin.site.register(Task)
admin.site.register(Document)
admin.site.register(Comment)
admin.site.register(Timeline)
admin.site.register(Notification)
