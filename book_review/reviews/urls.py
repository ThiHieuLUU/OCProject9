from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    # path("flux/", views.flux_view, name="flux"),
    path("flux/", views.feed_view, name="flux"),
    path("<int:id>", views.index, name="index"),



    path('tickets/create/', views.TicketCreateView.as_view(), name='ticket-create'),
    path('tickets/<int:id>/', views.TicketDetailView.as_view(), name='ticket-detail'),
    path('tickets/<int:id>/update/', views.TicketUpdateView.as_view(), name='ticket-update'),
    path('tickets/<int:id>/delete/', views.TicketDeleteView.as_view(), name='ticket-delete'),

    path('reviews/create/', views.ReviewCreateView.as_view(), name='review-create'),

    path("own_posts/", views.own_posts_view, name="own-posts"),

]
