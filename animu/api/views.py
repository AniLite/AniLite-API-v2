import json
import random
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from datetime import datetime
from django.core.signing import Signer
from django.conf import settings
from django.http import JsonResponse
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from users.models import CustomUser
from .serializers import AnimeDetailSerializer, AnimeListSerializer, CharacterDetailSerializer, CharacterListSerializer,  GenreSerializer
from animu.models import Anime, Genre, Character
from .mixins import MultipleFieldLookupMixin
from rest_framework.views import APIView
from users.permissions import IsLoggedIn, IsAdmin
from animu.tasks import sendMailInstantly
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.core import mail

########################## USING GENERIC VIEWS ##########################


##### Mailing list & subscription related views #####


class AnimeSubscribeView(APIView):

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

    permission_classes = [IsLoggedIn]

    def post(self, request, slug):
        user_id = request.COOKIES.get('anilite_cookie')
        user = CustomUser.objects.get(id=user_id)
        anime = Anime.objects.get(slug=slug)
        user.subscriptions.remove(anime)
        return JsonResponse({"Message": f"{user.username or user.email} unsubscribed to {anime.name_en or anime.name_jp} successfully"})


class SubscribeView(APIView):

    permission_classes = [IsLoggedIn]

    def post(self, request, slug):
        user_id = request.COOKIES.get('anilite_cookie')
        user = CustomUser.objects.get(id=user_id)
        user.get_mails = True
        return JsonResponse({"Message": f"{user.username or user.email} subscribed to the mailing list!"})


class UnsubscribeView(APIView):

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


class SendMailView(APIView):

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


class ScheduleMail(APIView):

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


class CeleryMailView(APIView):

    permission_classes = [IsAdmin]

    def post(self, request, slug):
        sendMailInstantly.delay(slug)
        return JsonResponse({"Message": "Task sent to celery successfully!"})


##### Anime related views #####


class AnimeListView(ListAPIView):

    def get_queryset(self):

        queryset = Anime.objects.all()
        fields = ['startswith', 'includes', 'sort', 'genre', 'type']

        for field in fields:

            globals()[field] = self.request.query_params.get(f'{field}')

            if globals()[field]:

                if field == 'includes':
                    queryset = queryset.filter(
                        name_en__icontains=globals()[field])
                    if queryset == Anime.objects.all():
                        queryset = queryset.filter(
                            name_jp__icontains=globals()[field])

                elif field == 'genre':
                    genres = globals()[field].split(' ')
                    for count, genre in enumerate(genres, 1):
                        globals()['qs' + str(count)
                                  ] = Genre.objects.get(slug__iexact=genre).animes.all()
                        queryset = queryset.intersection(
                            globals()['qs' + str(count)])

                elif field == 'startswith':
                    queryset = queryset.filter(
                        name_en__istartswith=globals()[field])

                elif field == 'type':
                    if globals()[field] == 'movie':
                        queryset = queryset.filter(type__icontains='MOVIE')

                elif field == 'sort':
                    if globals()[field] == 'rating':
                        queryset = queryset.order_by(
                            '-' + str(globals()[field]))
                    else:
                        queryset = queryset.order_by(str(globals()[field]))

        return queryset

    serializer_class = AnimeListSerializer


class AnimeDetailView(MultipleFieldLookupMixin, RetrieveAPIView):
    queryset = Anime.objects.all()
    serializer_class = AnimeDetailSerializer
    lookup_fields = ['slug']


class AnimeCreateView(CreateAPIView):
    queryset = Anime.objects.all()
    serializer_class = AnimeListSerializer


class AnimeUpdateView(MultipleFieldLookupMixin, UpdateAPIView):
    queryset = Anime.objects.all()
    serializer_class = AnimeListSerializer
    lookup_fields = ['slug']


class AnimeDeleteView(MultipleFieldLookupMixin, DestroyAPIView):
    queryset = Anime.objects.all()
    serializer_class = AnimeListSerializer
    lookup_fields = ['slug']


##### Genre related views #####


class GenreListView(ListAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class GenreDetailView(MultipleFieldLookupMixin, RetrieveAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_fields = ['slug']


class GenreCreateView(CreateAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class GenreUpdateView(MultipleFieldLookupMixin, UpdateAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_fields = ['slug']


class GenreDeleteView(MultipleFieldLookupMixin, DestroyAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_fields = ['slug']


##### Character related views #####


class CharacterListView(ListAPIView):

    def get_queryset(self):

        queryset = Character.objects.all()
        fields = ['startswith', 'includes', 'sort']

        for field in fields:

            globals()[field] = self.request.query_params.get(f'{field}')

            if globals()[field]:

                if field == 'startswith':
                    queryset = queryset.filter(
                        name__istartswith=globals()[field])

                elif field == 'includes':
                    queryset = queryset.filter(
                        name__icontains=globals()[field])

                elif field == 'sort':
                    queryset = queryset.order_by(str(globals()[field]))

        return queryset

    serializer_class = CharacterListSerializer


class CharacterDetailView(MultipleFieldLookupMixin, RetrieveAPIView):
    queryset = Character.objects.all()
    serializer_class = CharacterDetailSerializer
    lookup_fields = ['slug']


class CharacterCreateView(CreateAPIView):
    queryset = Character.objects.all()
    serializer_class = CharacterDetailSerializer


class CharacterUpdateView(MultipleFieldLookupMixin, UpdateAPIView):
    queryset = Character.objects.all()
    serializer_class = CharacterDetailSerializer
    lookup_fields = ['slug']


class CharacterDeleteView(MultipleFieldLookupMixin, DestroyAPIView):
    queryset = Character.objects.all()
    serializer_class = CharacterDetailSerializer
    lookup_fields = ['slug']
