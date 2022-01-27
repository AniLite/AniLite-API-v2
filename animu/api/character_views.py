from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from animu.models import Character
from .mixins import MultipleFieldLookupMixin
from .serializers import CharacterDetailSerializer, CharacterListSerializer


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
