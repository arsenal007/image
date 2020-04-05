from PIL import Image
import sys, os, time, datetime, glob, filecmp, piexif




extensions=["jpg","JPG","mp4","MP4","3gp","MOV","3GP","avi","wmv","WMV","jpeg","JPEG","MOD","mov","tiff","TIFF", "NEF","png","gif","AVI"]


def get_minimum_creation_time(exif_data):
    mtime = "?"
    if 306 in exif_data and exif_data[306] < mtime: # 306 = DateTime
        mtime = exif_data[306]
    if 36867 in exif_data and exif_data[36867] < mtime: # 36867 = DateTimeOriginal
        mtime = exif_data[36867]
    if 36868 in exif_data and exif_data[36868] < mtime: # 36868 = DateTimeDigitized
        mtime = exif_data[36868]
    return mtime



def min(x,y):
	if x>y:
		return y
	elif x<y:
		return x
	elif x==y:
		return x
def min3(x,y,z):
      return min(min(x,y),z)	

def rename( modtime, file, ext ):
	y = datetime.datetime.strftime(modtime,"%Y")
	m = datetime.datetime.strftime(modtime,"%Y-%m")
	if not os.path.exists(y):
		os.makedirs(y)
	sub_dir = os.path.join("", '%s/%s' % ( y, m ))
	if not os.path.exists(sub_dir):
		os.makedirs(sub_dir)
	format="%Y-%m-%d_%H.%M.%S_%A."+ext
	basename = os.path.basename( datetime.datetime.strftime(modtime,format) )
	head, tail = os.path.splitext( basename )
	dst_file = os.path.join("", '%s/%s' % ( sub_dir, basename))
	# rename if necessary
	count = 0
	while os.path.exists(dst_file) and (not filecmp.cmp(file,dst_file)):
		count += 1
		dst_file = os.path.join("", '%s/%s_%d%s' % ( sub_dir, head, count, tail))
	#print '%s -> %s' % (file, dst_file)
	print(file, dst_file, sep=' -> ', end='\n', file=sys.stdout, flush=False)
	os.replace(file, dst_file)

def f_try(file,format):
	try:
		name_time=datetime.datetime.strptime(file, format)
	except ValueError:
		return (False, "")
	return (True, name_time)

def exif(file):
	#dict = piexif.load(file)
	#l = len(dict)	
	return (True)

#def try_img(file):
	
		
def ren(file,ext):
	formats = ["%Y-%m-%d %H.%M.%S."+ext,"%Y-%m-%d_%H.%M.%S_%A."+ext, "%Y-%m-%d_%H.%M.%S_%A_1."+ext, "%Y-%m-%d_%H.%M.%S_%A_2."+ext, "%Y-%m-%d_%H.%M.%S_%A_3."+ext, "%Y-%m-%d_%H.%M.%S_%A_4."+ext, "%Y-%m-%d_%H.%M.%S_%A_5."+ext, "IMG_%Y%m%d_%H%M%S."+ext,"IMG_%Y%m%d_%H%M%S_1."+ext,"IMG_%Y%m%d_%H%M%S_2."+ext, "VID_%Y%m%d_%H%M%S."+ext, "%Y%m%d_%H%M%S."+ext,"%Y%m%d_%H%M%S-ANIMATION."+ext ]
	i=0
	for f in formats:
		res = f_try(file,f)
		if res[0]:
			name_time = res[1]
			mod_time=datetime.datetime.strptime(time.ctime(os.path.getmtime(file)),"%a %b %d %H:%M:%S %Y")
			try:
			   img_file=Image.open(file)
			   create_time=get_minimum_creation_time(img_file._getexif())

			   img_time=datetime.datetime.strptime(create_time,"%Y:%m:%d %H:%M:%S")
			   new_time=min3(mod_time,name_time,img_time)
			   img_file.close()
			except OSError:
				new_time=min(mod_time,name_time)
			except (AttributeError, TypeError) as e:
			 	new_time=min(mod_time,name_time)
			 	img_file.close()
			rename(new_time, file, ext)
			return
				
	s=time.ctime(os.path.getmtime(file))
	modtime=datetime.datetime.strptime(s, "%a %b %d %H:%M:%S %Y")
	try:
	   img_file=Image.open(file)
	   img_time=datetime.datetime.strptime(get_minimum_creation_time(img_file._getexif()),"%Y:%m:%d %H:%M:%S")
	   new_time=new_time=min(modtime,img_time)
	   img_file.close()
	except:
	   new_time = modtime
	img_file.close()	
	rename(new_time, file, ext)
	return

for ext in extensions:
	for file in glob.glob("*."+ext):
		ren(file,ext)
input("Press Enter to continue...")		

