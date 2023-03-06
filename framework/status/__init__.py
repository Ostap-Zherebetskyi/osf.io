# -*- coding: utf-8 -*-

from collections import namedtuple

from framework.sessions import session

Status = namedtuple('Status', ['message', 'jumbotron', 'css_class', 'dismissible', 'trust', 'id', 'extra'])  # trust=True displays msg as raw HTML

#: Status_type => bootstrap css class
TYPE_MAP = {
    'warning': 'warning',
    'warn': 'warning',
    'success': 'success',
    'info': 'info',
    'error': 'danger',
    'danger': 'danger',
    'default': 'default',
}


def push_status_message(message, kind='warning', dismissible=True, trust=True, jumbotron=False, id=None, extra=None):
    """
    Push a status message that will be displayed as a banner on the next page loaded by the user.

    :param message: Text of the message to display
    :param kind: The type of alert message to use; translates into a bootstrap CSS class of `alert-<kind>`
    :param dismissible: Whether the status message can be dismissed by the user
    :param trust: Whether the text is safe to insert directly into HTML as given. (useful if the message includes
        custom code, eg links) If false, the message will be automatically escaped as an HTML-safe string.
    :param jumbotron: Should this be in a jumbotron element rather than an alert
    """
    # TODO: Change the default to trust=False once conversion to markupsafe rendering is complete
    try:
        statuses = session.get('status', None)
    except RuntimeError as e:
        exception_message = str(e)
        if 'Working outside of request context.' in exception_message:
            # Working outside of request context, so should be a DRF issue. Status messages are not appropriate there.
            # If it's any kind of notification, then it doesn't make sense to send back to the API routes.
            if kind == 'error':
                #  If it's an error, then the call should fail with the error message. I do not know of any cases where
                # this branch will be hit, but I'd like to avoid a silent failure.
                from rest_framework.exceptions import ValidationError
                raise ValidationError(message)
            return
        else:
            raise
    if not statuses:
        statuses = []
    if not extra:
        extra = {}
    css_class = TYPE_MAP.get(kind, 'warning')
    statuses.append(Status(message=message,
                           jumbotron=jumbotron,
                           css_class=css_class,
                           dismissible=dismissible,
                           id=id,
                           extra=extra,
                           trust=trust))
    session['status'] = statuses
    session.save()


def pop_status_messages(level=0):
    messages = session.get('status', None)
    for message in messages or []:
        if len(message) == 5:
            message += [None, None]  # Make sure all status's have enough arguments
    session['status_prev'] = messages
    if 'status' in session:
        session.pop('status', None)
        session.save()
    return messages


def pop_previous_status_messages(level=0):
    messages = session.get('status_prev', None)
    if 'status_prev' in session:
        session.pop('status_prev', None)
        session.save()
    return messages
