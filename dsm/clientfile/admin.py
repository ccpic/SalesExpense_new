from django.contrib import admin
from .models import Client, Group, Hp_IQVIA, Staff
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User


class ClientAdmin(admin.ModelAdmin):
    search_fields = ["bu", "rd", "rm", "dsm", "rsp", "hospital", "dept", "name"]


class StaffInline(admin.StackedInline):
    model = Staff
    can_delete = False
    verbose_name_plural = "员工"


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (StaffInline,)


admin.site.register(Client, ClientAdmin)
admin.site.register([Group, Hp_IQVIA])
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
