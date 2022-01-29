import json
import random
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from datetime import datetime
from django.core.signing import Signer
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from users.models import CustomUser
from animu.models import Anime
from users.permissions import IsLoggedIn, IsAdmin
from animu.tasks import sendMailInstantly
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.core import mail


class SubscribeView(APIView):

    '''
    For subscribing to the mailing list
    '''

    permission_classes = [IsLoggedIn]

    def post(self, request):
        user_id = request.COOKIES.get('anilite_cookie')
        user = CustomUser.objects.get(id=user_id)
        user.get_mails = True
        user.save()
        return JsonResponse({"Message": f"{user.username or user.email} subscribed to the mailing list!"})


class UnsubscribeView(APIView):

    '''
    For unsubscribing to the mailing list
    '''

    def get(self, request):
        signer = Signer(salt=str(settings.SECRET_KEY))
        signed = request.GET.get('id', None)
        unsigned = signer.unsign_object(signed)
        email = unsigned['email']
        if signed is not None:
            user = CustomUser.objects.get(email=email)
            user.get_mails = False
            user.save()
            return JsonResponse({"Message": f"{user.username or user.email} unsubscribed to all mails successfully!"})
        return JsonResponse({"Message": "Something went wrong"})


class AnimeSubscribeView(APIView):

    '''
    For subscribing to a certain anime
    '''

    permission_classes = [IsLoggedIn]

    def post(self, request, slug):
        user_id = request.COOKIES.get('anilite_cookie')
        user = CustomUser.objects.get(id=user_id)
        anime = Anime.objects.get(slug=slug)
        if anime.is_completed == True:
            return JsonResponse({"Message": "This anime is already complete, don't expect any more episodes to air"})
        user.subscriptions.add(anime)
        return JsonResponse({"Message": f"{user.username or user.email} subscribed to {anime.name_en}!"})


class AnimeUnsubscribeView(APIView):

    '''
    For unsubscribing to a certain anime
    '''

    permission_classes = [IsLoggedIn]

    def post(self, request, slug):
        user_id = request.COOKIES.get('anilite_cookie')
        user = CustomUser.objects.get(id=user_id)
        anime = Anime.objects.get(slug=slug)
        user.subscriptions.remove(anime)
        return JsonResponse({"Message": f"{user.username or user.email} unsubscribed to {anime.name_en or anime.name_jp} successfully"})


class SendMailView(APIView):

    '''
    For sending mails instantly without celery
    '''

    permission_classes = [IsAdmin]

    def post(self, request, slug):

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
            return JsonResponse({"Message": f"{num_mails} mail(s) sent successfully!"})

        return JsonResponse({"Message": "Looks like nobody was subscribed to this anime :/"})


class CeleryMailView(APIView):

    '''
    For sending mails instantly with celery
    '''

    permission_classes = [IsAdmin]

    def post(self, request, slug):
        res = sendMailInstantly.delay(slug)
        print(res)
        return JsonResponse({"Message": "Task sent to celery successfully!"})


class ScheduleMail(APIView):

    '''
    For scheduling mails with celery
    '''

    permission_classes = [IsAdmin]

    def post(self, request, slug):

        try:
            param = str(request.GET.get('datetime', None))
            dt = datetime.strptime(param, "%d/%m/%Y-%H:%M")
        except Exception as e:
            return JsonResponse({"Error details": f'{e}'})

        schedule, created = CrontabSchedule.objects.get_or_create(
            hour=dt.hour, minute=dt.minute, day_of_month=dt.day, month_of_year=dt.month)
        task = PeriodicTask.objects.create(crontab=schedule, name="schedule-email-"+str(
            param) + str(random.randint(1, 1000)), one_off=True, task='animu.tasks.sendMailInstantly', args=json.dumps([slug]))
        return JsonResponse({"Message": "Mail scheduled successfully"})
