from django.apps import apps

import logging
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


def send_email_notifications(context, recipients, notification_type='blank', *args, **kwargs):
    NotificationType = apps.get_model('osf.NotificationType')

    notification_type_qs = NotificationType.objects.filter(name=notification_type)
    if not notification_type_qs.exists():
        return
    notification_type = notification_type_qs.first()
    for recipient in recipients:
        notification_type.emit(
            user=recipient,
            event_context=context
        )


class Command(BaseCommand):
    help = 'Send email notifications for selected users'

    def handle(self, *args, **options):
        send_email_notifications()
