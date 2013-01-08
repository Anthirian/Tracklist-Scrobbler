try:
    from distutils.core import setup
    import py2exe
    from glob import glob
    import sys, os
    import shutil
    import fnmatch
    import Parser, Scrobbler
except ImportError, message:
    raise SystemExit,  "Unable to load module. %s" % message

sys.argv.append('py2exe')

includes = ['pylast']
options = {'py2exe': {'bundle_files': 3, 'includes': includes, 'optimize': 2}}

def recursive_find_data_files(root_dir, allowed_extensions=tuple('*')):

    to_return = {}
    for (dirpath, dirnames, filenames) in os.walk(root_dir):
        if not filenames:
            continue

        for cur_filename in filenames:

            matches_pattern = False
            for cur_pattern in allowed_extensions:
                if fnmatch.fnmatch(cur_filename, '*.'+cur_pattern):
                    matches_pattern = True
            if not matches_pattern:
                continue

            cur_filepath = os.path.join(dirpath, cur_filename)
            to_return.setdefault(dirpath, []).append(cur_filepath)

    return sorted(to_return.items())

setup(
    name = 'Tracklist Scrobbler',
    version = '1.0',
    packages = [''],
    url = '',
    license = '',
    author = 'Geert',
    author_email = '',
    description = 'Tracklist Scrobbler allows you to scrobble the tracks that were played in a podcast. It parses a tracklist you provide into a last.fm-sanitized format. ',
    windows = [
        {
            'script': 'Interface.py',
            'icon_resources': [(0, "images\\tracklistscrobbler.ico")]
        }
    ],
    data_files = recursive_find_data_files('images', ['gif', 'png', 'jpg', 'ico']),
    options = options
)
