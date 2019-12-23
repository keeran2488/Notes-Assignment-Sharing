from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import IntegerField
from django.db.models.functions import Cast
from django.contrib import messages
from datetime import date
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.views.generic import CreateView
from django.views.generic.edit import FormView
from django.contrib.auth.decorators import user_passes_test
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
from django.core.mail import send_mail
from django.forms import modelformset_factory

from .decorators import *
from .models import User, Assignment, Question, Subject, Student, StudentAnswer, StudentAnswerImage, AnswerRemark
from .forms import StudentSignUpForm, TeacherSignUpForm, QuestionForm, StudentAnswerForm, StudentAnswerImageForm, AnswerRemarkForm

def home(request):
    if request.user.is_authenticated:
        if request.user.is_teacher:
            return redirect('teachers:assignment_change_list')
        else:
            return redirect('students:assignment_list')
    return redirect('login')

def admin_check(user):
    return user.is_superuser

# class StudentSignUpView(CreateView):
#     model = User
#     form_class = StudentSignUpForm
#     template_name = 'signup_form.html'

#     def get_context_data(self, **kwargs):
#         kwargs['user_type'] = 'student'
#         return super().get_context_data(**kwargs)

#     def form_valid(self, form):
#         user = form.save()
#         login(self.request, user)
#         return redirect('home')




@user_passes_test(admin_check, login_url='admin:login')
def teachersignup(request):
    user_t = "Teacher"
    if request.method == 'POST':
        form = TeacherSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.is_teacher = True
            user.email = form.cleaned_data.get('email')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            return redirect('admin:index')
    else:
        form = TeacherSignUpForm()
    return render(request, 'registration/signup_form.html', {'form': form,'user_type':user_t})


@method_decorator([login_required, teacher_required], name='dispatch')
class AssignmentListView(ListView):
    model = Assignment
    ordering = ('name',)
    context_object_name = 'assignments'
    template_name = 'teachers/assignment_change_list.html'

    def get_queryset(self):
        queryset = self.request.user.assignments.all()
        return queryset


@method_decorator([login_required, teacher_required], name='dispatch')
class AssignmentCreateView(CreateView):
    model = Assignment
    fields = ('name', 'subject','submission_date',)
    template_name = 'teachers/assignment_add_form.html'

    def form_valid(self, form):
        assignment = form.save(commit=False)
        assignment.owner = self.request.user
        assignment.save()
        # custom_subject = 'New Assignment: ' + form.cleaned_data.get('name')
        # custom_message = 'This assignment must be submitted before ' + form.cleaned_data.get('submission_date').strftime("%Y/%m/%d")
        # a_semester = Subject.objects.filter(name = form.cleaned_data.get('subject')).annotate(as_int=Cast('semester', IntegerField())).get()
        # receiver = []
        # for studentemail in Student.objects.filter(semester=a_semester.as_int).values_list('user__email', flat=True):
        #     receiver.append(studentemail)
        # send_mail(
        #     custom_subject,
        #     custom_message,
        #     'chaudharyk456@gmail.com',
        #     receiver
        # )
        messages.success(self.request, 'The assignment was created! Add some questions to it.')
        return redirect('teachers:assignment_change', assignment.pk)


@method_decorator([login_required, teacher_required], name='dispatch')        
class AssignmentUpdateView(UpdateView):
    model = Assignment
    fields = ('name', 'subject','submission_date',)
    context_object_name = 'assignments'
    template_name = 'teachers/assignment_change_form.html'

    def get_context_data(self, **kwargs):
        kwargs['questions'] = self.get_object().questions.all()
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.assignments.all()

    def get_success_url(self):
        return reverse('teachers:assignment_change', kwargs={'pk': self.object.pk})
    

@method_decorator([login_required, teacher_required], name='dispatch')
class AssignmentDeleteView(DeleteView):
    model = Assignment
    context_object_name = 'assignments'
    template_name = 'teachers/assignment_delete_confirm.html'
    success_url = reverse_lazy('teachers:assignment_change_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'The assignment was deleted with success!')
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.assignments.all()
    

@login_required
@teacher_required
def question_add(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save(commit=False)
            question.assignment = assignment
            question.save()
            messages.success(request, 'Question added successfully!')
            return redirect('teachers:question_change', assignment.pk, question.pk)
    else:
        form = QuestionForm()

    return render(request, 'teachers/question_add_form.html', {'assignments': assignment, 'form': form})


@login_required
@teacher_required
def question_change(request, assignment_pk, question_pk):
    assignment = get_object_or_404(Assignment, pk=assignment_pk, owner=request.user)
    question = get_object_or_404(Question, pk=question_pk, assignment=assignment)

    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES, instance=question)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            messages.success(request, 'Question saved with success!')
            return redirect('teachers:assignment_change', assignment.pk)
    else:
        form = QuestionForm(instance=question)

    return render(request, 'teachers/question_change_form.html', {
        'assignments': assignment,
        'question': question,
        'form': form,
    })


@method_decorator([login_required, teacher_required], name='dispatch')
class QuestionDeleteView(DeleteView):
    model = Question
    context_object_name = 'question'
    template_name = 'teachers/question_delete_confirm.html'
    pk_url_kwarg = 'question_pk'

    def get_context_data(self, **kwargs):
        question = self.get_object()
        kwargs['assignments'] = question.assignment
        return super().get_context_data(**kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'The question was deleted with success!')
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return Question.objects.filter(assignment__owner=self.request.user)

    def get_success_url(self):
        question = self.get_object()
        return reverse('teachers:assignment_change', kwargs={'pk': question.assignment_id})


@login_required
@teacher_required
def view_result(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    answered_student = StudentAnswer.objects.filter(assignment_id = pk)

    return render(request, 'teachers/view_result.html', {
        'assignments': assignment,
        'answered_student': answered_student,
    })


@login_required
@teacher_required
def view_answer(request, assignments_pk, asn_pk):
    assignment = get_object_or_404(Assignment, pk=assignments_pk)
    answered_image = StudentAnswerImage.objects.filter(studentanswer_id = asn_pk)
    studentanswer = get_object_or_404(StudentAnswer, pk=asn_pk)
    if request.method == 'POST':
        form = AnswerRemarkForm(request.POST)
        if form.is_valid():
            remark = form.save(commit=False)
            remark.studentanswer = studentanswer 
            remark.save()
            messages.success(request, 'Remarks added successfully!')
            return redirect('teachers:view_result_student', assignments_pk, asn_pk)
    else:
        form = AnswerRemarkForm()

    return render(request, 'teachers/view_answers.html', {
        'answered_image': answered_image,
        'assignments': assignment,
        'form':form,
    })





#-------------Views for students-------------------------#


@user_passes_test(admin_check, login_url='admin:login')
def studentsignup(request):
    user_t = "Student"
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        # context={
        #     'form':form,
        #     'user_type':user_t,
        # }
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.student.roll_no = form.cleaned_data.get('roll_no')
            user.student.semester = form.cleaned_data.get('semester')
            user.email = form.cleaned_data.get('email')
            user.is_student = True
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            return redirect('admin:index')
    else:
        form = StudentSignUpForm()
    # return render(request, 'signup_form.html', context)
    return render(request, 'registration/signup_form.html', {'form': form,'user_type':user_t})


@method_decorator([login_required, student_required], name='dispatch')
class StudentAssignmentListView(ListView):
    model = Assignment
    ordering = ('name',)
    context_object_name = 'assignments'
    template_name = 'students/assignment_list.html'

    def get_context_data(self, **kwargs):
        kwargs['timen'] = date.today()
        # kwargs['remarks'] = AnswerRemark.objects.filter(studentanswer__assignment_id__in = [1,2], studentanswer__student_id = self.request.user.id)
        return super().get_context_data(**kwargs)

    # def remark_answer(self):
    #     return AnswerRemark.objects.filter(studentanswer__assignment_id = 1, studentanswer__student_id = 3)

    def get_queryset(self):
        student = self.request.user.student
        student_semester = Student.objects.filter(pk = self.request.user.student.pk).values_list('semester', flat=True)
        student_subs = Subject.objects.filter(semester__in = student_semester).values_list('pk', flat=True)
        assign = Assignment.objects.filter(subject__in = student_subs).order_by('-submission_date')
        remarks = AnswerRemark.objects.filter(studentanswer__assignment_id__in = [1,2], studentanswer__student_id = self.request.user.id)
        queryset = zip(assign, remarks)
        return queryset


@login_required
@student_required
def take_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    question = Question.objects.filter(assignment_id = pk)
    question_i = Question.objects.filter(assignment_id = pk).values("question_image")
    return render(request, 'students/take_assignment.html', {
        'assignments': assignment,
        'question': question,
        'questionimages' : question_i,
    })


@login_required
@student_required
def submit_answer(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    user = request.user.student
    if request.method == "POST":
        form = StudentAnswerForm(request.POST)
        file_form = StudentAnswerImageForm(request.POST, request.FILES)
        files = request.FILES.getlist('answer_image')
        if form.is_valid() and file_form.is_valid():
            student_answer = form.save(commit=False)
            student_answer.student = user
            student_answer.assignment = assignment
            student_answer.save()
            for f in files:
                file_instance = StudentAnswerImage(answer_image = f, studentanswer = student_answer)
                file_instance.save()
            messages.success(request,"Answers have been submitted!")
            return redirect("students:assignment_list")
    else:
        form = StudentAnswerForm
        file_form = StudentAnswerImageForm
    return render(request, 'students/submit_answer.html', {
        'form':form,
        'file_form':file_form,
        'assignments': assignment,
    })