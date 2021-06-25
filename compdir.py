import glob
import os
import re
import sys
import filecmp
import hashlib


def hashFile(file):
	h = hashlib.new('sha1')
	block_size = h.block_size * 4096
	with open(file, "rb") as f:
		BinaryData = f.read( block_size)
		while BinaryData:
			h.update(BinaryData)
			BinaryData= f.read(block_size)
	return h.hexdigest()

#
# Return
#   True: 2 files are the same
#   False: 2 files sre differ
def compfileex(srcfile,tgtfile):
	if not os.path.exists(srcfile):
		print(f"{srcfile} does not exist")
		return False
	if not os.path.isfile(srcfile):
		print(f"{srcfile} is not a file")
		return False
	
	if not os.path.exists(tgtfile):
		print(f"{tgtfile} does not exist")
		return False
	if not os.path.isfile(tgtfile):
		print(f"{tgtfile} is not a file")
		return False
	
	
	srcstat = os.stat( srcfile)
	tgtstat = os.stat( tgtfile)
	if srcstat.st_size != tgtstat.st_size:
		print(f"sizes differ:{srcfile}")
		return False
		

	srchash = hashFile(srcfile)
	tgthash = hashFile(tgtfile)
	if srchash != tgthash:
		print(f"hashes differ:{srcfile}")
		#hash differ
		return False
	
	issame = filecmp.cmp(srcfile,tgtfile)
	if not issame:
		print(f"binary data differ:{srcfile}")
		return False
	
	return True
	

def comp_single_dir( srcdir, tgtdir):
	print('comp_single_dir')
	details = []
	if not os.path.isdir(srcdir):
		print(f"{srcdir} is not a directory")
		return None
	
	files = glob.glob(srcdir +'\\*')
	for f in files:
		basename = os.path.basename( f)
		tgtfile = tgtdir + "\\" + basename
		if os.path.isfile(f):
			if os.path.exists(tgtfile):
				if os.path.isfile(tgtfile):
					print(f"comparing {f} and {tgtfile}\n")
					issame = compfileex(f, tgtfile)
					if not issame:
						print(f"{f} and {tgtfile} differ")
						details.append( {'path': f,'reason':'data differ'})
				else:
						print(f"{tgtfile} is not a file")
						details.append( {'path': f,'reason':'not a file in the target but a dir'})
					
			else:
				print(f"target file:{tgtfile} does not exist")
				details.append( {'path': f,'reason':'target file not found'})
		else:
			#for dir
			if os.path.exists(tgtfile):
				if os.path.isdir(tgtfile):
					sub_details = comp_single_dir(f, tgtfile)
					if sub_details:
						details.extend( sub_details)
				else:
					print(f"dir:{f} is not a dir but a file in the target dir")
					details.append( {'path': f,'reason':'not a dir in the target but a file'})
					
			else:
				print(f"target dir:{tgtfile} does not exist")
				details.append( {'path': f,'reason':'target dir not found'})
				
	return details

def existense_check(tgtdir, srcdir):
	non_exitense_list =[]
	
	files = glob.glob(tgtdir +'\\*')
	for f in files:
		basename = os.path.basename( f)
		srcfile = srcdir + "\\" + basename
		if os.path.isfile(f):
			if not os.path.exists(srcfile):
				print(f"target file:{tgtfile} does not exist in the source dir")
				details.append( {'path': f,'reason':'target file not found in the source dir'})
		else:
			#for dir
			if os.path.exists(srcfile):
				if os.path.isdir(srcfile):
					# both exist and a dir, go deeper
					sub_details = existense_check(f, srcfile)
					if sub_details:
						non_exitense_list.extend( sub_details)
				else:
					print(f"a file with the same name as target dir:{f} exists in source dir")
					non_existense_list.append( {'path': f,'reason':'the same name file as target dir'})
					
			else:
				print(f"target dir:{f} exists only on target dir")
				non_existense_list.append( {'path': f,'reason':'only on target dir'})
				
	return details
	
if len(sys.argv) <3 or len(sys.argv) > 4:
	print(f"Usage: {sys.argv[0]} <source dir> <target dir> [<log file name>]", file=sys.error)
#srcdir = "comics"
#tgtdir = "G:\\comics"
srcdir = sys.argv[1]
tgtdir = sys.argv[2]

logfile = "compdir.log"
if len(sys.argv) == 4:
	logfile = sys.argv[3]
log =open(logfile,"w")

if not os.path.isdir(srcdir) or not os.path.isdir(tgtdir):
	print("both arguments must be a directory")
	sys.exit()


details = comp_single_dir( srcdir, tgtdir)

if details:
	for info in details:
		log.write(info['reason'] + ': ' + info['path'] + '\n')

log.write("reverse check\n")
details = existense_check( tgtdir, srcdir)

if details:
	for info in details:
		log.write(info['reason'] + ': ' + info['path'] + '\n')

log.close()
