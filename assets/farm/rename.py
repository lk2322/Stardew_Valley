import os
path = os.path.curdir
for file_name in os.listdir(path):
    # Имя файла и его формат
    base_name, ext = os.path.splitext(file_name)

    # Нужны файлы определенного формата
    if ext.lower() not in ['.png']:
        continue

    # Полный путь к текущему файлу
    abs_file_name = os.path.join(path, file_name)

    # Полный путь к текущему файлу с новым названием
    try:
        int(file_name[5:9])
    except Exception:
        continue

    os.rename(abs_file_name, file_name[:5] + file_name[10:])
    print(file_name[:5] + file_name[10:])
