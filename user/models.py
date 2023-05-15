from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

class Course(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(default='',editable=False,max_length=255)
    description = models.TextField()
    author = models.CharField(max_length=100)
    duration = models.CharField(max_length=50)
    enrolled_count = models.IntegerField(default=0)
    thumbnail = models.ImageField(upload_to='course_thumbnails/')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        course_name = self.name
        self.slug = slugify(course_name, allow_unicode=True)
        super().save(*args, **kwargs)


class Lession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    description = models.TextField()
    duration = models.CharField(max_length=50)
    video = models.FileField(upload_to='lession_videos/')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.course} - {self.name}"


class UserCourseLink(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.course.name}"


class QuizQuestion(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    question = models.TextField()
    option1 = models.CharField(max_length=140)
    option2 = models.CharField(max_length=140)
    option3 = models.CharField(max_length=140)
    option4 = models.CharField(max_length=140)
    answer = models.CharField(max_length=140)

    def __str__(self):
        return f"{self.course.name}"


class QuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    selected_options = models.TextField()
    result = models.CharField(max_length=25)

    def __str__(self):
        return f"{self.course.name}"