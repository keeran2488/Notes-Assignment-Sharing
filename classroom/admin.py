from django.contrib import admin
from .models import User, Subject, Question, Assignment,Student

admin.site.register(User)
admin.site.register(Student)
admin.site.register(Subject)
admin.site.register(Question)
admin.site.register(Assignment)