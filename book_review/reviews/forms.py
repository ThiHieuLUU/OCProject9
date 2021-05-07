#! /usr/bin/venv python3
# coding: utf-8
"""Forms for book_review project.

Forms contain:
- NewUserForm which is used to register the site.
- MyAuthenticationForm which is used to login the site.
- TicketModelForm which is used to display some fields of Ticket model.
- ReviewModelForm which is used to display some fields of Review model.
- UserFollowsModelForm which is used to display some fields of UserFollows model.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

from .models import Ticket, Review, UserFollows


class NewUserForm(UserCreationForm):
    """Form used to allow a new user registers the site."""

    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        """Establish the elements to display the form in template."""

        super(NewUserForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].help_text = None
            self.fields[field_name].label = ""
        self.fields['username'].widget.attrs['placeholder'] = 'Nom d\'utilisateur'
        self.fields['password1'].widget.attrs['placeholder'] = 'Mot de pass'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirmer mot de passe'

    def save(self, commit=True):
        """Save new user in the database when the form is valid."""

        user = super(NewUserForm, self).save(commit=False)
        if commit:
            user.save()
        return user


class MyAuthenticationForm(AuthenticationForm):
    """Form used to allow the authentication of a user."""

    class Meta:
        model = User
        fields = ("username", "password")

    def __init__(self, *args, **kwargs):
        """Establish the elements to display the form in template."""

        super(MyAuthenticationForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].help_text = None
            self.fields[field_name].label = ""

        self.base_fields['username'].widget.attrs['placeholder'] = 'Nom d\'utilisateur'
        self.base_fields['password'].widget.attrs['placeholder'] = 'Mot de pass'


class TicketModelForm(forms.ModelForm):
    """Form to display Ticket's attributes."""

    title = forms.CharField(
        label='Titre',
        required=False,
    )

    description = forms.CharField(
        label="Description",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "new-class-name two",
                "id": "my-id-for-textarea",
                "rows": 5,
                'cols': 50
            }
        )
    )

    class Meta:
        model = Ticket
        fields = ["title", "description", "image"]


class ReviewModelForm(forms.ModelForm):
    """Form to display Review's attributes."""

    RATING_RANGE = (
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5')
    )

    rating = forms.ChoiceField(
        label='Note',
        required=False,
        choices=RATING_RANGE,
        widget=forms.RadioSelect
    )

    headline = forms.CharField(
        label='Titre',
        required=False,
    )

    body = forms.CharField(
        label="Commentaire",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "new-class-name two",
                "id": "my-id-for-textarea",
                "rows": 5,
                'cols': 50,
            }
        )
    )

    class Meta():
        model = Review
        fields = ["headline", "rating", "body"]


class UserFollowsModelForm(forms.ModelForm):
    """Form to display UserFollows' attributes."""

    class Meta:
        model = UserFollows
        fields = ["followed_user"]

    def __init__(self, *args, **kwargs):
        super(UserFollowsModelForm, self).__init__(*args, **kwargs)
        self.base_fields["followed_user"].widget.attrs['placeholder'] = 'Nom d\'utilisateur'
