from django import forms
from osf.models import NotificationType


class NotificationTypeForm(forms.ModelForm):
    class Meta:
        model = NotificationType
        fields = '__all__'


class SendNotificationEmailForm(forms.Form):
    username = forms.CharField(required=False)

    username__contains = forms.CharField(required=False)

    activity_status = forms.ChoiceField(
        required=False,
        choices=(
            ('', 'Any'),
            ('active', 'Active'),
            ('inactive', 'Inactive'),
        ),
    )

    context = forms.CharField(required=False,)

    approve_recipients = forms.BooleanField(
        required=False,
        label='I reviewed the recipient list and approve sending',
    )
