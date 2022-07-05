from django.contrib import admin, messages
from .models import Movie, Director, Actor, DressingRoom
from django.db.models import QuerySet

admin.site.register(Director)
admin.site.register(Actor)


@admin.register(DressingRoom)
class DressingRoomAdmin(admin.ModelAdmin):
    list_display = ['floor', 'number', 'actor']


class RatingFilter(admin.SimpleListFilter):  # create own filter
    title = 'Filter by rating'  # filter name
    parameter_name = 'rating'  # word, that puts in a link, when filter used

    def lookups(self, request, model_admin):  # categories you can choose
        return [
            ('<40', 'Low'),
            ('from 40 to 59', 'Middle'),
            ('from 60 to 79', 'High'),
            ('>=80', 'Magnificent!'),
        ]

    def queryset(self, request, queryset: QuerySet):  # processing a filter-request with a result
        if self.value() == '<40':
            return queryset.filter(rating__lt=40)
        if self.value() == 'from 40 to 59':
            return queryset.filter(rating__gte=40).filter(rating__lt=60)
        if self.value() == 'from 60 to 79':
            return queryset.filter(rating__gte=60).filter(rating__lt=80)
        if self.value() == '>=80':
            return queryset.filter(rating__gte=80)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    # fields = ['name', 'rating']  # only these fields will be included in element form
    # exclude = ['slug']  # element form will contain all fields except specified
    # readonly_fields = ['year']  # specified fields changing forbidden
    prepopulated_fields = {'slug': ('name',)}  # autocomplete 'slug' field on 'name' field base
    list_display = ['name', 'rating', 'director', 'budget',
                    'rating_status']  # first field (here 'name') must be link to element form, therefore it can't be 'editable' (see below)
    list_editable = ['rating', 'director', 'budget']  # fields, you can change on the main panel
    filter_horizontal = ['actors']
    ordering = ['-rating', 'name']  # original sorting when you open the main panel
    list_per_page = 10  # max amount of objects, which will displayed on the main panel
    actions = ['set_dollars',
               'set_euro']  # list of possible actions, which you can use for objects (see functions below)
    search_fields = ['name', 'rating']  # adding search field, indication where we can search
    list_filter = ['name', 'currency', RatingFilter]  # available filters

    @admin.display(ordering='rating',
                   description='Status')  # decorator for additional field 'Status', based on 'rating'
    def rating_status(self, mov: Movie):
        if mov.rating < 50:
            return 'Did u really wanna watch it?'
        if mov.rating < 70:
            return 'One time u can watch it'
        if mov.rating <= 85:
            return 'Nice'
        return 'The best!'

    @admin.action(description='Set currency in USD')
    def set_dollars(self, request, qs: QuerySet):
        qs.update(currency=Movie.USD)

    @admin.action(description='Set currency in EUR')
    def set_euro(self, request, qs: QuerySet):
        count_update = qs.update(currency=Movie.EUR)
        self.message_user(  # add the pop-up message, after method was execute
            request,
            f'{count_update} notes was updated',  # content of pop-up message
            messages.ERROR  # set red color of pop-up
        )

# admin.site.register(Movie, MovieAdmin) == decorator  '@admin.register(Movie)'
