from datetime import datetime
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Post, Category
from .signals import send_notificatins
from NewsPaper import settings
import time
from celery.schedules import crontab


@shared_task
def send_post_for_subscribers_celery(post_pk):
    post = Post.objects.get(id=post_pk)
    categories = post.category.all()
    subscribers_all = []
    for category in categories:
        subscribers_all += category.subscribers.all()
    subscribers_list = {}
    for person in subscribers_all:
        subscribers_list[person.username] = person.email
    for n in subscribers_list.items():
        send_notificatins(n[0], post.title, post.text[:50], n[1], post.pk)

@shared_task
def weekly_post():
    today = datetime.datetime.now()
    day_week_ago = today - datetime.timedelta(days=7)
    posts = Post.objects.filter(date_post__gte=day_week_ago)
    categories = set(posts.values_list('category__name', flat=True))
    subscribers = set(Category.objects.filter(name__in=categories).values_list('subscribers__email', flat=True))

    html_content = render_to_string('posts/posts_created_last_week.html',{
            'link': f'http://127.0.0.1:8000',
            'posts': posts,
        }
    )
    msg = EmailMultiAlternatives(
        subject="новости недели",
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers,
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

    app.conf.beat_schedule = {
        'action_every_monday_8am': {
            'task': 'action',
            'schedule': crontab(hour=8, minute=0, day_of_week='monday'),
            'args': (agrs),
        },
    }


@shared_task
def hello():
    time.sleep(10)
    print("Hello, world!")


@shared_task
def printer(N):
    for i in range(N):
        time.sleep(1)
        print(i+1)