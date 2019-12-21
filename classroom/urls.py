from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# from .views import home, AssignmentListView, AssignmentCreateView, AssignmentUpdateView, AssignmentDeleteView, question_add, question_change
from .views import *

urlpatterns = [
    path('', home, name='home'),

    path('students/', include(([
        path('', StudentAssignmentListView.as_view(), name='assignment_list'),
        # path('interests/', students.StudentInterestsView.as_view(), name='student_interests'),
        # path('taken/', students.TakenQuizListView.as_view(), name='taken_quiz_list'),
        path('assignment/<int:pk>/', take_assignment, name='take_assignment'),
    ], 'classroom'), namespace='students')),

    path('teacher/', include(([
        path('', AssignmentListView.as_view(), name='assignment_change_list'),
        path('assignment/add/', AssignmentCreateView.as_view(), name='assignment_add'),
        path('assignment/<int:pk>/', AssignmentUpdateView.as_view(), name='assignment_change'),
        path('assignment/<int:pk>/delete/', AssignmentDeleteView.as_view(), name='assignment_delete'),
        # path('quiz/<int:pk>/results/', teachers.QuizResultsView.as_view(), name='quiz_results'),
        path('assignment/<int:pk>/question/add/', question_add, name='question_add'),
        path('assignment/<int:assignment_pk>/question/<int:question_pk>/', question_change, name='question_change'),
        path('assignment/<int:assignment_pk>/question/<int:question_pk>/delete/', QuestionDeleteView.as_view(), name='question_delete'),
    ], 'classroom'), namespace='teachers')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
