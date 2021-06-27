from django.db import models
from django.contrib.auth.models import User

from company.models import Company


class Question(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    question_slug = models.CharField(max_length=100, unique=True, db_index=True)
    body = models.CharField(max_length=1000)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    vote = models.ManyToManyField(User, related_name='question_votes')
    down_vote = models.ManyToManyField(User, related_name='question_down_votes')
    view = models.ManyToManyField(User, related_name='question_views')
    total_view = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    body = models.CharField(max_length=5000)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    vote = models.ManyToManyField(User, related_name='answer_votes')
    down_vote = models.ManyToManyField(User, related_name='answer_down_votes')

    def __str__(self):
        return self.body[:100]
