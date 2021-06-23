from django.core.cache import cache

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
