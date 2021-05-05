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


