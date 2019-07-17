import os


def list_directory(directory):
    return [
        os.path.join(parent, name)
        for (parent, subdirs, files) in os.walk(directory)
        for name in files + subdirs
    ]


def list_sub_directory(base_directory, sub_directory):
    directory = os.path.join(base_directory, sub_directory)
    return [e[len(directory):] for e in list_directory(directory)]
