from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache

from authnz.utilities import handle_user_total_rate
from company.models import Company
from job.models import Job


class ProsConsBase(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    logo = models.CharField(max_length=200, null=True)
    icon = models.CharField(max_length=50, null=True)
    is_deleted = models.BooleanField(default=False)
    priority = models.IntegerField(default=0)

    class Meta:
        abstract = True

    def add_cons_priority(self):
        self.priority += 1
        self.save()


class Pros(ProsConsBase):
    def __str__(self):
        return self.name


class Cons(ProsConsBase):
    def __str__(self):
        return self.name


class CompanyReview(models.Model):
    YEAR = 'YEAR'
    MONTH = 'MONTH'
    DAY = 'DAY'
    HOUR = 'HOUR'

    SALARY_CHOICES = (
        (YEAR, 'PER YEAR'),
        (MONTH, 'PER MONTH'),
        (DAY, 'PER DAY'),
        (HOUR, 'PER HOUR'),
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, null=True, on_delete=models.SET_NULL)
    recommend_to_friend = models.BooleanField()
    pros = models.ManyToManyField(Pros, blank=True)
    cons = models.ManyToManyField(Cons, blank=True)
    state = models.CharField(max_length=10, choices=settings.STATE_CHOICES)
    # ratings
    work_life_balance = models.IntegerField(choices=settings.RATE_CHOICES)
    salary_benefit = models.IntegerField(choices=settings.RATE_CHOICES)
    security = models.IntegerField(choices=settings.RATE_CHOICES)
    management = models.IntegerField(choices=settings.RATE_CHOICES)
    culture = models.IntegerField(choices=settings.RATE_CHOICES)
    over_all_rate = models.FloatField()
    anonymous_job = models.BooleanField()
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=40000, null=True)
    salary = models.IntegerField()
    salary_type = models.CharField(choices=SALARY_CHOICES, max_length=10)
    is_deleted = models.BooleanField(default=False)
    has_legal_issue = models.BooleanField(default=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    vote = models.ManyToManyField(User, related_name='company_review_votes')
    down_vote = models.ManyToManyField(User, related_name='company_review_down_votes')
    view = models.ManyToManyField(User, related_name='company_review_views')
    total_view = models.IntegerField(default=0)
    approved = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    current_work = models.BooleanField(default=False)
    ip = models.CharField(max_length=20, null=True, blank=True)
    reply = models.CharField(max_length=40000, null=True, blank=True)
    reply_created = models.DateTimeField(null=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return '/review/{}'.format(self.id)

    def save(self, force_insert=False, force_update=False):
        cache.delete(settings.BEST_COMPANY_LIST)
        cache.delete(settings.DISCUSSED_COMPANY_LIST)
        cache.delete(settings.TOTAL_REVIEW)
        super(CompanyReview, self).save(force_insert, force_update)
        self.creator.profile.total_review, self.creator.profile.rate_avg = handle_user_total_rate(self.creator)
        self.creator.save()


class Interview(models.Model):
    YEAR = 'YEAR'
    MONTH = 'MONTH'
    DAY = 'DAY'
    HOUR = 'HOUR'

    SALARY_CHOICES = (
        (YEAR, 'PER YEAR'),
        (MONTH, 'PER MONTH'),
        (DAY, 'PER DAY'),
        (HOUR, 'PER HOUR'),
    )

    RESPONSE_TIME_CHOICES = (
        ('1WEEK', '1WEEK'),
        ('2WEEK', '2WEEK'),
        ('1MONTH', '1MONTH'),
        ('MORE', 'MORE'),
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, null=True, on_delete=models.SET_NULL)
    pros = models.ManyToManyField(Pros, blank=True)
    cons = models.ManyToManyField(Cons, blank=True)
    status = models.CharField(max_length=10, choices=settings.INTERVIEW_STATUS)
    apply_method = models.CharField(max_length=10, choices=settings.APPLY_METHOD)
    # ratings
    interviewer_rate = models.IntegerField(choices=settings.RATE_CHOICES)
    total_rate = models.IntegerField(choices=settings.RATE_CHOICES)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=40000, null=True)
    asked_salary = models.IntegerField()
    offered_salary = models.IntegerField()
    is_deleted = models.BooleanField(default=False)
    has_legal_issue = models.BooleanField(default=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    vote = models.ManyToManyField(User, related_name='interview_votes')
    down_vote = models.ManyToManyField(User, related_name='interview_down_votes')
    total_view = models.IntegerField(default=0)
    view = models.ManyToManyField(User, related_name='interview_views')
    approved = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    interview_date = models.DateField(null=True)
    response_time_before_review = models.CharField(choices=RESPONSE_TIME_CHOICES, max_length=8)
    response_time_after_review = models.CharField(choices=RESPONSE_TIME_CHOICES, null=True, max_length=8)
    ip = models.CharField(max_length=20, null=True, blank=True)
    reply = models.CharField(max_length=40000, null=True, blank=True)
    reply_created = models.DateTimeField(null=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return '/interview/{}'.format(self.id)

    def save(self, force_insert=False, force_update=False):
        cache.delete(settings.BEST_COMPANY_LIST)
        cache.delete(settings.DISCUSSED_COMPANY_LIST)
        cache.delete(settings.TOTAL_INTERVIEW)
        super(Interview, self).save(force_insert, force_update)
        self.creator.profile.total_review, self.creator.profile.rate_avg = handle_user_total_rate(self.creator)
        self.creator.save()


class ReviewComment(models.Model):
    body = models.CharField(max_length=500)
    vote = models.ManyToManyField(User, related_name='review_comment_votes')
    down_vote = models.ManyToManyField(User, related_name='review_comment_down_votes')
    is_deleted = models.BooleanField(default=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    review = models.ForeignKey(CompanyReview, on_delete=models.CASCADE)
    ip = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.body


class InterviewComment(models.Model):
    body = models.CharField(max_length=500)
    vote = models.ManyToManyField(User, related_name='interview_comment_votes')
    down_vote = models.ManyToManyField(User, related_name='interview_comment_down_votes')
    is_deleted = models.BooleanField(default=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE)
    ip = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.body
