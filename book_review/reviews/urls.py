from django.urls import path
from . import views, view_test

app_name = "reviews"

urlpatterns = [
    path("", views.connection_view, name="home"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    # path("flux/", views.flux_view, name="flux"),
    path("flux/", views.feed_view, name="flux"),
    # path("<int:id>", views.index, name="index"),



    path('tickets/create/', views.TicketCreateView.as_view(), name='ticket-create'),
    path('tickets/list/', views.TicketListView.as_view(), name='ticket-list'),
    path('tickets/<int:pk>/', views.TicketDetailView.as_view(), name='ticket-detail'),
    path('tickets/<int:pk>/update/', views.TicketUpdateView.as_view(), name='ticket-update'),
    path('tickets/<int:pk>/delete/', views.TicketDeleteView.as_view(), name='ticket-delete'),

    # path('reviews/create/', views.ReviewCreateView.as_view(), name='review-create'),
    path('reviews/create/', views.create_new_ticket_review_view, name='review-create'),
    path('reviews/list/', views.ReviewListView.as_view(), name='review-list'),
    path('reviews/<int:pk>/', views.ReviewDetailView.as_view(), name='review-detail'),

    path("own_posts/", views.own_posts_view, name="own-posts"),
    path("user_follows/", views.user_follows_view, name="user-follows"),
    path("multiforms/", view_test.MultiformCreateView.as_view(), name="multiform"),



]
