from .models import Anime
from django.core import mail
from django.core.signing import Signer
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.conf import settings
from celery import shared_task


@shared_task(bind=True)
def sendMailInstantly(self, slug):
    anime = Anime.objects.get(slug=slug)
    subscribers = [user for user in anime.subscribers.all()]
    signer = Signer(salt=str(settings.SECRET_KEY))
    if subscribers:
        messages = []
        for subscriber in subscribers:
            if subscriber.get_mails == True:
                signed = signer.sign_object({"email": subscriber.email})
                html_body = get_template('episode_drop.html')
                unsub_link = f"http://127.0.0.1:8000/api/unsubscribe?id={signed}"
                image_link = anime.poster_image or anime.cover_image
                context = {
                    "user": subscriber,
                    "unsub_link": str(unsub_link),
                    "anime": anime,
                    "image_link": image_link
                }
                body = html_body.render(context)
                message = EmailMultiAlternatives(
                    subject=f'New episode alert for {anime.name_en or anime.name_jp}',
                    body=f'Hey {subscriber.username or subscriber.email}, a new episode has just dropped for {anime.name_en or anime.name_jp}, go check it out!\n\nTo unsubscribe, click on this link: http://127.0.0.1:8000/api/unsubscribe?id={signed}',
                    to=[subscriber.email],
                    from_email=f"AniLite<{settings.EMAIL_HOST_USER}>"
                )
                message.attach_alternative(body, "text/html")
                messages.append(message)
        connection = mail.get_connection()
        num_mails = connection.send_messages(messages)
        return f"Celery sent {num_mails} mail(s) successfully"
    return "Celery could not send mails"
