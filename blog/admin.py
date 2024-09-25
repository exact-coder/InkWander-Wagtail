from django.contrib import admin
from blog.models import Subscriber
from wagtail_modeladmin.options import ( ModelAdmin,modeladmin_register,)

# Register your models here.

class SubscriberAdmin(ModelAdmin):

    model = Subscriber
    menu_label = "Subscribers"
    menu_icon = "draft"
    menu_order = 290
    add_to_settings_menu=False
    exclude_from_explorer = False
    list_display = ("email","name",)
    search_fields = ("email","name",)

modeladmin_register(SubscriberAdmin)
