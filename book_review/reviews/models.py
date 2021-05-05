from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


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
        return reverse("reviews:ticket-detail",  kwargs={"pk": self.id})

    @staticmethod
    def get_tickets_created_by_user(user):
        return user.tickets.all()

    @classmethod
    def get_users_viewable_tickets(cls, user):
        return cls.get_tickets_created_by_user(user) | cls.get_tickets_created_by_following_user(user)

    @classmethod
    def get_tickets_created_by_following_user(cls, user):
        list_of_tickets = User.objects.none()
        userfollows_followings = user.following.all()  # list of UserFollows objects
        for userfollow in userfollows_followings:
            following_user = userfollow.followed_user  # the person who the "user" follows
            tickets = cls.get_tickets_created_by_user(following_user)
            list_of_tickets |= tickets
        return list_of_tickets


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

    @staticmethod
    def get_reviews_posted_by_user(user):
        return user.reviews.all()

    @staticmethod
    def get_reviews_related_to_a_ticket(ticket):
        return ticket.reviews.all()

    @staticmethod
    def get_reviews_related_to_all_tickets_of_user(user):
        list_of_reviews = User.objects.none()
        for ticket in user.tickets.all():
            list_of_reviews |= ticket.reviews.all()
        return list_of_reviews

    @classmethod
    def get_reviews_posted_by_following_user(cls, user):
        list_of_reviews = User.objects.none()
        userfollows_followings = user.following.all()  # list of UserFollows objects
        for userfollow in userfollows_followings:
            following_user = userfollow.followed_user  # the person who the "user" follows
            reviews = cls.get_reviews_posted_by_user(following_user)
            list_of_reviews |= reviews
        return list_of_reviews

    @classmethod
    def get_users_viewable_reviews(cls, user):
        return cls.get_reviews_posted_by_user(user) | cls.get_reviews_posted_by_following_user(
            user) | cls.get_reviews_related_to_all_tickets_of_user(user)


class UserFollows(models.Model):
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
        cls.objects.create(user=user, followed_user=followed_user)
        # new_user_follows = cls(user=user, followed_user=followed_user)
        # new_user_follows.save()


    @classmethod
    def get_following_user_follows_from_user(cls, user):
        user_follows_list = cls.objects.filter(user__username=user.username)
        return user_follows_list

    @classmethod
    def get_followed_user_follows_from_user(cls, user):
        user_follows_list = cls.objects.filter(followed_user__username=user.username)
        return user_follows_list






















