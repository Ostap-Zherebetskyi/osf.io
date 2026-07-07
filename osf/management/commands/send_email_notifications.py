from django.db.models import Q
from django.db.models import OuterRef, Subquery
from django.db.models.functions import Coalesce
from osf.models import OSFUser, UserActivityCounter, NotificationTypeEnum, NotificationType
from framework.celery_tasks import app as celery_app

import logging
from django.core.management.base import BaseCommand
from django.utils import timezone

logger = logging.getLogger(__name__)

counter_subquery = (
    UserActivityCounter.objects
    .filter(_id=OuterRef('guids___id'))
    .values('total')[:1]
)

FILTER_PRESETS = {
    'active': {'is_active': True},
    'internal': {'is_active': True, 'is_staff': True, 'username__endswith': '@cos.io'},
}


def get_batches(filters={}, batch_size=100):
    qs = (
        OSFUser.objects
        .filter(**filters)
        .annotate(
            activity_total=Coalesce(
                Subquery(counter_subquery),
                0
            )
        )
        .order_by('-activity_total', '-date_registered', '-id')
    )

    last_total = None
    last_date = None
    last_id = None

    while True:
        batch_qs = qs

        if last_total is not None:
            batch_qs = batch_qs.filter(
                Q(activity_total__lt=last_total) |
                Q(activity_total=last_total, date_registered__lt=last_date) |
                Q(activity_total=last_total, date_registered=last_date, id__lt=last_id)
            )

        batch = batch_qs[:batch_size]

        if not batch:
            break

        batch_ids = list(batch.values_list('id', flat=True))

        yield batch_ids

        last_total = list(batch.values_list('activity_total', flat=True))[-1]
        last_date = list(batch.values_list('date_registered', flat=True))[-1]
        last_id = batch_ids[-1]


@celery_app.task(name='management.commands.send_email_notifications')
def send_email_notifications(notification_type_name='blank', filters={'is_active': True}, context={}, *args, **kwargs):
    if hasattr(NotificationTypeEnum, notification_type_name):
        del getattr(NotificationTypeEnum, notification_type_name).instance

    for batch in get_batches(filters=filters, batch_size=100):
        send_batch.delay(notification_type_name=notification_type_name, recipients_ids=batch, context=context, *args, **kwargs)

@celery_app.task(name='management.commands.send_batch')
def send_batch(notification_type_name='blank', recipients_ids=[], context={}, *args, **kwargs):
    if hasattr(NotificationTypeEnum, notification_type_name):
        notification_type = getattr(NotificationTypeEnum, notification_type_name).instance
    else:
        notification_type_qs = NotificationType.objects.filter(name=notification_type_name)  # TODO: cache
        if not notification_type_qs.exists():
            return
        notification_type = notification_type_qs.first()
    recipients_qs = OSFUser.objects.filter(id__in=recipients_ids)
    recipient_to_update = []
    for recipient in recipients_qs:
        try:
            notification_type.emit(
                user=recipient,
                event_context=context,
                save=False,  # Too many write operations
            )
            recipient.notifications_configured.update({notification_type_name: timezone.now().strftime('%d-%m-%Y %H:%M:%S')})
            recipient_to_update.append(recipient)
        except Exception as exc:
            logger.error(exc)  # TODO update error
            pass

    OSFUser.objects.bulk_update(recipient_to_update, ['notifications_configured'])
    # logger.log()  # batch done


class Command(BaseCommand):
    help = 'Send email notifications for selected users'

    def handle(self, *args, **options):
        send_email_notifications(context={'data1': 'mock_data1', 'subject': 'subject'})
