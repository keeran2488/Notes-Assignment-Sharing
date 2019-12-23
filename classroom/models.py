from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist



class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    email = models.EmailField(max_length=100)


class Subject(models.Model):
    name = models.CharField(max_length=30)
    semester = models.IntegerField(null=True)

    def __str__(self):
        return self.name
    

class Assignment(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments')
    name = models.CharField(max_length=225)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    submission_date = models.DateField('Submission Date')
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField('Question', max_length=255)
    question_image = models.ImageField(upload_to='media/', verbose_name='Image', blank=True)

    def __str__(self):
        return self.text

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key = True)
    roll_no = models.PositiveIntegerField(unique=True, null=True)
    semester = models.PositiveIntegerField(null=True)

    def __str__(self):
        return self.user.username


# @receiver(post_save, sender=User)
# def update_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Student.objects.create(user=instance)
#     instance.student.save()


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    try:
        instance.student.save()
    except ObjectDoesNotExist:
        Student.objects.create(user=instance)
    

class StudentAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='assignment_answers')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    text = models.CharField(max_length=255, null=True)


class AnswerRemark(models.Model):
    Remarks = models.TextField('Remarks', default="No remarks added!", null=True)
    studentanswer = models.ForeignKey(StudentAnswer, on_delete=models.CASCADE)

    def __str__(self):
        return self.Remarks
    
    

class StudentAnswerImage(models.Model):
    studentanswer = models.ForeignKey(StudentAnswer, on_delete=models.CASCADE)
    answer_image = models.ImageField(upload_to='media/', verbose_name='Answer Image', blank=True)
