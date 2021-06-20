from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from company.models import City, Company, Industry, Province
from job.models import Job
from review.models import CompanyReview


class JobTests(APITestCase):
    def setUp(self):
        # User
        user = User.objects.create(
            username="testuser",
        )
        user.set_password("testpassword")
        user.save()

        # Job
        job = Job.objects.create(
            name="برنامه نویس پایتون",
            cover="/default/system/cover.jpg",
            icon="fas fa-home",
            description="برنامه نویس پایتون",
        )
        # Industry
        industry = Industry.objects.create(
            name="کامپیوتر، فناوری اطلاعات و اینترنت",
            industry_slug="کامپیوتر-فناوری-اطلاعات-و-اینترنت",
            logo="/default/system/cover.jpg",
            icon="fas fa-graduation-cap",
            description="good industry",
        )
        # Province
        province = Province.objects.create(name="تهران")

        # City
        city = City.objects.create(
            name="تهران",
            province=province,
        )

        # Company
        company = Company.objects.create(
            user=user,
            name="فرازپردازان",
            name_en="Faraz Pardazan",
            description="ما در فرازپردازان، با هم کار را شروع می کنیم. با هم یاد می گیریم و با هم رشد می کنیم و با هم فعالیت حرفه ای و اقتصادی خود را به جلو می بریم.  مهم‌ترین مزیت کاری فرازپردازان کار در یک محیط کاملا دوستانه است",
            logo="/company/faraz-pardazan/4aa04840-4030-11e9-8ad3-7bb6142308a0.png",
            industry=industry,
            founded="2010-02-10",
            company_slug="faraz-pardazan",
            size="S",
            city=city,
            tell="0213456789",
            site="http://farazpardazan.com",
        )
        company2 = Company.objects.create(
            user=user,
            name="ابرآروان",
            name_en="Arvan Cloud",
            description=" شروع کار ابر آروان تولید فناوری شبکه توزیع محتوا یا CDN بود. محصولی که وظیفه اصلی اش شتابدهی وب و محافظت از وب سایت ها در برابر حملات سایبری بوده و هست. محتوای یک وبسایت یا در واقع هرنوع محتوای آنلاین به کمک این سرویس با سرعت بالاتر و از نزدیکترین نقطه جغرافیایی به دست کاربر نهایی وبسایت میرسد و در نتیجه تجربه کاربری به شکل چشم گیری افزایش پیدا می کند و از طرف دیگر وب سایت هم در برابر حملات مختلف محافظت میشود. در شرایط فعلی ابر آروان تنها راه‌کار مقابله با حملات DDoS در ایران است.",
            logo="/company/arvan-cloud/536b8ec0-40de-11e9-82ca-553f80196c54.jpg",
            industry=industry,
            founded="2015-02-10",
            company_slug="arvan-cloud",
            size="VS",
            city=city,
            tell="0213456789",
            site="http://arvancloud.com",
        )
        # Company Review
        CompanyReview.objects.create(
            company=company,
            job=job,
            recommend_to_friend=False,
            state="FULL TIME",
            work_life_balance=1,
            salary_benefit=1,
            security=1,
            management=1,
            culture=1,
            over_all_rate=1,
            anonymous_job=True,
            title="بهترین تجربه عمرم",
            salary=5000000,
            salary_type="PER MOUNTH",
            creator=user,
        )
        CompanyReview.objects.create(
            company=company2,
            job=job,
            recommend_to_friend=False,
            state="PART TIME",
            work_life_balance=2,
            salary_benefit=2,
            security=2,
            management=2,
            culture=2,
            over_all_rate=2,
            anonymous_job=True,
            title="بدترین تجربه عمرم",
            salary=6000000,
            salary_type="PER MOUNTH",
            creator=user,
        )

    def test_company_count(self):
        job = Job.objects.get(name="برنامه نویس پایتون")
        self.assertEqual(job.company_count, 2)

    def test_model_representation(self):
        job = Job.objects.get(name="برنامه نویس پایتون")
        self.assertEqual(str(job), "برنامه نویس پایتون")
