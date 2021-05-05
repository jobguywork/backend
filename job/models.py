from django.db import models


class Job(models.Model):
    name = models.CharField(max_length=50)
    job_slug = models.CharField(max_length=50, unique=True, db_index=True)
    cover = models.CharField(max_length=200, null=True)
    icon = models.CharField(max_length=50, null=True)
    description = models.CharField(max_length=10000, null=True)
    is_deleted = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)

    @property
    def company_count(self):
        return self.companyreview_set.aggregate(models.Count('company', distinct=True))['company__count']

    def __str__(self):
        return self.name
