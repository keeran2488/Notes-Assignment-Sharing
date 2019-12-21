from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from .models import Student, Subject, User, Question, Assignment

class StudentSignUpForm(UserCreationForm):
    roll_no = forms.IntegerField(required=True, help_text='Enter your class roll number.',)
    semester = forms.IntegerField(required = True)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('username','roll_no','semester','email','password1', 'password2',)

    # @transaction.atomic
    # def save(self):
    #     user = super().save(commit=False)
    #     user.is_student = True
    #     user.save()
    #     student = Student.objects.create(user=user)
    #     student.roll_no.add(*self.cleaned_data.get('roll_no'))
    #     student.semester.add(*self.cleaned_data.get('semester'))
    #     return user


class TeacherSignUpForm(UserCreationForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ('username','email','password1', 'password2',)


class QuestionForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ('text', 'question_image', )

# class DocumentForm(forms.ModelForm):
#     class Meta:
#         model = Document
#         fields = ('description', 'document', )