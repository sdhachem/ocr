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

def imageToText(in_dir,file,binData,errors,metadata,totalImagesArg):
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
		
		#CHECK_1 : Check the magic number is correct
		#print('totalfileNumber ',totalfileNumber,' totalImagesArg ',totalImagesArg,' len(text) = ',len(text))
		if not totalfileNumber == totalImagesArg:
			res = False
			errorMsg = 'Wrong magic Number'
		
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

	except :
		res = False
		errorMsg = 'Wrong magic number'


	if res :
		text = text[40:]
		if not fileNumber in binData:	
			metadata['sucess']=metadata['sucess']+1
			binData[fileNumber]=text

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



def showhelp():
		print('''Usage: python convertImageToText.py WorkingDir NumberOfValidFiles ...
	WorkingDir : Directory that contain the images
	NumberOfValidFiles : Number of total file to restore (see the output of encoding script)
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

	#Working directories
	valid_hex_files_dir = in_dir+'/02-validImageFiles'

	os.system('mkdir -p ' +in_dir+'//01-processed//')
	os.system('mkdir -p ' +valid_hex_files_dir)
	os.system('mkdir -p ' +in_dir+'/03-validTextFiles')
	os.system('mkdir -p ' +in_dir+'/04-ImagesToReview/')
	os.system('mkdir -p ' +in_dir+'/05-HexToReview/')
	
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

		thread = threading.Thread(target=imageToText, args=(in_dir,file,binData,errors,metadata,totalImagesArg,))
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



