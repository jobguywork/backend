import magic
from django.conf import settings
from django.utils.translation import ugettext as _
from rest_framework import serializers

from config.utilities import get_int_config_value


def file_validator(file):
    """
    file validator

    check type of file is supported or not
    check max file size allowed for file

    :param file:
    :return:
    """
    mime = magic.from_buffer(file.read(), mime=True)
    file_type = settings.KNOWN_EXTENSION.get(mime)
    file.seek(0)
    if not file_type:
        raise serializers.ValidationError(_('{} type is not supported'.format(mime)))
    max_file_size = get_int_config_value('MAX_FILE_SIZE')
    if file.size > max_file_size:
        raise serializers.ValidationError(_('Max file size is {} and your file size is {}'.
                                          format(max_file_size, file.size)))


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField(validators=[file_validator])
    slug = serializers.SlugField(max_length=150, min_length=5)


class MergeCompanySerializer(serializers.Serializer):
    src = serializers.IntegerField()
    des = serializers.IntegerField()
