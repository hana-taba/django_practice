from django.urls import path
from.import views

urlpatterns = [
    path('create_post/',views.PostCreate.as_view()),
    path('category/<str:slug>/',views.category_page),
    path('<int:pk>/',views.PostDetail.as_view()),
    path('',views.PostList.as_view()),
]