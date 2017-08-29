import pathlib
import os

DEFAULT_PATH = '/daqroot'


# def path_getter(uri=DEFAULT_PATH):
#     path = pathlib.Path(uri)
#     if not os.path.exists(path.as_posix()):
#         path = pathlib.Path(DEFAULT_PATH)
#     directories, files = [], []
#     for entry in path.iterdir():
#         if not entry.name.startswith('.'):
#             if entry.is_dir():
#                 directories.append(entry)
#             else:
#                 files.append(entry)
#
#     directories = sorted(directories, key=lambda d: d.name.lower())
#     files = sorted(files, key=lambda f: f.name.lower())
#     return path, directories, files

DEFAULT_PATH = '/daqroot'
def path_getter(uri=DEFAULT_PATH):
    path = pathlib.Path(uri)
    if not os.path.exists(path.as_posix()):
        path = pathlib.Path(DEFAULT_PATH)
    return path, list(path.iterdir())
