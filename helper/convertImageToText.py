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
from datetime import datetime
import pathlib
import logging

logging.basicConfig(filename='ocr.log',level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Parameter to adjust According Your Screen Size (Should have the same value as the converter)
# 11240
HEADER_SIZE 	 = 40
SCREEN_LENGTH    = 51 
SCREEM_WIDTH  	 = 220 # 55 Hex
CORRECTION_DELTA = - 20

def getMD5(text):
	nospacenoLine = text.replace('\n','').replace(' ','')
	#Convert file to Hex
	binstr = nospacenoLine[40:]
	i=0
	text = ''
	while i < len(binstr):
		binStr = binstr[i:i+4]
		i=i+4
		hexStr = hex(int(binStr, 2))[2:]
		text = text + hexStr

	md5 = hashlib.md5(text.encode()).hexdigest()
	
	return md5

def imageToText(in_dir,file,binData,errors,metadata,totalImagesArg,allMd5):
	#print('###### ##### file',file)
	# Read the input image in grayscale
	image = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
	if image is None:
	    logger.info("Error: Could not open or read the image.",file)
	    return
	custom_config = r'tessedit_char_whitelist=01'
	text = pytesseract.image_to_string(image,config=custom_config) 
	originalText = text


	res = True
	#Check if valid based om MD5
	#Check if image is correct : max 40 lines. Eache line has 50, first one has 12
	lines = text.split('\n')
	numberOflines = len(lines)
	magicNumber = lines[0]
	#print('numberOflines ',numberOflines)
	#print('magicNumber ',magicNumber)
	errorMsg = ''
	
	fileNumber=0
	text = text.replace('\n','').replace(' ','')
	try:
		totalfileNumber = int(text[20:40], 2)
		fileNumber = int(text[:20], 2)#start from 1
		#logger.info('fileNumber %i ',fileNumber)

		#CHECK_1 : Check the magic number is correct
		#print('totalfileNumber ',totalfileNumber,' totalImagesArg ',totalImagesArg,' len(text) = ',len(text))
		if not totalfileNumber == totalImagesArg:
			res = False
			errorMsg = 'Wrong magic Number(1)'
		

		#CHECK_2 :  Check if file complete
		unitFileSize = SCREEN_LENGTH*SCREEM_WIDTH + HEADER_SIZE + CORRECTION_DELTA
		if res and (fileNumber < totalfileNumber and len(text)<11240):
			res = False
			errorMsg = 'Incomplete Image'
			#print(errorMsg)

		#CHECK_3 :  Check if contains only 1 and 0
		if res :
			characters = [char for char in text]
			characters = list(set(characters))

		if res and (not len(characters)==2):
			res = False
			errorMsg = 'Wrong binary ' #+str(characters)
			#If only one carcter then keep for further processing
			if len(characters) == 3 :
				characters.remove('0')
				characters.remove('1')
				suppCar = characters[0]
				suppCar = binascii.hexlify(suppCar.encode()).decode()
				dir_path_toReview = in_dir+'/04-ImagesToReview/'+suppCar
				dir_path_hexToReview = in_dir+'/05-HexToReview'

				os.system('mkdir -p ' + dir_path_toReview)
				os.system('cp '+file+' '+dir_path_toReview+'/'+str(fileNumber)+'.png')
				
				with open(dir_path_hexToReview+'/'+str(fileNumber)+'.txt','w') as f :
					f.write(originalText)
				#print('Wrong binary ' +str(characters),' fileNumber ',fileNumber,file)
		
		#CHECK_4 : Check MD5 if exists
		if res :
			md5 = getMD5(text)
			if res and not allMd5[str(fileNumber)]==md5:
				res = False
				errorMsg = 'WRONG MD5'

	except :
		res = False
		errorMsg = 'Wrong magic number(2)'


	if res :
		text = text[40:]
		if not fileNumber in binData:	
			metadata['sucess']=metadata['sucess']+1
			binData[fileNumber]=text
			logger.info('Success fileNumber %i ',fileNumber)
			#Save text
			hexPath = in_dir+'/03-validTextFiles'
			validImgPath = in_dir+'/02-validImageFiles'
			if not (os.path.isfile(validImgPath+'/'+str(fileNumber)+'.png')):
				os.system('cp '+file+' '+validImgPath+'/'+str(fileNumber)+'.png')
				with open(hexPath+'/'+str(fileNumber)+'.txt','w') as f :
					f.write(originalText)

				metadata['newfile']=metadata['newfile']+1
				

		metadata['totalFiles']=	totalfileNumber			
		
	else :	
		if 	errorMsg in errors :
			errors[errorMsg] = 1 + errors[errorMsg]
		else :
			errors[errorMsg] = 1	

	os.system('mv '+file+' '+in_dir+'//01-processed//')

	#if fileNumber in [162, 331, 653, 660, 681, 687, 703, 725, 738, 740, 743, 744, 752, 766, 790, 791, 838, 843, 856, 870, 875, 900, 902, 916, 918, 926, 931, 942, 958, 976, 984, 987, 988, 989, 990, 1039, 1040, 1047, 1110, 1124, 1126, 1130, 1145, 1170, 1187, 1189, 1196, 1213, 1228, 1229, 1230, 1240, 1322, 1326, 1327, 1334, 1338, 1382, 1411, 1412, 1476, 1477, 1538, 1559, 1561, 1562, 1563, 1580, 1633, 1636, 1652, 1656, 1673, 1692, 1757, 1768, 1818, 1819, 1820, 1821, 1835, 1869, 1888, 1933, 1952, 1975, 1984, 1985, 1987, 1988, 1990, 1995, 1998, 2007, 2013, 2038, 2069, 2083, 2107, 2115, 2124, 2142, 2184, 2195, 2196, 2210, 2234, 2236, 2247, 2257, 2262, 2272, 2275, 2278, 2286, 2333, 2388, 2394, 2395, 2400, 2408, 2409, 2411, 2476, 2478, 2480, 2483, 2485, 2487, 2512, 2522, 2527, 2537, 2578, 2580, 2596, 2606, 2610, 2616, 2628, 2674, 2782, 2783, 2815, 2922, 2923, 2942, 2946, 2967, 2974, 2976, 3021, 3384, 3502, 3503, 3515, 3516, 3522, 3523, 3544, 3566, 3572, 3593, 3604, 3608, 3616, 3645, 3691, 3721, 3724, 3738, 3739, 3740, 3744, 3790, 3810, 3818, 3914, 3974, 3976, 3980, 3983, 4052, 4061, 4075, 4076, 4149, 4151, 4190, 4209, 4235, 4285, 4330, 4331, 4337, 4383, 4384, 4430, 4431, 4436, 4437, 4462, 4465, 4479, 4522, 4598, 4634, 4649, 4651, 4679, 4684, 4689, 4717, 4720, 4752, 4758, 5054]:
	if fileNumber and fileNumber < totalImagesArg:
		logger.info('fileNumber %i errors=%s',fileNumber,str(errorMsg))

	#logger.info('fileNumber=%i errorMsg=%s ',fileNumber,str(errorMsg))
	'''
	if fileNumber in [1557, 2428, 2585, 3019, 3067, 3728, 4428, 4444, 4995]:
		os.system('mkdir -p ' + in_dir+'//01-processed//'+str(fileNumber))
		os.system('mv '+file+' '+in_dir+'//01-processed//'+str(fileNumber)+'//')
	else:
		os.system('rm -rf '+file)
	'''


def showhelp():
		print('''Usage: python convertImageToText.py WorkingDir NumberOfValidFiles ...
	WorkingDir : Directory that contain the images
	NumberOfValidFiles : Number of total file to restore (see the output of encoding script)
	MD5File : MD5 for all files (optional)
			''')

if __name__ == "__main__":

	if len(sys.argv) < 3:
		showhelp()
		sys.exit(1)  

	in_dir = sys.argv[1]
	try :
		totalImagesArg = int(sys.argv[2])
	except:
		print('Error : ',sys.argv[2], 'is not a valid integer')
		showhelp()
		sys.exit(1)

	md5ForCheck = None
	allMd5 = {}
	if len(sys.argv) == 4 :
		md5ForCheck = sys.argv[3]		
		with open(md5ForCheck) as f :
			md5Files = f.readlines()
		for l in md5Files :
			findex,md5 = l.split(';')
			allMd5[findex]=md5.strip()

	#Working directories
	valid_hex_files_dir = in_dir+'/02-validImageFiles'

	os.system('mkdir -p ' +in_dir+'//01-processed')
	os.system('mkdir -p ' +valid_hex_files_dir)
	os.system('mkdir -p ' +in_dir+'/03-validTextFiles')
	os.system('mkdir -p ' +in_dir+'/04-ImagesToReview')
	os.system('mkdir -p ' +in_dir+'/05-HexToReview')
	
	file_list = [f for f in os.listdir(in_dir) if os.path.isfile(os.path.join(in_dir, f))]
	
	binData = {}
	errors = {}
	metadata = {'totalFiles':0,'sucess':0,'newfile':0}

	totalFrame = len(file_list)
	threadsPool = []

	max_pool = 50
	
	file_list.sort()

	for file_name in file_list:

		file = os.path.join(in_dir, file_name)

		thread = threading.Thread(target=imageToText, args=(in_dir,file,binData,errors,metadata,totalImagesArg,allMd5,))
		threadsPool.append(thread)

	i=0
	while i <len(threadsPool):
		runningThread = threadsPool[i:i+max_pool]		
		logger.info('Processing file from %i to %i/%i',i+1,max_pool + i + 1,totalFrame)
		for th in runningThread:
			th.start()
		for th in runningThread:
			th.join()
		i = max_pool + i
		logger.info('%i Files processed => (newfile=%i) & Success Rate :%i/%i',i,metadata['newfile'],metadata['sucess'],metadata['totalFiles'])
		
	logger.info('errors = %s ',str(errors))
	logger.info('Found %i  New Valid Files among a total of %i ',metadata['newfile'],metadata['sucess'])
	logger.info(' Applly the script decode.py to %s',in_dir+'/03-validTextFiles')
	# > /dev/null 2>&1 &



