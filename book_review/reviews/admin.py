#! /usr/bin/venv python3
# coding: utf-8
from django.contrib import admin
from .models import Ticket, Review, UserFollows

admin.site.register(Ticket)
admin.site.register(Review)
admin.site.register(UserFollows)
