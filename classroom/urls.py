from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    home,
    StudentAssignmentListView,
    take_assignment,
    submit_answer,
    AssignmentListView,
    AssignmentCreateView,
    AssignmentDeleteView,
    AssignmentUpdateView,
    view_result,
    view_answer,
    question_add,
    question_change,
    QuestionDeleteView,
)

urlpatterns = [
    path("", home, name="home"),
    path(
        "students/",
        include(
            (
                [
                    path(
                        "", StudentAssignmentListView.as_view(), name="assignment_list"
                    ),
                    path(
                        "assignment/<int:pk>/", take_assignment, name="take_assignment"
                    ),
                    path(
                        "assignment/<int:pk>/submit",
                        submit_answer,
                        name="submit_answer",
                    ),
                ],
                "classroom",
            ),
            namespace="students",
        ),
    ),
    path(
        "teacher/",
        include(
            (
                [
                    path(
                        "", AssignmentListView.as_view(), name="assignment_change_list"
                    ),
                    path(
                        "assignment/add/",
                        AssignmentCreateView.as_view(),
                        name="assignment_add",
                    ),
                    path(
                        "assignment/<int:pk>/",
                        AssignmentUpdateView.as_view(),
                        name="assignment_change",
                    ),
                    path(
                        "assignment/<int:pk>/delete/",
                        AssignmentDeleteView.as_view(),
                        name="assignment_delete",
                    ),
                    # path('quiz/<int:pk>/results/', teachers.QuizResultsView.as_view(), name='quiz_results'),
                    path(
                        "assignment/<int:pk>/result/", view_result, name="view_result"
                    ),
                    path(
                        "assignment/<int:assignments_pk>/result/<int:asn_pk>/",
                        view_answer,
                        name="view_result_student",
                    ),
                    path(
                        "assignment/<int:pk>/question/add/",
                        question_add,
                        name="question_add",
                    ),
                    path(
                        "assignment/<int:assignment_pk>/question/<int:question_pk>/",
                        question_change,
                        name="question_change",
                    ),
                    path(
                        "assignment/<int:assignment_pk>/question/<int:question_pk>/delete/",
                        QuestionDeleteView.as_view(),
                        name="question_delete",
                    ),
                ],
                "classroom",
            ),
            namespace="teachers",
        ),
    ),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_header = "Notes Assignment Sharing Administration"
admin.site.site_title = "NAS Admin Login"
admin.site.index_title = "Welcome to Notes Assignment Sharing Portal"
