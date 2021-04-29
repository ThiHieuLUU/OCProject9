from django.shortcuts import render, redirect
from .forms import NewUserForm, MyAuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages  # import messages
from django.contrib.auth.forms import AuthenticationForm  # add this

from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView
)
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from django.contrib.auth.models import User
from itertools import chain
from django.db.models import CharField, Value

from .forms import *
from .models import *


def home_view(request):
    if request.method == "POST":
        form = MyAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("reviews:flux")
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe invalide.")
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe invalide.")
    form = MyAuthenticationForm()
    context = {"login_form": form}

    return render(request=request, template_name='reviews/home.html', context=context)


def flux_view(request):
    user = request.user
    ls = user.tickets.all()

    return render(request, "reviews/flux.html", {"ls": ls})


def register_view(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            # login(request, user)
            messages.success(request, "Inscription effectuée avec succès")
            return redirect("reviews:home")
        messages.error(request, "Le nom d'utilisateur ou le mot de passe est incorrect.")
    form = NewUserForm
    return render(request=request, template_name="reviews/register.html", context={"register_form": form})


def logout_view(request):
    logout(request)
    return redirect("reviews:home")


def feed_view(request):
    reviews = get_users_viewable_reviews(request.user)
    # returns queryset of reviews
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    tickets = get_users_viewable_tickets(request.user)
    # returns queryset of tickets
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))

    # combine and sort the two types of posts
    posts = sorted(
        chain(reviews, tickets),
        key=lambda post: post.time_created,
        reverse=True
    )
    return render(request, "reviews/flux.html", context={'posts': posts})


def own_posts_view(request):
    reviews = get_reviews_posted_by_user(request.user)
    # returns queryset of reviews
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    tickets = get_tickets_created_by_user(request.user)
    # returns queryset of tickets
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))

    # combine and sort the two types of posts
    posts = sorted(
        chain(reviews, tickets),
        key=lambda post: post.time_created,
        reverse=True
    )
    return render(request, "reviews/own_posts.html", context={'posts': posts})


def user_follows_view(request):
    # A regarder comment récupérer données
    if request.method == "POST":
        user = request.user
        # followed_user_name = request.POST.get("followed_user")
        # followed_user_name = request.POST.get("followed_user")
        print(request.POST)
        try:
            if request.POST.get("will_follow_user") != "Nom d'utilisateur":
                will_follow_user_name = request.POST.get("will_follow_user")
                UserFollows.add_user_follows(user, will_follow_user_name)
                messages.success(request, "Le suivi est effectué.")
                return redirect("reviews:user-follows")
        except ObjectDoesNotExist:
            messages.error(request, "Le nom d'utilisateur n'existe pas")
        except IntegrityError:
            messages.error(request, "Vous avez déjà suivi cet utilisateur")
        else:
            messages.error(request, "Erreur de demande de suivi")

        if request.POST.get("unfollow"):
            print("In Here")
            followed_user_name = request.POST.get("unfollow")
            UserFollows.delete_user_follows(user, followed_user_name)
            messages.success(request, f"Vous avez désabonné le {followed_user_name}")
            return redirect("reviews:user-follows")

    form = UserFollowsModelForm()
    user = request.user
    following_users = get_following_users(user)
    followed_users = get_followed_users(user)
    context = {"following_users": following_users, "followed_users": followed_users, "form": form}
    return render(request, "reviews/user_follows.html", context=context)


class TicketCreateView(CreateView):
    template_name = 'tickets/ticket_create.html'
    form_class = TicketModelForm
    queryset = Ticket.objects.all()  # <blog>/<modelname>_list.html

    # success_url = '/'

    def form_valid(self, form):
        form.instance.user = self.request.user  # To add logged user as attribute "user" of Ticket
        return super().form_valid(form)


class TicketDetailView(DetailView):
    template_name = 'tickets/ticket_detail.html'

    # queryset = Article.objects.all()

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Ticket, id=id_)


class TicketUpdateView(UpdateView):
    template_name = 'tickets/ticket_create.html'
    form_class = TicketModelForm

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Ticket, id=id_)

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)


class TicketDeleteView(DeleteView):
    template_name = 'tickets/ticket_delete.html'

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Ticket, id=id_)

    def get_success_url(self):
        return reverse('tickets:ticket-list')


class ReviewCreateView(CreateView):
    template_name = 'reviews/review_create.html'
    form_class = ReviewModelForm
    queryset = Review.objects.all()  # <blog>/<modelname>_list.html

    # success_url = '/'

    def form_valid(self, form):
        form.instance.user = self.request.user  # To add logged user as attribute "user" of Ticket

        return super().form_valid(form)
