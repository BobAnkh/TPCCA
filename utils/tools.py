import os


def clear_folder(folder):
    del_list = os.listdir(folder)
    for f in del_list:
        file_path = os.path.join(folder, f)
        if os.path.isfile(file_path):
            os.remove(file_path)
