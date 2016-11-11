from django.contrib import admin
from web import models

# Register your models here.
admin.site.register(models.Tasks)
admin.site.register(models.TasksHandle)
admin.site.register(models.Projects)
admin.site.register(models.TaskTalk)
admin.site.register(models.UserInfo)
