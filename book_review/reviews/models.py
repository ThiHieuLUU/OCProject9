from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

# django.contrib.auth.models.User

""" An user:
- creates many tickets (to request reviews on the different books)
- posts many reviews (each review is a response to a ticket or to any book that the user wants)
- has many followed-users (via followed_by)

An user:
- follows many other users (vi following)
"""


class Ticket(models.Model):
    # Ticket is created when a review request is created.
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    image = models.ImageField(null=True, blank=True, upload_to="images/")
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} (créé par {self.user})'

    def get_absolute_url(self):
        # return reverse("reviews:ticket-detail", kwargs={"id": self.id})
        return reverse("reviews:ticket-detail",  kwargs={"pk": self.id})


class Review(models.Model):
    # Many reviews for one ticket
    ticket = models.ForeignKey(to=Ticket, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(
        # validates that rating must be between 0 and 5
        validators=[MinValueValidator(0), MaxValueValidator(5)])
    headline = models.CharField(max_length=128)
    body = models.CharField(max_length=8192, blank=True)
    # Many reviews posted by one user
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    time_created = models.DateTimeField(auto_now_add=True) # Add this

    def __str__(self):
        if self.ticket:
            return f'Critique de {self.user} pour la demande de {self.ticket}'
        else:
            return f'{self.user} a créé une critique sur {self.headline}'

    def get_absolute_url(self):
        return reverse("reviews:review-detail", kwargs={"pk": self.id})


class UserFollows(models.Model):
    # Your UserFollows model definition goes here
    # An user has many UserFollows with an UserFollows containing UserFollows.user/ UserFollows.followed_user
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='following')

    followed_user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                      related_name='followed_by')

    class Meta:
        # ensures we don't get multiple UserFollows instances
        # for unique user-user_followed pairs
        unique_together = ('user', 'followed_user', )

    def __str__(self):
        return f'{self.user} follows {self.followed_user}'

    @classmethod
    def add_user_follows(cls, user, will_follow_user_name):
        followed_user = User.objects.get(username=will_follow_user_name)
        new_user_follows = cls(user=user, followed_user=followed_user)
        new_user_follows.save()

    @staticmethod
    def delete_user_follows(user, followed_user_name):
        all_user_follows = user.following.all()
        followed_user_names = [obj.followed_user.username for obj in all_user_follows]
        index = followed_user_names.index(followed_user_name)
        all_user_follows[index].delete()


def get_tickets_created_by_user(user):
    return user.tickets.all()


def get_reviews_posted_by_user(user):
    return user.reviews.all()


def get_reviews_related_to_a_ticket(ticket):
    return ticket.reviews.all()


def get_reviews_related_to_all_tickets_of_user(user):
    list_of_reviews = User.objects.none()
    for ticket in user.tickets.all():
        list_of_reviews |= ticket.reviews.all()
    return list_of_reviews


def get_reviews_posted_by_following_user(user):
    list_of_reviews = User.objects.none()
    userfollows_followings = user.following.all() # list of UserFollows objects
    for userfollow in userfollows_followings:
        following_user = userfollow.followed_user # the person who the "user" follows
        reviews = get_reviews_posted_by_user(following_user)
        list_of_reviews |= reviews
    return list_of_reviews


def get_tickets_created_by_following_user(user):
    list_of_tickets = User.objects.none()
    userfollows_followings = user.following.all() # list of UserFollows objects
    for userfollow in userfollows_followings:
        following_user = userfollow.followed_user # the person who the "user" follows
        tickets = get_tickets_created_by_user(following_user)
        list_of_tickets |= tickets
    return list_of_tickets


def get_users_viewable_reviews(user):
    return get_reviews_posted_by_user(user) | get_reviews_posted_by_following_user(user) | get_reviews_related_to_all_tickets_of_user(user)


def get_users_viewable_tickets(user):
    return get_tickets_created_by_user(user) | get_tickets_created_by_following_user(user)


def get_following_users(user):
    following_users = [user_follow.followed_user for user_follow in user.following.all()]
    return following_users


def get_followed_users(user):
    followed_users = [user_follow.user for user_follow in user.followed_by.all()]
    return followed_users









