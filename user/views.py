from django.shortcuts import redirect, HttpResponseRedirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.views.generic import TemplateView, View, CreateView, DetailView
from .forms import *
from .models import *
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
import json

class Home(TemplateView):
    template_name = 'user/home.html'
    extra_context = {}

    def get(self, request, *args, **kwargs):
        course_obj = Course.objects.all()
        self.extra_context["course_obj"] = course_obj
        if request.user.is_authenticated:
            user_enrolled_course_list = UserCourseLink.objects.values_list("course__id",flat=True).filter(user=request.user)
            self.extra_context["user_enrolled_course_list"] = user_enrolled_course_list
        return super().get(request, *args, **kwargs)

class UserLogin(LoginView):
    template_name = 'user/login.html'
    form_class = LoginForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        return super().get(request, *args, **kwargs)

class UserSignUp(CreateView):
    template_name = 'user/sign_up.html'
    model = User
    form_class = SignUpForm
    success_url = reverse_lazy('login')

class UserLogout(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("login")

class EnrollCourse(LoginRequiredMixin, DetailView):
    template_name = 'user/enroll_course.html'
    model = Course
    context_object_name = "course_obj"
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = {}
        lesson_obj = Lession.objects.filter(course=self.object)
        quiz_obj = QuizQuestion.objects.filter(course=self.object)
        user_enrolled_course_obj = UserCourseLink.objects.filter(user=self.request.user, course=self.object)
        if user_enrolled_course_obj:
            context['enrolled'] = True
        else:
            context['enrolled'] = False
        if quiz_obj:
            context['quiz_obj'] = quiz_obj
        context['lesson_obj'] = lesson_obj
        return super().get_context_data(**context)

    def post(self, request, *args, **kwargs):
        course_id = request.POST.get('course_id')
        course_obj = Course.objects.filter(id=course_id)
        if course_obj:
            course_obj = course_obj.first()
            course_obj.enrolled_count += 1
            course_obj.save()

            user_course_obj = UserCourseLink()
            user_course_obj.user = request.user
            user_course_obj.course = course_obj
            user_course_obj.save()
        return redirect("my_course")


class DetailedCourseView(LoginRequiredMixin, DetailView):
    template_name = 'user/course.html'
    model = Course
    context_object_name = "course_obj"
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = {}
        lesson_obj = Lession.objects.filter(course=self.object)
        quiz_obj = QuizQuestion.objects.filter(course=self.object).order_by("?")
        result_obj = QuizResult.objects.filter(course=self.object,user=self.request.user)
        if quiz_obj:
            context['quiz_obj'] = quiz_obj
        if result_obj:
            result_obj = result_obj.first()
            context['result'] = result_obj.result
            context['selected_options'] = result_obj.selected_options
        context['lesson_obj'] = lesson_obj
        return super().get_context_data(**context)

    def post(self, request, *args, **kwargs):
        course_id = int(request.POST['course_id'])
        course_obj = Course.objects.get(id=course_id)
        question_keys = [k for k in request.POST.keys() if "q" in k]
        selected_options = ""
        result_obj = QuizResult()
        result_obj.course = course_obj
        result_obj.user = request.user
        correct_ans = 0
        for k in question_keys:
            selected_op = request.POST.get(k,"null")
            quiz_obj = QuizQuestion.objects.get(id=int(k.replace("q","")))
            if quiz_obj.answer.strip() == selected_op.strip():
                correct_ans += 1
            selected_options += selected_op + ","
        result_obj.selected_options = selected_options
        result_obj.result = f"{correct_ans}/{len(question_keys)}"
        result_obj.save()
        return HttpResponseRedirect(self.request.path_info)

class MyCourse(LoginRequiredMixin, TemplateView):
    template_name = 'user/my_course.html'
    extra_context = {}
    login_url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        user_course_link_obj = UserCourseLink.objects.filter(user=request.user)
        if user_course_link_obj:
            self.extra_context["course_obj"] = [data.course for data in user_course_link_obj]
        else:
            self.extra_context["course_obj"] = None
        return super().get(request, *args, **kwargs)