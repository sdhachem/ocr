import sys
import binascii
import os
import pytesseract
from PIL import Image
import pytesseract 
import cv2
import numpy as np

def decryptData(text,outputFileName):
	binary_data = binascii.unhexlify(text.encode())
	with open(outputFileName,'wb') as f:
		f.write(binary_data)
	print('Data restored with sucess ....... Check output in ',outputFileName)

def showMissingStats(missingf,totalFiles):
	stats = {}
	print('Missing Files : ',len(missingf))
	for i in missingf :
		k = i // 100
		#print('k',k)
		if k*100 not in stats:
			stats[k*100] = {'missing':1,'max':i,'min':i,'delta':0,'list':[i]}
		else :
			stats[k*100]['missing'] = stats[k*100]['missing'] + 1
			stats[k*100]['max'] = max(i,stats[k*100]['max'])
			stats[k*100]['min'] = min(i,stats[k*100]['min'])
			stats[k*100]['delta'] = stats[k*100]['max'] -  stats[k*100]['min']+1
			stats[k*100]['list'].append(i)

	#sorted_stats = {k: v for k, v in sorted(stats.items(), key=lambda item: item[1])}

	#print(stats)
	totalRecordingTimeRequired = 0 # Based on  2 second 
	totalRecordingTimeRequiredOneByOne = 0 # Based on  2 second 


	TotalSleep = 3
	for a in stats:
		#if len(stats[a]['list'])>=20:
		print (a,' : ',stats[a]['missing'],' / ',stats[a]['delta'],'==> [',stats[a]['min'],',',stats[a]['max'],'] (',3*stats[a]['delta']//60,')',stats[a]['list'])
		#if len(stats[a]['list'])>=20:
		#	print(stats[a]['list'])
		totalRecordingTimeRequired = totalRecordingTimeRequired + stats[a]['delta']*TotalSleep
		totalRecordingTimeRequiredOneByOne = totalRecordingTimeRequiredOneByOne + stats[a]['missing']*(TotalSleep+3) # 5second open Powershel and changing the cmd

	h = totalRecordingTimeRequired // 3600
	m = (totalRecordingTimeRequired - h*3600)//60
	s = totalRecordingTimeRequired - h*3600 - m*60
	print('Total required time is (Option Interval) : ',totalRecordingTimeRequired,' Seconds ==> ',h,':',m,':',s)

	h = totalRecordingTimeRequiredOneByOne // 3600
	m = (totalRecordingTimeRequiredOneByOne - h*3600)//60
	s = totalRecordingTimeRequiredOneByOne - h*3600 - m*60
	print('Total required time is (Option one by one) : ',totalRecordingTimeRequiredOneByOne,' Seconds ==> ',h,':',m,':',s)	

	h = totalFiles*TotalSleep // 3600
	m = (totalFiles*TotalSleep - h*3600)//60
	s = totalFiles*TotalSleep - h*3600 - m*60
	print('Initial Total required time is : ',totalFiles*TotalSleep,' Seconds ==> ',h,':',m,':',s)	
	print(missingf)



def imageToText(input_image_path):
	print('###### #####')
	# Read the input image in grayscale
	image = cv2.imread(input_image_path, cv2.IMREAD_GRAYSCALE)
	if image is None:
	    print("Error: Could not open or read the image.",input_image_path)
	    return
	custom_config = r'tessedit_char_whitelist=01'

	text = pytesseract.image_to_string(image,config=custom_config) 

	#print(text)

	#Check if image is correct : max 40 lines. Eache line has 50, first one has 12
	lines = text.split('\n')
	numberOflines = len(lines)
	magicNumber = lines[0]
	#print('numberOflines ',numberOflines)
	#print('magicNumber ',magicNumber)
	try:
		totalfileNumber = int(text[20:40], 2)
		fileNumber = int(text[:20], 2)#start from 1
		print('fileNumber / totalfileNumber => ',fileNumber,'/',totalfileNumber)
		
		#if fileNumber == 1 :
		#	print(text)
	except :
		print('Invalid File  magicNumber=',str(magicNumber),' Path='+input_image_path+': Wrong magic number ' )
		return False,None,'Wrong magic number',0

	if not len(magicNumber) ==40 :
		print('Invalid File  magicNumber=',str(magicNumber),' Path='+input_image_path+': Wrong magic number ' )
		return False,None,'Wrong magic number',totalfileNumber
	for i in range(1,numberOflines-2):
		lineLength = len(lines[i])
		if not lineLength ==220 and not len(lines[i]) ==0 :
			#print(text)
			print('Invalid File (',str(fileNumber),') Path='+input_image_path+': Incomplete Line ',lineLength )
			return False,fileNumber,'Incomplete Line',totalfileNumber

	# if numberOflines >= 41 then 40 shoud contain
	text = text.replace('\n','')
	text = text[40:]
	return True,fileNumber,text,totalfileNumber

def decryptData(binstr):

	i=0
	text = ''
	while i < len(binstr):
		binStr = binstr[i:i+4]
		i=i+4
		hexStr = hex(int(binStr, 2))[2:]
		text = text + hexStr

	#print(text)
	byte_data = binascii.unhexlify(text)

	with open('00-output.7z','wb') as f:
		f.write(byte_data)
	print('Data restored with sucess ....... ')

if __name__ == "__main__":

	#File should to be named as 1,2,3,..etc
	in_dir = sys.argv[1]
	dataLabel = sys.argv[2]
	os.system('mkdir '+dataLabel)
	file_list = [f for f in os.listdir(in_dir) if os.path.isfile(os.path.join(in_dir, f))]

	binData = {}
	errors = {}
	totalFiles = 0
	for file_name in file_list:
		file = os.path.join(in_dir, file_name)
		if 'Frame' in file:
			res,fnb,text,totalFiles_ = imageToText(file)
			if res :
				#print('mv '+file+' '+dataLabel+''+str(fnb)+'.txt')
				os.system('mv '+file+' '+dataLabel+'//'+str(fnb)+'.txt')
				totalFiles = totalFiles_
				binData[fnb]=text
				print(file,' processed => number :',fnb)
			else :
				os.system('rm -rf '+file)
				errors[fnb] = {'msg':text}
	#decrypt binary : generate 00-output.7

	#delete succefful duplicated image
	for fnb in binData :
		if fnb in errors:
			del errors[fnb]

	print('Total files = ',totalFiles)
	print('errors = ',errors)
	with open('errors.txt','a') as f :
		f.write('\nerrors : '+str(errors))
	filesComplete = True
	if not totalFiles :
		filesComplete = False
		with open('errors.txt','a') as f :
			f.write('\n No Files found : ' + str(totalFiles))

	for i in range(1,totalFiles+1):
		if i not in binData:
			filesComplete = False
			#print('Missing files : ',i)
			with open('errors.txt','a') as f :
				f.write('\nMissing files : ' +str(i) +  '/'+str(totalFiles))

	if filesComplete :
		encdata = ''
		for i in range(1,len(binData)+1):
			encdata = encdata + binData[i]
		decryptData(encdata)




