from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import Comment, Document, Notification, Project, Task, Timeline


@receiver(post_save, sender=Project)
def project_created(sender, instance, created, **kwargs):
    if created:
        Timeline.objects.create(project=instance)


@receiver(post_save, sender=Task)
def create_timeline_for_task(sender, instance, created=False, **kwargs):
    if created:
        # Prevent the "updated" event from being created right after "created"
        instance._initial_creation = True
        Timeline.objects.create(project=instance.project, event_type="created")
    else:
        if getattr(instance, "_initial_creation", False):
            instance._initial_creation = False
        else:
            Timeline.objects.create(project=instance.project, event_type="updated")


@receiver(post_delete, sender=Task)
def create_timeline_for_task_delete(sender, instance, **kwargs):
    Timeline.objects.create(project=instance.project, event_type="deleted")


@receiver(post_save, sender=Document)
def create_timeline_for_document(sender, instance, created=False, **kwargs):
    if created:
        instance._initial_creation = True
        Timeline.objects.create(project=instance.project, event_type="created")
    else:
        if getattr(instance, "_initial_creation", False):
            instance._initial_creation = False
        else:
            Timeline.objects.create(project=instance.project, event_type="updated")


@receiver(post_delete, sender=Document)
def create_timeline_for_task_delete(sender, instance, **kwargs):
    Timeline.objects.create(project=instance.project, event_type="deleted")


@receiver(post_save, sender=Comment)
def create_timeline_for_comment(sender, instance, created=False, **kwargs):
    if created:
        instance._initial_creation = True
        Timeline.objects.create(project=instance.project, event_type="created")
    else:
        if getattr(instance, "_initial_creation", False):
            instance._initial_creation = False
        else:
            Timeline.objects.create(project=instance.project, event_type="updated")


@receiver(post_delete, sender=Comment)
def create_timeline_for_task_delete(sender, instance, **kwargs):
    Timeline.objects.create(project=instance.project, event_type="deleted")


@receiver(pre_save, sender=Task)
def task_assign_notification(sender, instance, **kwargs):
    try:
        old_task = Task.objects.get(id=instance.id)
        if old_task:
            if old_task.assignee != instance.assignee:
                Notification.objects.create(
                    text=f"""New task "{instance.title}" has been assigned to you""",
                    user=instance.assignee,
                )
            else:
                pass
        else:
            pass
    except:
        pass
