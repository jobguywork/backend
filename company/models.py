from django.core.cache import cache
from django.contrib.gis.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from location_field.models.spatial import LocationField


class Industry(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    industry_slug = models.CharField(max_length=100, unique=True, db_index=True)
    logo = models.CharField(max_length=200, null=True)
    icon = models.CharField(max_length=50, null=True)
    description = models.CharField(max_length=2000)
    supported = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']

    @property
    def company_count(self):
        return self.company_set.filter(approved=True).count()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(settings.INDUSTRY_LIST)


class Benefit(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    logo = models.CharField(max_length=200, null=True)
    icon = models.CharField(max_length=50, null=True)
    supported = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    priority = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Province(models.Model):
    name = models.CharField(max_length=50, unique=True, db_index=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    supported = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=50, unique=True, db_index=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    supported = models.BooleanField(default=False)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    show_name = models.CharField(max_length=100)
    city_slug = models.CharField(max_length=50, unique=True, db_index=True)
    priority = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.show_name


class Company(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    description = models.CharField(max_length=3000, null=True)
    logo = models.CharField(max_length=200, null=True)
    cover = models.CharField(max_length=200, null=True)
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE)
    founded = models.DateField(null=True, blank=True)
    company_slug = models.SlugField(max_length=255, unique=True, db_index=True)
    benefit = models.ManyToManyField(Benefit, blank=True)
    size = models.CharField(choices=settings.OFFICE_SIZE_CHOICES, max_length=2)
    is_deleted = models.BooleanField(default=False)
    has_legal_issue = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=False)
    user_generated = models.BooleanField(default=False)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    tell = models.CharField(max_length=14, blank=True)
    site = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=200, blank=True)
    location_point = LocationField(based_fields=['city'], zoom=7, default=Point(0, 0), null=True, blank=True)
    working_hours_start = models.TimeField(null=True)
    working_hours_stop = models.TimeField(null=True)
    work_life_balance = models.FloatField(default=0)
    salary_benefit = models.FloatField(default=0)
    security = models.FloatField(default=0)
    management = models.IntegerField( default=0)
    culture = models.FloatField(default=0)
    over_all_rate = models.FloatField(default=0)
    salary_avg = models.FloatField(default=0)
    salary_max = models.FloatField(default=0)
    salary_min = models.FloatField(default=0)
    recommend_to_friend = models.IntegerField(default=0)
    total_review = models.IntegerField(default=0)
    total_interview = models.IntegerField(default=0)
    view = models.ManyToManyField(User, related_name='company_views')
    total_view = models.IntegerField(default=0)
    is_cheater = models.BooleanField(default=False)  # for company that try to cheat and advertise, 1 point in best company
    is_famous = models.BooleanField(default=False)  # 2 points in best company
    has_panel_moderator = models.BooleanField(default=False)  # 1 point
    is_big_company = models.BooleanField(default=False)  # 1 point
    company_score = models.FloatField(default=0)  # company rate for best company

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        cache.delete(settings.BEST_COMPANY_LIST)
        cache.delete(settings.DISCUSSED_COMPANY_LIST)
        cache.delete(settings.TOTAL_COMPANY)
        self.is_big_company = False if self.size in ['VS', 'S'] else True
        self.handle_company_score()
        for review in self.companyreview_set.all():
            review.has_legal_issue = self.has_legal_issue
            review.save()
        for interview in self.interview_set.all():
            interview.has_legal_issue = self.has_legal_issue
            interview.save()
        super().save(*args, **kwargs)

    def handle_company_score(self):
        review_count = self.companyreview_set.filter(is_deleted=False, approved=True).count()
        interview_count = self.interview_set.filter(is_deleted=False, approved=True).count()
        review_point = (review_count + interview_count)
        review_point = 20 if review_point > 20 else review_point
        review_point /= 4  # max must be 5
        bool_point = (2*self.is_famous) + self.has_panel_moderator + self.is_big_company + (not self.is_cheater)
        over_all_rate = self.companyreview_set.filter(is_deleted=False, approved=True). \
            aggregate(models.Avg('over_all_rate'))
        over_all_rate = over_all_rate['over_all_rate__avg'] if over_all_rate['over_all_rate__avg'] else 0
        self.company_score = round((bool_point + review_point + over_all_rate)/3, 1)

    @property
    def get_media(self):
        return self.logo

    def get_absolute_url(self):
        return '/company/{}'.format(self.company_slug)

    def handle_company_review_statics(self):
        result_company_review = self.companyreview_set.filter(is_deleted=False, approved=True).exclude(salary=0). \
            aggregate(models.Avg('salary'), models.Max('salary'), models.Min('salary'),
                      models.Avg('work_life_balance'), models.Avg('salary_benefit'), models.Avg('security'),
                      models.Avg('management'), models.Avg('culture'), models.Avg('over_all_rate'))
        result_list = self.companyreview_set.filter(is_deleted=False, approved=True).values_list('recommend_to_friend')
        total_result_list = len(result_list)
        total_result_list_true = len(list(filter(lambda x: x[0], result_list)))
        temp_data = {
            'total_review': total_result_list,
            'salary_avg': result_company_review['salary__avg'],
            'salary_max': result_company_review['salary__max'],
            'salary_min': result_company_review['salary__min'],
            'work_life_balance': result_company_review['work_life_balance__avg'],
            'salary_benefit': result_company_review['salary_benefit__avg'],
            'security': result_company_review['security__avg'],
            'management': result_company_review['management__avg'],
            'culture': result_company_review['culture__avg'],
            'over_all_rate': result_company_review['over_all_rate__avg'],
            'recommend_to_friend': round(total_result_list_true / total_result_list) * 100 if total_result_list else 0,
        }
        self.total_review = temp_data['total_review']
        self.salary_avg = round(temp_data['salary_avg']/1000000, 1) if temp_data['salary_avg'] else 0
        self.salary_max = round(temp_data['salary_max']/1000000, 1) if temp_data['salary_max'] else 0
        self.salary_min = round(temp_data['salary_min']/1000000, 1) if temp_data['salary_min'] else 0
        self.work_life_balance = round(temp_data['work_life_balance'], 1) if temp_data['work_life_balance'] else 0
        self.salary_benefit = round(temp_data['salary_benefit'], 1) if temp_data['salary_benefit'] else 0
        self.security = round(temp_data['security'], 1) if temp_data['security'] else 0
        self.management = round(temp_data['management'], 1) if temp_data['management'] else 0
        self.culture = round(temp_data['culture'], 1) if temp_data['culture'] else 0
        self.over_all_rate = round(temp_data['over_all_rate'], 1) if temp_data['over_all_rate'] else 0
        self.recommend_to_friend = round(temp_data['recommend_to_friend'], 2) if temp_data['recommend_to_friend'] else 0
        self.handle_company_score()
        self.save()

    def handle_company_interview_statics(self):
        self.total_interview = self.interview_set.filter(is_deleted=False, approved=True).count()
        self.handle_company_score()
        self.save()


class Gallery(models.Model):
    path = models.CharField(max_length=200)
    description = models.CharField(max_length=1000, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.company.name
