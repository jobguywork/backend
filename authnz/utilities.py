import magic

from django.core.files.storage import default_storage
from django.conf import settings
from django.core.files.base import ContentFile
from django.db.models import Avg, Count


def file_upload_saver(user_slug, file, company_slug):
    file.seek(0)
    file_type = settings.KNOWN_EXTENSION.get(magic.from_buffer(file.read(), mime=True))
    file.seek(0)
    file_byte = file.read()
    file_name = file.name.split('.')[0]
    if company_slug:
        url = '{}/{}/{}'.format(
            str(user_slug),
            str(company_slug),
            str(file_name) + file_type
        )
    else:
        url = '{}/{}'.format(
            str(user_slug),
            str(file_name) + file_type
        )
    file = ContentFile(file_byte)
    if default_storage.exists(url):
        default_storage.delete(url)
    file = default_storage.save(url, file)
    return file


def handle_user_total_rate(user):
    rvs = user.companyreview_set.aggregate(avg=Avg('over_all_rate'), count=Count('over_all_rate'))  # review set
    ivs = user.interview_set.aggregate(avg=Avg('total_rate'), count=Count('total_rate'))  # interview set
    tr = rvs['count'] + ivs['count']
    ra = (((rvs['avg'] or 0) * rvs['count'] + (ivs['avg'] or 0) * ivs['count']) / tr) if tr else 0
    return tr, ra
