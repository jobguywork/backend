from django.core.cache import cache
from django.core.mail import send_mail
from django.template.loader import render_to_string

from review.models import CompanyReview


def salary_handler(salary, salary_type, resp=False):
    if resp:
        if salary_type == CompanyReview.YEAR:
            return salary * 12
        elif salary_type == CompanyReview.MONTH:
            return salary
        elif salary_type == CompanyReview.DAY:
            return salary / 20
        else:  # HOUR
            return salary / (20 * 9)
    else:
        if salary_type == CompanyReview.YEAR:
            return salary / 12
        elif salary_type == CompanyReview.MONTH:
            return salary
        elif salary_type == CompanyReview.DAY:
            return salary * 20
        else:  # HOUR
            return salary * 20 * 9


def check_notify_to_telegram_channel(data):
    if not data["approved"]:
        return False
    notified = cache.get("CHANNEL_NOTIFY_{}_{}".format(data["type"], data["id"]))
    if notified:
        return False
    cache.set("CHANNEL_NOTIFY_{}_{}".format(data["type"], data["id"]), True,
              timeout=7*24*60*60)
    return True


def send_notice_instance_rejected(user, instance_type_fa, company):
    subject = '{} رد شد'.format(instance_type_fa)
    message = render_to_string('rejected_content.html', {
        "instance_type_fa": instance_type_fa,
        "company_name": company.name,
        "company_slug": company.company_slug,
    })
    send_mail(subject=subject, message='', from_email=None,
              recipient_list=[user.email], html_message=message)


def get_compnay(instance, instance_type):
    if instance_type in ('review', 'interview', 'question'):
        return instance.company
    elif instance_type == 'answer':
        return instance.question.company
    elif instance_type == 'review_comment':
        return instance.review.company
    elif instance_type == 'interview_comment':
        return instance.interview.company
