#! /usr/bin/venv python3
# coding: utf-8
"""Models for book_review project.

Models contain:
- Ticket model is used when a user demands a review for a book or an article.
- Review model is used when a user posts a review.
- UserFollows model is used to handle the following relationship between users.

- A user can:
- create many tickets
- post many reviews (each review is a response to a ticket or to any book that the user wants)
- have many followed-users (via followed_by)
- follow many other users (via following)
"""

from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Ticket(models.Model):
    """Ticket model is created when a user request a review for a book or an article."""

    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    # A user can create many tickets.
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    image = models.ImageField(null=True, blank=True, upload_to="images/")
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """To display a Ticket object in a readable format."""

        return f'{self.title} (créé par {self.user})'

    def get_absolute_url(self):
        """To redirect toward the detail view for a ticket object."""

        return reverse("reviews:ticket-detail", kwargs={"pk": self.id})

    @staticmethod
    def get_tickets_created_by_user(user):
        """Get all tickets of a user."""

        return user.tickets.all()

    @classmethod
    def get_tickets_created_by_following_user(cls, user):
        """Get tickets from other users who the user follows."""

        tickets = User.objects.none()
        userfollows_followings = user.following.all()  # Queryset of UserFollows objects
        for userfollow in userfollows_followings:
            following_user = userfollow.followed_user  # The person who the "user" follows
            tickets_from_following_users = cls.get_tickets_created_by_user(following_user)
            tickets |= tickets_from_following_users  # Union of queryset
        return tickets

    @classmethod
    def get_users_viewable_tickets(cls, user):
        """Get all tickets that a user can see (his own tickets and which of his following users)."""

        return cls.get_tickets_created_by_user(user) | cls.get_tickets_created_by_following_user(user)


class Review(models.Model):
    """Review is created when a user replies to a ticket or creates an own review."""

    # A ticket can have many reviews.
    ticket = models.ForeignKey(to=Ticket, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(
        # validates that rating must be between 0 and 5
        validators=[MinValueValidator(0), MaxValueValidator(5)])
    headline = models.CharField(max_length=128)
    body = models.CharField(max_length=8192, blank=True)
    # A user can post many reviews.
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    time_created = models.DateTimeField(auto_now_add=True)  # Add this

    def __str__(self):
        """To display a Review object in a readable format."""

        if self.ticket:
            return f'Critique de {self.user} pour la demande de {self.ticket}'
        else:
            return f'{self.user} a créé une critique sur {self.headline}'

    def get_absolute_url(self):
        """To redirect toward the detail view for a review object."""

        return reverse("reviews:review-detail", kwargs={"pk": self.id})

    @staticmethod
    def get_reviews_posted_by_user(user):
        """Get all reviews of a user."""

        return user.reviews.all()

    @staticmethod
    def get_reviews_related_to_a_ticket(ticket):
        """Get all reviews posted for a ticket."""

        return ticket.reviews.all()

    @staticmethod
    def get_reviews_related_to_all_tickets_of_user(user):
        """Get all reviews posted by a user."""

        reviews = User.objects.none()
        for ticket in user.tickets.all():
            reviews |= ticket.reviews.all()
        return reviews

    @classmethod
    def get_reviews_posted_by_following_user(cls, user):
        """Get all reviews posted by following users of an user."""

        reviews = User.objects.none()
        user_follows_followings = user.following.all()  # Queryset of UserFollows objects
        for user_follows in user_follows_followings:
            following_user = user_follows.followed_user  # The person who the "user" follows
            reviews_from_following_user = cls.get_reviews_posted_by_user(following_user)
            reviews |= reviews_from_following_user  # Union of queryset
        return reviews

    @classmethod
    def get_users_viewable_reviews(cls, user):
        """Get all reviews that a user can see (his own reviews and which of his following users)."""

        return cls.get_reviews_posted_by_user(user) | cls.get_reviews_posted_by_following_user(
            user) | cls.get_reviews_related_to_all_tickets_of_user(user)


class UserFollows(models.Model):
    """UserFollows is created when a user follows another user (another user is 'followed_user' attribute)"""
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='following')

    followed_user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                      related_name='followed_by')

    class Meta:
        # Ensures we don't get multiple UserFollows instances
        # for unique user-user_followed pairs
        unique_together = ('user', 'followed_user',)

    def __str__(self):
        return f'{self.user} follows {self.followed_user}'

    @classmethod
    def add_user_follows(cls, user, will_follow_user_name):
        """This method is used when an user decides to follow another user."""

        followed_user = User.objects.get(username=will_follow_user_name)
        cls.objects.create(user=user, followed_user=followed_user)


    @classmethod
    def get_following_user_follows_from_user(cls, user):
        """Get all users who the user follows."""

        user_follows_following = cls.objects.filter(user__username=user.username)
        return user_follows_following

    @classmethod
    def get_followed_user_follows_from_user(cls, user):
        """Get all users they follow the user."""

        user_follows_followed_by = cls.objects.filter(followed_user__username=user.username)
        return user_follows_followed_by
