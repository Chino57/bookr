from django.contrib import admin
from django.contrib.admin import AdminSite

from reviews.models import Publisher, Contributor,Book, BookContributor, Review


class BookAdmin(admin.ModelAdmin):
    model = Book
    date_hierarchy = 'publication_date'
    list_display = ('title', 'isbn', 'get_publisher', 'publication_date')
    list_filter = ('publisher','publication_date')
    search_fields = ('title', 'publisher__name')

    def get_publisher(self, obj):
        return obj.publisher.name


class ReviewAdmin(admin.ModelAdmin):
    exclude = ('date_edited',)
    fieldsets = (('Linkage', {'fields': ('creator', 'book')}),
                 ('Review content', {'fields':('content', 'rating')}))


class ContributorAdmin(admin.ModelAdmin):
    list_display = ('last_names', 'first_names')
    search_fields = ('last_names__startswith', 'first_names')
    list_filter = ('last_names',)


# Register your models here.
admin.site.register(Publisher)
admin.site.register(Contributor, ContributorAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(BookContributor)
admin.site.register(Review, ReviewAdmin)

