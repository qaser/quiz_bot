import os

print(os.getcwd())
for d in os.listdir():
    os.chdir(f'{os.getcwd()}\{d}')
    for f in os.listdir():
        f_name, f_ext = os.path.splitext(f)
        f_ext = '.cbr'
        new_name = f'{f_name}{f_ext}'
        os.rename(f, new_name)
    os.chdir('..')
