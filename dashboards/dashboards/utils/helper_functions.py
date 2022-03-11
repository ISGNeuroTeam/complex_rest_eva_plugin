import os


def make_unique_name(path_template, name, num=0):
    if os.path.exists(path_template.format(name)):
        num = num + 1
        if not os.path.exists(path_template.format(f'{name}-{num}')):
            return name
        else:
            make_unique_name(path_template, name, num)
    return name