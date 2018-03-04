from django.conf import settings

# Django will look within each of these paths for the <locale_code>/LC_MESSAGES
# directories containing the actual translation files.
# LOCALE_PATHS = [
#     '/home/www/project/common_files/locale',
#     '/var/local/translations/locale',
# ]

DEFAULT_TRANSLATION_IGNORE_PATTERNS = ['CVS', '.*', '*~', '*.pyc']
TRANSLATION_IGNORE_ROOTS = (
    settings.MEDIA_ROOT,
    settings.STATIC_ROOT
)
