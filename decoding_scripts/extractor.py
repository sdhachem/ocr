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
import shutil

logging.basicConfig(filename='ocr.log',level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def imageToText(file,out_dir,binData,errors,metadata):
	# Read the input image in grayscale
	image = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
	if image is None:
	    logger.info("Error: Could not open or read the image.",file)
	    return
	custom_config = r'tessedit_char_whitelist=01'
	text = pytesseract.image_to_string(image,config=custom_config) 

	nospacenoLine = text.replace('\n','').replace('	','')
	#Convert file to Hex
	res = True
	errorMsg=''

	input_string_with_binary_only = nospacenoLine.replace('0', '').replace('1', '')
	

	if len(input_string_with_binary_only) :
			res = False
			errorMsg = 'OCR_FAIL'
	elif len(nospacenoLine)>=112:
		try:
			crc = int(nospacenoLine[0:32],2)
			fileIndex = int(nospacenoLine[32:52],2)
			fileNb = int(nospacenoLine[52:72],2)
			screen_length = int(nospacenoLine[72:92],2)
			screen_width = int(nospacenoLine[92:112],2)
			screenSize = screen_length*screen_width

			dataShunk = nospacenoLine[112:]
			crc32_checksum = binascii.crc32(dataShunk.encode())
			#print(file,'fileIndex',fileIndex,'fileNb ',fileNb,' screen_length',screen_length,' screen_width',screen_width,'crc',nospacenoLine[0:32])
			
			if not crc == crc32_checksum : #Incorrect Image
				errorMsg = 'WRONG_CRC'
				res = False
				#logger.debug('Wrong CRC fileNumber=%i file=%s ',fileIndex,file)

			#Just for debug to remove
			if not res and (fileIndex<fileNb) and (len(dataShunk)==screenSize) and not len(input_string_with_binary_only):
				logger.debug('DEBUG - good canidate for fileNumber=%i file=%s ',fileIndex,file)
				shutil.copy(file, DEBUG_DIR)
		except :
			res = False
			errorMsg = 'WRONG_MAGIC_HEADER'
			raise
			
	else :
			res = False
			errorMsg = 'MISSING_MAGIC_HEADER'		

	if res :
		metadata['sucess']=metadata['sucess']+1
		if not fileIndex in binData:	
			binData[fileIndex]=dataShunk			
			metadata['totalFiles']=	fileNb

		if not (os.path.isfile(VALID_IMAGE_DIR+'/'+str(fileIndex)+'.png')):#Not already copied
			shutil.copy(file, VALID_IMAGE_DIR+'/'+str(fileIndex)+'.png')
			metadata['newfile']=metadata['newfile']+1

		with open(VALID_TEXT_DIR+'/'+str(fileIndex)+'.txt','w') as f :
			f.write(text)
	else :
		if 	errorMsg in errors :
			errors[errorMsg] = 1 + errors[errorMsg]
		else :
			errors[errorMsg] = 1	

	try :
		shutil.move(file, PROCESSED_IMAGES)
	except :
		os.remove(file)

	#logger.debug('Last errorMsg=[%s] res=[%s] ',str(errorMsg),str(res))
		

def showhelp():
		print('''Usage: python convertImageToText.py in_dir ...
	in_dir : Directory that contain the images
			''')

if __name__ == "__main__":

	if len(sys.argv) < 2:
		showhelp()
		sys.exit(1)  

	in_dir = sys.argv[1]
	out_dir = in_dir#sys.argv[2]

	print('For more logs detail ==> tail -f ./ocr.log')
	#Create working directory
	if not os.path.exists(out_dir):
		os.mkdir(out_dir)
	VALID_IMAGE_DIR  =out_dir+'/01-validImages'
	VALID_TEXT_DIR   =out_dir+'/02-validText'
	PROCESSED_IMAGES =out_dir+'/00-processed'
	DEBUG_DIR 		 =out_dir+'/03-debug'
	if not os.path.exists(VALID_IMAGE_DIR):
		os.mkdir(VALID_IMAGE_DIR)
	if not os.path.exists(VALID_TEXT_DIR):
		os.mkdir(VALID_TEXT_DIR)
	if not os.path.exists(PROCESSED_IMAGES):
		os.mkdir(PROCESSED_IMAGES)
	if not os.path.exists(DEBUG_DIR):
		os.mkdir(DEBUG_DIR)
	
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
		#imageToText(file,in_dir,binData,errors,metadata)
		thread = threading.Thread(target=imageToText, args=(file,in_dir,binData,errors,metadata,))
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
	logger.info('Found %i  New Valid Files among a total of %i ',metadata['newfile'],metadata['totalFiles'])
	logger.info(' Applly the script decode.py to %s',VALID_TEXT_DIR)
	# > /dev/null 2>&1 &



