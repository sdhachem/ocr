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

def decryptData(text,outputFileName):

	byte_data = binascii.unhexlify(text)

	with open(outputFileName,'wb') as f:
		f.write(byte_data)
	print('Data restored with sucess ....... Check output in ',outputFileName)

def binaryToHexString(text,fileIndex):

	nospacenoLine = text.replace('\n','').replace(' ','')

	#Check file Index for control
	fileIndexFromHeader = int(text[:20], 2)
	if not fileIndex == fileIndexFromHeader :
		raise Exception('Mismatch between file Index and File header Index=',fileIndex,' IndexFromHeader= ',fileIndexFromHeader)


	#Convert file to Hex
	binstr = nospacenoLine[40:]
	i=0
	text = ''
	modulo = len(binstr) % 4
	if modulo :
		print('Binary > 4!!!. FIleIndex=',fileIndex)


	while i < len(binstr):
		binStr = binstr[i:i+4]
		i=i+4
		hexStr = hex(int(binStr, 2))[2:]
		text = text + hexStr

	controledText = text
	md5 = hashlib.md5(controledText.encode()).hexdigest()
	
	return md5,controledText


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



def isThereMissingFiles(in_dir):
	missingf=[]
	#Check total Number of Files
	firstFilePath= os.path.join(in_dir, '1.txt')	
	if not os.path.isfile(firstFilePath):
		print('Why')
		return 0,[1]
	with open(firstFilePath) as f :
		text = f.read()
	text = text.replace('\n','').replace(' ','')
	nbfiles = int(text[20:40], 2)

	#Check missing File
	for i in range(nbfiles):
		path_ = os.path.join(in_dir, str(i+1)+'.txt')	
		second_path = os.path.join( in_dir+'/../05-HexToReview'	, str(i+1)+'.txt')	
		if not  os.path.isfile(path_)  :#and not  os.path.isfile(second_path) :
			missingf.append(i+1)
		'''
		elif i<15 :
			with open(path_) as f :
				text = f.read()
			md5,controledText =binaryToHexString(text) 
			print(i+1,md5)
		'''

	return nbfiles,missingf

def showhelp():
		print('''Usage: python decode.py hexFilesFOlder outputFileName ...
	hexFilesFOlder : Directory that contain the hex files (03-validTextFiles)
	outputFileName : If will be created in the current directory
	md5FIle : That contains MD5 for each file (optional)
			''')

if __name__ == "__main__":


	if len(sys.argv) < 3:
		showhelp()
		sys.exit(1)  

	in_dir = sys.argv[1]
	outputFileName = sys.argv[2]

	md5ForCheck = None
	allMd5 = {}
	if len(sys.argv) == 4 :
		md5ForCheck = sys.argv[3]
		with open(md5ForCheck) as f :
			md5Files = f.readlines()
		for l in md5Files :
			findex,md5 = l.split(';')
			allMd5[findex]=md5.strip()

	nbfiles,missingf = isThereMissingFiles(in_dir)
	if len(missingf):
		print('Error : Still missing ',len(missingf),' Files / ',nbfiles)
		#print(missingf)
		showMissingStats(missingf,nbfiles)
		sys.exit(1)

	print('All files are collected ... start decoding nbfiles=',nbfiles)

	file_list = [f for f in os.listdir(in_dir) if os.path.isfile(os.path.join(in_dir, f))]
	file_list.sort()
	encdata=''

	wrongHex = []
	for i in range(1,nbfiles+1) :
		file = os.path.join(in_dir, str(i)+'.txt')
		image = os.path.join(in_dir+'../02-validImageFiles/', str(i)+'.png')

		#print(file)
		with open(file) as f :
			text = f.read()

		md5,controledText =binaryToHexString(text,i) 
		#Check MD5 if provided
		if len(allMd5) and (not md5 == allMd5[str(i)]):
			#print('File ',i,' is wrong : Correct MD5 ', allMd5[str(i)],' Actual one is ',md5)
			wrongHex.append(i)
			os.system(' mv '+file+'  00-wrong_images_MD5/')
			os.system(' mv '+image+' 00-wrong_images_MD5/')

		encdata = encdata + controledText

	finalMd5 = hashlib.md5(encdata.encode()).hexdigest()
	print(' finalMd5 ',finalMd5)

	if not len(allMd5) or allMd5['end']==finalMd5:
		decryptData(encdata,outputFileName)
	else :
		print(wrongHex)
		print('Wrong :',len(wrongHex),'/',nbfiles)





