from django.db import models
from django.forms import ModelForm
from .models import Post, Group, Comment
from django import forms



class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("group", "text", "image")
        required = {
            "group": False,
        }
        labels = {
            "text": "Текст записи",
            "group": "Сообщества",
            "image": "Изображение",
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]

