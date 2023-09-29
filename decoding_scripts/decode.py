import sys
import binascii
import os
import pytesseract
from PIL import Image
import pytesseract 
import cv2
import numpy as np
import threading
import hashlib



def decode(text,outputFileName):

	binary_data = hex(int(text, 2))[2:]
	binary_data = binascii.unhexlify(binary_data)
	print('binary_data',len(binary_data))

	with open(outputFileName,'wb') as f:
		f.write(binary_data)
		
	print('Data restored with sucess ....... Check output in ',outputFileName)

def isThereMissingFiles(in_dir):

	#Find the total number of files
	all_files = os.listdir(in_dir)
	if all_files :
		any_valid_file = all_files[0]

	with open (os.path.join(in_dir, any_valid_file)	) as f :
		text = f.read().replace('\n','').replace('	','')
	
	nbfiles = int(text[52:72],2)

	missingf=[]
	if len(all_files)<nbfiles:#There is missing Files
		for i in range(nbfiles):
			path_ = os.path.join(in_dir, str(i+1)+'.txt')	
			if not  os.path.isfile(path_)  :
				missingf.append(i+1)
	

	return nbfiles,missingf

def showhelp():
		print('''Usage: python decode.py hexFilesFOlder outputFileName ...
	hexFilesFOlder : Directory that contain the hex files (03-validTextFiles)
	outputFileName : If will be created in the current directory
			''')

if __name__ == "__main__":


	if len(sys.argv) < 3:
		showhelp()
		sys.exit(1)  

	in_dir = sys.argv[1]
	outputFileName = sys.argv[2]

	nbfiles,missingf = isThereMissingFiles(in_dir)
	if len(missingf):
		print('Missing Files : ',missingf)
		print('Error : Still missing ',len(missingf),' Files / ',nbfiles)
		sys.exit(1)

	print('All files are collected ... start decoding nbfiles=',nbfiles)

	file_list = [f for f in os.listdir(in_dir) if os.path.isfile(os.path.join(in_dir, f))]
	file_list.sort()
	encdata=''

	wrongHex = []
	for i in range(1,nbfiles+1) :
		file = os.path.join(in_dir, str(i)+'.txt')
		with open(file) as f :
			text = f.read().replace('\n','').replace('	','')[112:]

		encdata = encdata + text

	decode(encdata,outputFileName)




