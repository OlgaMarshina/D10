from turtle import title

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.template.loader import render_to_string

from news.models import PostCategory


def send_notificatins(preview, pk, subscribers):
    html_contect = render_to_string(
        'post_created_email.html',
    {
        'text': preview,
        'link': f'{settings.SITE_URL}/news/{pk}'

    }

    )
    msg = EmailMultiAlternatives(
        subject= title,
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to = subscribers,
    )

    msg.attach_alternative(html_contect, 'text/html')
    msg.send()


@receiver(m2m_changed, sender=PostCategory)
def notify_about_new_post(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add':
        categories = instance.category.all()
        subscribers_emails =[]

        for cat in categories:
            subscribers = cat.subscribers.all()
            subscribers_emails += [s.email for s in subscribers]

        send_notificatins(instance.preview(), instance.pk, subscribers_emails)