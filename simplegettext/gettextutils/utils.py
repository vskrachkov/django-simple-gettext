import fnmatch
import os

from django.conf import settings
from django.core.files.temp import NamedTemporaryFile
from django.core.management.utils import handle_extensions, popen_wrapper

from . import consts


def is_ignored_path_pattern(path, ignore_patterns):
    """Check that taken path pattern is match the list of the path patterns
    which must be ignored on selecting translatable strings.
    """
    # copy pasted from:
    # line: 457, file: django.core.management.commands.makemessages

    filename = os.path.basename(path)

    def ignore(pattern):
        # returns first matching pattern of nothing
        return fnmatch.fnmatchcase(filename, pattern) \
               or fnmatch.fnmatchcase(path, pattern)

    # returns true if any filename match the ignore pattern
    return any(ignore(pattern) for pattern in ignore_patterns)


def find_translatable_files(start_path=settings.BASE_DIR, ignore=(),
                            extensions=()):
    """Returns list of the paths to the files with translatable strings.

    :param start_path: path from which start search;
    :param ignore: ignore patterns;
    :param extensions: allowed file extensions;
    """
    # copy pasted with minimal changes from:
    # line: 457, file: django.core.management.commands.makemessages

    # define allowed for search file extensions
    extensions = handle_extensions(extensions)

    # define ignore patterns
    _ignore = consts.DEFAULT_TRANSLATION_IGNORE_PATTERNS + list(ignore)
    ignore_patterns = [os.path.normcase(p) for p in _ignore]

    # define directory suffixes
    dir_suffixes = {'%s*' % path_sep for path_sep in {'/', os.sep}}

    # define normalized ignore patterns that do not ends with dir suffix
    normalized_ignore_patterns = []
    for p in ignore_patterns:
        for dir_suffix in dir_suffixes:
            if p.endswith(dir_suffix):
                # if pattern ends with dir suffix just truncate it
                normalized_ignore_patterns.append(p[:-len(dir_suffix)])
                break
        else:
            normalized_ignore_patterns.append(p)

    # build ignored roots
    ignored_roots = [os.path.normpath(p) for p in
                     consts.TRANSLATION_IGNORE_ROOTS if p]

    # define list for storing paths to the files with translatable stings
    result_files = []

    for dirpath, dirnames, filenames in os.walk(start_path, topdown=True):
        for dirname in dirnames[:]:
            # relative path to the dirname
            _path = os.path.normpath(os.path.join(dirpath, dirname))

            # absolute path to the dirname
            _root = os.path.join(os.path.abspath(dirpath), dirname)

            # remove directories which are match ignore patterns
            if is_ignored_path_pattern(_path, normalized_ignore_patterns) \
                    or _root in ignored_roots:
                dirnames.remove(dirname)

            elif dirname == 'locale':
                dirnames.remove(dirname)

        for filename in filenames:
            file_path = os.path.normpath(os.path.join(dirpath, filename))
            file_ext = os.path.splitext(filename)[1]
            if not is_ignored_path_pattern(file_path, set(ignore_patterns)) \
                    or file_ext in extensions:

                result_files.append(os.path.join(dirpath, filename))
    return sorted(result_files)


def select_translatable_strings(files_list):
    """Returns translatable strings from the taken files list.

    :param files_list: list of the paths to the files with
        translatable strings
    :return: PO file string with selected translatable strings
    """
    # copy pasted with minimal changes from:
    # line: 457, file: django.core.management.commands.makemessages

    # for now we translate just Python files
    args = [
        'xgettext',
        '-d', 'translatable_messages',
        '--language=Python',
        '--keyword=gettext_noop',
        '--keyword=gettext_lazy',
        '--keyword=ngettext_lazy:1,2',
        '--keyword=ugettext_noop',
        '--keyword=ugettext_lazy',
        '--keyword=ungettext_lazy:1,2',
        '--keyword=pgettext:1c,2',
        '--keyword=npgettext:1c,2,3',
        '--keyword=pgettext_lazy:1c,2',
        '--keyword=npgettext_lazy:1c,2,3',
        '--output=-',
    ]

    with NamedTemporaryFile(mode='w+') as input_files_list:
        input_files_list.write(('\n'.join(files_list)))
        input_files_list.flush()
        args.extend(['--files-from', input_files_list.name])
        msgs, errors, status = popen_wrapper(args)

    return msgs, errors
