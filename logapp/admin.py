from django.contrib import admin
from .models import User
import csv
from django.http import HttpResponse
from django.contrib.auth.models import Group
# Register your models here.
# admin.site.register(User)

admin.site.unregister(Group)
def export_log(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="user_details.csv"'
    writer = csv.writer(response)
    writer.writerow(['Usename', 'Phonenumber','Email'])
    user_details = queryset.values_list('first_name', 'phonenumber','email')
    for i in user_details:
        writer.writerow(i)
    return response
export_log.short_description = 'Export to csv'
class UserAdmin(admin.ModelAdmin):
    list_display=['first_name','email','phonenumber']
    actions = [export_log]
    search_fields = ['first_name']

    # def has_delete_permission(self, request, obj=None):
    #     return request.user.is_superuser
    #
    # def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
    #     context.update({
    #         'show_save': False,
    #         'show_save_and_continue': False,
    #         'show_save_and_add_another': False,
    #         'show_delete': False
    #     })
    #     return super().render_change_form(request, context, add, change, form_url, obj)

admin.site.register(User, UserAdmin)

