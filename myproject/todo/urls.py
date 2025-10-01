from django.urls import path
from . import views
urlpatterns=[
    path("register/",views.registerPage,name="register"),
    path("login/",views.loginPage,name="login"),
    path("logout/",views.logoutUser,name="logout"),
    path("tasks/new/",views.create_task,name="task_create"),
    path("task/<int:pk>/done/",views.task_mark_done,name="task_mark_done"),
    path("tasks/<int:pk>/edit/",views.update_task,name="task_update"),
    path("tasks/<int:pk>/delete/",views.delete_task,name="task_delete"),
    path("tasks/<int:pk>/change_status/",views.change_status,name="task_change_status"),
    path("",views.home,name="home")
]