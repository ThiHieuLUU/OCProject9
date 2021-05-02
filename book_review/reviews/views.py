from django.shortcuts import render, redirect
from django.template.context_processors import csrf

from .forms import NewUserForm, MyAuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages  # import messages
from django.contrib.auth.forms import AuthenticationForm  # add this
from django.http import HttpResponseRedirect
from django.urls import reverse

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
    if request.method == "POST":
        if 'create_review' in request.POST:
            post_id = request.POST.get('create_review') # post is a ticket
            request.session["ticket_id"] = post_id
            request.session["has_already_ticket"] = True
            return redirect("reviews:review-create")
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

    if request.method == "POST":
        if request.POST.get("deletePost"):
            post_value = request.POST.get("deletePost")
            print(post_value)
            if "TICKET" in post_value:
                _id = int(post_value[len("TICKET"):])  # The rest of string
                title = request.user.tickets.get(id=_id).title
                request.user.tickets.get(id=_id).delete()
                messages.success(request, f"Vous avez supprimé la demande de critique {title}")
            # WHY DON'T WORK ?
            if "REVIEW" in post_value:
                _id = int(post_value[len("REVIEW"):])  # The rest of string
                print("id =", _id)
                # # request.user.reviews.get(id=_id).delete()
                ticket = Review.objects.get(id=_id).ticket
                # request.user.reviews.all()[_id].delete()
                Review.objects.get(id=_id).delete()
                messages.success(request, f"Vous avez supprimé la critique {ticket} ")
            return redirect("reviews:own-posts")

    return render(request, "reviews/own_posts.html", context={'posts': posts})


def user_follows_view(request):
    # A regarder comment récupérer données
    if request.method == "POST":
        user = request.user
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
    queryset = Ticket.objects.all()

    def form_valid(self, form):
        form.instance.user = self.request.user  # To add logged user as attribute "user" of Ticket
        return super().form_valid(form)


class TicketListView(ListView):
    template_name = 'tickets/ticket_list.html'
    queryset = Ticket.objects.all()


class TicketDetailView(DetailView):
    template_name = 'tickets/ticket_detail.html'
    queryset = Ticket.objects.all()


class TicketUpdateView(UpdateView):
    template_name = 'tickets/ticket_create.html'
    form_class = TicketModelForm
    queryset = Ticket.objects.all()

    def form_valid(self, form):
        return super().form_valid(form)


class TicketDeleteView(DeleteView):
    template_name = 'tickets/ticket_delete.html'
    queryset = Ticket.objects.all()

    def get_success_url(self):
        return reverse('reviews:ticket-list')


class ReviewCreateView(CreateView):
    template_name = 'reviews/review_create.html'
    form_class = ReviewModelForm
    queryset = Review.objects.all()  # <blog>/<modelname>_list.html

    # success_url = '/'

    def form_valid(self, form):
        form.instance.user = self.request.user  # To add logged user as attribute "user" of Ticket

        return super().form_valid(form)


def create_new_ticket_review_view(request):
    if request.method == "POST":
        if request.POST.get("new_ticket_review") == "new_ticket_review":
            ticket_form = TicketModelForm(request.POST)
            review_form = ReviewModelForm(request.POST)
            user = request.user
            if ticket_form.is_valid() and review_form.is_valid():
                print(ticket_form)
                ticket = ticket_form.save(False)
                ticket.user = user
                ticket.save() # Pb with image

                review = review_form.save(False)
                review.ticket = ticket
                review.user = user
                review.save()
                return redirect("reviews:own-posts")
        if "already_ticket" in request.POST:
            ticket_id = request.POST.get("already_ticket")
            ticket = Ticket.objects.get(id=ticket_id)
            review_form = ReviewModelForm(request.POST)
            user = request.user
            if review_form.is_valid():
                review = review_form.save(False)
                review.ticket = ticket
                review.user = user
                review.save()
                return redirect("reviews:own-posts")
    context = {}
    context.update(csrf(request))
    review_form = ReviewModelForm()
    context["review_form"] = review_form
    if request.session.get("has_already_ticket"):
        ticket_id = request.session.get("ticket_id")
        ticket = Ticket.objects.get(id=ticket_id)
        has_ticket = True
        context["has_ticket"] = has_ticket
        context["post"] = ticket
        del request.session["has_already_ticket"]
        del request.session["ticket_id"]
    else:
        ticket_form = TicketModelForm()
        context["ticket_form"] = ticket_form
        has_ticket = False
        context["has_ticket"] = has_ticket
    return render(request, "reviews/review_create.html", context=context)

