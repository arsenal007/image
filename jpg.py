from PIL import Image
import sys
import os
import time
import datetime
import glob
import filecmp
import piexif
import errno
import os
import stat
import shutil


#dirName = "E:\\tmp\\Pictures"
dirName = "..\work"





extensions = ["jpg", "JPG", "mp4", "MP4", "3gp", "MOV", "3GP", "avi", "wmv",
              "WMV", "jpeg", "JPEG", "MOD", "mov", "tiff", "TIFF", "NEF", "png", "gif", "GIF", "AVI","MPG","mpg"]


def get_minimum_creation_time(exif_data):
    mtime = "?"
    if 306 in exif_data and exif_data[306] < mtime:  # 306 = DateTime
        mtime = exif_data[306]
    # 36867 = DateTimeOriginal
    if 36867 in exif_data and exif_data[36867] < mtime:
        mtime = exif_data[36867]
    # 36868 = DateTimeDigitized
    if 36868 in exif_data and exif_data[36868] < mtime:
        mtime = exif_data[36868]
    return mtime


def min(x, y):
    if x > y:
        return y
    elif x < y:
        return x
    elif x == y:
        return x


def min3(x, y, z):
    return min(min(x, y), z)


def rename(modtime, file, ext):
    y = datetime.datetime.strftime(modtime, "%Y")
    m = datetime.datetime.strftime(modtime, "%Y-%m")
    if not os.path.exists(y):
        os.makedirs(y)
    sub_dir = os.path.join("", '%s/%s' % (y, m))
    if not os.path.exists(sub_dir):
        os.makedirs(sub_dir)
    format = "%Y-%m-%d_%H.%M.%S_%A." + ext
    basename = os.path.basename(datetime.datetime.strftime(modtime, format))
    head, tail = os.path.splitext(basename)
    dst_file = os.path.join("", '%s/%s' % (sub_dir, basename))
    # rename if necessary
    count = 0
    while os.path.exists(dst_file) and (not filecmp.cmp(file, dst_file)):
        count += 1
        dst_file = os.path.join("", '%s/%s_%d%s' %
                                (sub_dir, head, count, tail))
    # print '%s -> %s' % (file, dst_file)
    print(file, dst_file, sep=' -> ', end=']\n', file=sys.stdout, flush=False)
    os.replace(file, dst_file)


def f_try(file, format):
    try:
        name_time = datetime.datetime.strptime(file.decode("utf-8"), format)
    except ValueError:
        return (False, "")
    return (True, name_time)


def exif(file):
    #dict = piexif.load(file)
    #l = len(dict)
    return (True)


def get_ext(name):
    base, ext = os.path.splitext(name)
    return ext[1:]


def is_ext(name, ext):
    return get_ext(name) == ext


'''
    For the given path, get the List of all files in the directory tree 
'''


def getListOfFiles(dirName, ext):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
    allFiles = []
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath, ext)
        elif is_ext(entry, ext):
            allFiles.append(fullPath)

    return allFiles


def handleRemoveReadonly(func, path, exc):
    excvalue = exc[1]
    if func in (os.rmdir) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)
    else:
        raise


def clean(dirr):
    dirContents = os.listdir(dirr)
    if not os.access(dirr, os.W_OK):
        os.chmod(dirr, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

    if len(dirContents) == 0:
        # os.remove(dirr)
        shutil.rmtree(dirr, ignore_errors=False, onerror=handleRemoveReadonly)
    else:
        for f in dirContents:
            fullPath = os.path.join(dirr, f)
            if os.path.isdir(fullPath):
                clean(fullPath)


def ren(file, ext):
    formats = ["%Y-%m-%d %H.%M.%S." + ext, "%Y-%m-%d_%H.%M.%S_%A." + ext, "%Y-%m-%d_%H.%M.%S_%A_1." + ext, "%Y-%m-%d_%H.%M.%S_%A_2." + ext, "%Y-%m-%d_%H.%M.%S_%A_3." + ext, "%Y-%m-%d_%H.%M.%S_%A_4." + ext,
               "%Y-%m-%d_%H.%M.%S_%A_5." + ext, "IMG_%Y%m%d_%H%M%S." + ext, "IMG_%Y%m%d_%H%M%S_1." + ext, "IMG_%Y%m%d_%H%M%S_2." + ext, "VID_%Y%m%d_%H%M%S." + ext, "%Y%m%d_%H%M%S." + ext, "%Y%m%d_%H%M%S-ANIMATION." + ext]
    i = 0
    for f in formats:
        res = f_try(file, f)
        if res[0]:
            name_time = res[1]
            mod_time = datetime.datetime.strptime(time.ctime(
                os.path.getmtime(file)), "%a %b %d %H:%M:%S %Y")
            try:
                img_file = Image.open(file)
                create_time = get_minimum_creation_time(img_file._getexif())

                img_time = datetime.datetime.strptime(
                    create_time, "%Y:%m:%d %H:%M:%S")
                new_time = min3(mod_time, name_time, img_time)
                img_file.close()
            except OSError:
                new_time = min(mod_time, name_time)
            except (AttributeError, TypeError, ValueError) as e:
                new_time = min(mod_time, name_time)
                img_file.close()
            rename(new_time, file, ext)
            return

    s = time.ctime(os.path.getmtime(file))
    modtime = datetime.datetime.strptime(s, "%a %b %d %H:%M:%S %Y")
    try:
        img_file = Image.open(file)
        img_time = datetime.datetime.strptime(
            get_minimum_creation_time(img_file._getexif()), "%Y:%m:%d %H:%M:%S")
        new_time = new_time = min(modtime, img_time)
        img_file.close()
    except OSError:
        new_time = modtime
    except:
        new_time = modtime
        img_file.close()
    rename(new_time, file, ext)
    return

#==============================================
# fix
# input: filename with arbitrarery extension
# output: filename with lower case extension
# example 1.JPG -> 1.jpg
#==============================================


def fix(name):
    base, ext = os.path.splitext(name)
    return base + ext.lower()


if __name__ == "__main__":
    fse = sys.getfilesystemencoding()

    for ext in extensions:
        list = getListOfFiles(dirName, ext)
        for file in list:
            head, teil = os.path.split(file)
            move_to = fix(teil)
            print(file.encode(fse), move_to.encode(fse), sep=' -> ',
                  end=' [', file=sys.stdout, flush=False)
            shutil.move(file.encode(fse), move_to.encode(fse))
            new_ext = get_ext(move_to.encode(fse))
            ren(move_to.encode(fse), new_ext.decode("utf-8"))
    clean(dirName)
    #input("Press Enter to continue...")
