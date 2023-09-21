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

def binaryToHexString(text):

	nospacenoLine = text.replace('\n','').replace(' ','')
	binstr = nospacenoLine[40:]
	i=0
	text = ''
	while i < len(binstr):
		binStr = binstr[i:i+4]
		i=i+4
		binStr=binStr.replace('2','1')
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


	TotalSleep = 4
	for a in stats:
		if a > 0:
			print (a,' : ',stats[a]['missing'],' / ',stats[a]['delta'],'==> [',stats[a]['min'],',',stats[a]['max'],'] (',3*stats[a]['delta']//60,')')#,stats[a]['list'])
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




def isThereMissingFiles(in_dir):
	missingf=[]
	#Check total Number of Files
	firstFilePath= os.path.join(in_dir, '1.txt')	
	if not os.path.isfile(firstFilePath):
		return 0,[1]
	with open(firstFilePath) as f :
		text = f.read()
	text = text.replace('\n','').replace(' ','')
	nbfiles = int(text[20:40], 2)

	#Check missing File
	for i in range(nbfiles):
		path_ = os.path.join(in_dir, str(i+1)+'.txt')	
		second_path = os.path.join( in_dir+'/../05-HexToReview'	, str(i+1)+'.txt')	
		if not  os.path.isfile(path_) and not  os.path.isfile(second_path) :
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
		print('Error : Still missing ',len(missingf),' Files / ',nbfiles)
		#print(missingf)
		showMissingStats(missingf,nbfiles)
		sys.exit(1)

	file_list = [f for f in os.listdir(in_dir) if os.path.isfile(os.path.join(in_dir, f))]
	file_list.sort()
	encdata=''
	for i in range(1,len(file_list)+1) :
		file = os.path.join(in_dir, str(i)+'.txt')
		#print(file)
		with open(file) as f :
			text = f.read()

		md5,controledText =binaryToHexString(text) 
		#print(i,md5)

		with open(file) as f :
			encdata = encdata + controledText


	decryptData(encdata,outputFileName)




