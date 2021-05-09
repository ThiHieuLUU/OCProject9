#! /usr/bin/venv python3
# coding: utf-8
"""Views for book_review project.

Main views:
- Connection page (for authentication)
- Registration page (to register the site)
- Home page (Flux view in the project: all posts of an authenticated user and which of his following users)
- Posts page (All posts (tickets and reviews) of an authenticated user)
- Abonnements page (to follow other users and to see who the user follows and who follows the user)
"""

from itertools import chain

from django.shortcuts import redirect
from django.template.context_processors import csrf
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages  # import messages
from django.shortcuts import render
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import CharField, Value
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView
)

from .forms import (
    NewUserForm,
    MyAuthenticationForm,
    TicketModelForm,
    ReviewModelForm,
    UserFollowsModelForm
)

from .models import (
    Ticket,
    Review,
    UserFollows
)


def connection_view(request):
    """This view is used to login for a user."""

    if request.method == "POST":
        form = MyAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("reviews:home")
        else:
            messages.error(
                request, "Nom d'utilisateur ou mot de passe invalide.")
    else:
        form = MyAuthenticationForm()
    context = {"login_form": form}
    return render(
        request=request,
        template_name='reviews/users/connection.html',
        context=context)


def register_view(request):
    """This view is used to register the site for a new user."""

    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Inscription effectuée avec succès")
            return redirect("reviews:connection")
        messages.error(
            request,
            "Le nom d'utilisateur ou le mot de passe est incorrect.")
    form = NewUserForm()
    return render(
        request=request,
        template_name="reviews/users/register.html",
        context={
            "register_form": form})


def logout_view(request):
    """This view is used to logout of the site."""

    logout(request)
    return redirect("reviews:connection")


def home_view(request):
    """The Home view used after a user is authenticated.

    This view displays all posts (tickets and reviews) related to the user and to his following users.
    """

    reviews = Review.get_users_viewable_reviews(request.user)
    # returns queryset of reviews
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    tickets = Ticket.get_users_viewable_tickets(request.user)
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
            post_id = request.POST.get('create_review')  # post is a ticket
            request.session["ticket_id"] = post_id
            request.session["has_already_ticket"] = True
            return redirect("reviews:review-create")
    return render(request, "reviews/users/home.html", context={'posts': posts})


def own_posts_view(request):
    """The Posts view used to display all posts (tickets and reviews) of the authenticated user."""

    reviews = Review.get_reviews_posted_by_user(request.user)
    # returns queryset of reviews
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    tickets = Ticket.get_tickets_created_by_user(request.user)
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
            if "TICKET" in post_value:
                # The rest of string
                ticket_id = int(post_value[len("TICKET"):])
                ticket = request.user.tickets.get(id=ticket_id)
                title = ticket.title
                ticket.delete()
                messages.success(
                    request, f"Vous avez supprimé le ticket {title}")
            if "REVIEW" in post_value:
                # The rest of string
                review_id = int(post_value[len("REVIEW"):])
                review = Review.objects.get(id=review_id)
                ticket = review.ticket
                review.delete()
                messages.success(
                    request, f"Vous avez supprimé la critique {ticket} ")
            return redirect("reviews:own-posts")

    return render(
        request,
        "reviews/users/own_posts.html",
        context={
            'posts': posts})


def user_follows_view(request):
    """This view corresponds to Abonnement page.

     The user can select an user name of other users to follow him.

     The user can see all users who follows him and all users he follows.
     """

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

    form = UserFollowsModelForm()
    user = request.user
    following_users = UserFollows.get_following_user_follows_from_user(user)
    followed_users = UserFollows.get_followed_user_follows_from_user(user)
    context = {
        "following_users": following_users,
        "followed_users": followed_users,
        "form": form}
    return render(request, "reviews/users/user_follows.html", context=context)


class TicketCreateView(CreateView):
    """This view is used when the authenticated user wants to create a ticket."""

    template_name = 'tickets/ticket_create.html'
    form_class = TicketModelForm
    queryset = Ticket.objects.all()

    def form_valid(self, form):
        """Validate the input for creating a Ticket model."""

        form.instance.user = self.request.user  # To add logged user as the attribute "user" of Ticket
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the Home page when the ticket is created with success."""

        return reverse('reviews:home')


class TicketListView(ListView):
    """This view is used when the authenticated user wants to see his all tickets."""

    template_name = 'tickets/ticket_list.html'
    queryset = Ticket.objects.all()


class TicketDetailView(DetailView):
    """This view is used when the authenticated user wants to see the detail of one of his tickets."""

    template_name = 'tickets/ticket_detail.html'
    queryset = Ticket.objects.all()


class TicketUpdateView(UpdateView):
    """This view is used when the authenticated user wants to update/modify one of his tickets."""

    template_name = 'tickets/ticket_update.html'
    form_class = TicketModelForm
    queryset = Ticket.objects.all()

    def form_valid(self, form):
        """Validate the updated information for a ticket."""

        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the Posts page when the ticket is updated with success."""

        return reverse('reviews:own-posts')


class TicketDeleteView(DeleteView):
    """This view is used when the authenticated user wants to delete one of his tickets."""

    template_name = 'tickets/ticket_delete.html'
    queryset = Ticket.objects.all()

    def get_success_url(self):
        """Redirect to the Posts page when the ticket is deleted."""

        return reverse('reviews:own-posts')


def create_new_ticket_review_view(request):
    """This view is used when the authenticated user wants to create his own review or reply to a ticket."""

    if request.method == "POST":
        if request.POST.get("new_ticket_review") == "new_ticket_review":
            ticket_form = TicketModelForm(request.POST, request.FILES)
            review_form = ReviewModelForm(request.POST)
            user = request.user
            if ticket_form.is_valid() and review_form.is_valid():
                print(ticket_form)
                ticket = ticket_form.save(False)
                ticket.user = user
                ticket.save()

                review = review_form.save(False)
                review.ticket = ticket
                review.user = user
                review.save()
                return redirect("reviews:home")
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
                return redirect("reviews:home")
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


class ReviewListView(ListView):
    """This view is used when the authenticated user wants to see his all reviews."""

    template_name = 'reviews/review_list.html'
    queryset = Review.objects.all()


class ReviewDetailView(DetailView):
    """This view is used when the authenticated user wants to see the detail of one of his reviews."""

    template_name = 'reviews/review_detail.html'
    queryset = Review.objects.all()


class ReviewDeleteView(DeleteView):
    """This view is used when the authenticated user wants to delete one of his reviews."""

    template_name = 'reviews/review_delete.html'
    queryset = Review.objects.all()

    def get_success_url(self):
        """Redirect to the Posts page when the review is deleted."""

        return reverse('reviews:own-posts')


class ReviewUpdateView(UpdateView):
    """This view is used when the authenticated user wants to update/modify one of his reviews."""

    template_name = 'reviews/review_update.html'
    form_class = ReviewModelForm
    queryset = Review.objects.all()

    def form_valid(self, form):
        """Validate the update information for a review."""

        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the Posts page when the review is updated with success."""

        return reverse('reviews:own-posts')


class UserFollowsDeleteView(DeleteView):
    """This view is used when the authenticated user wants to delete one of his following users."""

    template_name = 'reviews/users/user_follows_delete.html'
    queryset = UserFollows.objects.all()

    def get_success_url(self):
        """Redirect to the Abonnements page when the following user is removed."""

        return reverse('reviews:user-follows')
