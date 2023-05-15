from django.contrib import admin
from .models import *

admin.site.register(Course)
admin.site.register(Lession)
admin.site.register(UserCourseLink)
admin.site.register(QuizQuestion)
admin.site.register(QuizResult)