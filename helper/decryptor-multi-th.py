import sys
import binascii
import os
import pytesseract
from PIL import Image
import pytesseract 
import cv2
import numpy as np
import threading


def imageToText(in_dir,file,binData,errors,metadata,totalImagesArg):
	#print('###### ##### file',file)
	# Read the input image in grayscale
	image = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
	if image is None:
	    print("Error: Could not open or read the image.",file)
	    return
	custom_config = r'tessedit_char_whitelist=01'

	text = pytesseract.image_to_string(image,config=custom_config) 
	originalText = text
	#print('Image converted')
	#print(text)

	#Check if image is correct : max 40 lines. Eache line has 50, first one has 12
	lines = text.split('\n')
	numberOflines = len(lines)
	magicNumber = lines[0]
	#print('numberOflines ',numberOflines)
	#print('magicNumber ',magicNumber)
	errorMsg = ''
	res = True
	fileNumber=0
	text = text.replace('\n','').replace(' ','')
	try:
		totalfileNumber = int(text[20:40], 2)
		fileNumber = int(text[:20], 2)#start from 1
		
		#Check the magic number is correct
		#print('totalfileNumber ',totalfileNumber,' totalImagesArg ',totalImagesArg)
		if not totalfileNumber == totalImagesArg:
			res = False
			#print('Invalid File  magicNumber=',magicNumber,' Path='+file+': Wrong bi>
			errorMsg = 'Wrong magic Number'
			#print(text)
			#print(errorMsg)
		
		#check if file complete
		if fileNumber == totalfileNumbe :
			print('DEBUG ==> length of last file ',len(text),' compare to 11240')
		if fileNumber < totalfileNumber and len(text)<11240:
			res = False
			#print('Invalid File  characters=',characters,' Path='+file+': Wrong binary ' )
			errorMsg = 'Incomplete Image'
			#print(errorMsg)

		#Check if connatains only 1 and 0
		characters = [char for char in text]
		characters = list(set(characters))

		if not len(characters)==2:
			res = False
			#print('Invalid File  characters=',characters,' Path='+file+': Wrong binary ' )
			errorMsg = 'Wrong binary ' #+str(characters)
			'''
			if len(characters)==3 and (('4' in characters ) or ('9' in characters )) :
				res = True
				text = text.replace('4','1')
				text = text.replace('2','1')
				text = text.replace('9','0')
			elif len(characters)==3 :
				print(errorMsg,file)
				#print(errorMsg)
				#with open('originalText.txt','w') as f :
				#	f.write(originalText)
			'''
			
	except :
		#print('Invalid File  magicNumber=',str(magicNumber),' Path='+file+': Wrong magic number ' )
		res = False
		#errorMsg = 'Wrong magic number'
		#return False,None,'Wrong magic number',0



	'''
	if res :
		if not len(magicNumber) ==40 :
			#print('Invalid File  magicNumber=',str(magicNumber),' Path='+file+': Wrong magic number ' )
			res = False
			errorMsg = 'Wrong magic number'
			#return False,None,'Wrong magic number',totalfileNumber
		
		for i in range(1,numberOflines-2):
			lineLength = len(lines[i])
			if not lineLength ==220 and not len(lines[i]) ==0 :
				#print(' length  ==> ',len(text.replace('\n','').replace(' ','')))
				#print('Invalid File (',str(fileNumber),') Path='+file+': Incomplete Line ',lineLength )
				res = False
				errorMsg = 'Incomplete Line'
	'''

	#At the end of threads : binData Json and errors Json
	if res :
		
		#text = text.replace('\n','').replace(' ','')		
		text = text[40:]
		if not fileNumber in binData:	
			metadata['sucess']=metadata['sucess']+1
			binData[fileNumber]=text

			#Save text
			hexPath = in_dir+'/../../02-hexFiles/'+'/'+str(fileNumber)+'.txt'
			with open(hexPath) as f :
				f.write(originalText)
			

		metadata['totalFiles']=	totalfileNumber			
		#print('mv '+file+' '+in_dir+'//00-valid//'+str(fileNumber)+'.png')	

		if not (os.path.isfile(in_dir+'/../../01-validImages/'+'/'+str(fileNumber)+'.png')):
			os.system('cp '+file+' '+in_dir+'/../../01-validImages/'+'/'+str(fileNumber)+'.png')
			metadata['newfile']=metadata['newfile']+1
		
		#print('mv '+file+' '+in_dir+'//00-valid//'+str(fileNumber)+'.png')
		os.system('mv '+file+' '+in_dir+'//00-valid//'+str(fileNumber)+'.png')

		totalFiles = totalfileNumber
		
		#print('###### #####')
		#print(file,' processed => number :',fileNumber,'/',totalfileNumber)
	else :
		#print('mv '+file+' '+in_dir+'//01-invalid//')		
		os.system('mv '+file+' '+in_dir+'//01-invalid//')
		#print(errorMsg)
		errors[fileNumber] = {'msg':errorMsg}		
		

def decryptData(binstr):

	i=0
	text = ''
	while i < len(binstr):
		binStr = binstr[i:i+4]
		i=i+4
		binStr=binStr.replace('2','1')
		hexStr = hex(int(binStr, 2))[2:]
		text = text + hexStr

	print("**** DEBUG ==>  Hex original decouped ",len(text),' ?? ==> 965992')
	byte_data = binascii.unhexlify(text)

	with open('00-output.7z','wb') as f:
		f.write(byte_data)
	print('Data restored with sucess ....... ')

if __name__ == "__main__":

	#File should to be named as 1,2,3,..etc
	in_dir = sys.argv[1]
	totalImagesArg = int(sys.argv[2])
	os.system('mkdir -p '+in_dir+'//00-valid')
	os.system('mkdir -p '+in_dir+'//01-invalid')
	file_list = [f for f in os.listdir(in_dir) if os.path.isfile(os.path.join(in_dir, f))]
	binData = {}
	errors = {}
	metadata = {'totalFiles':0,'sucess':0,'newfile':0}
	totalFiles = 0
	totalFrame = len(file_list)
	frameIndex = 1
	threadsPool = []
	fileCounters = 1


	max_pool = 50
	#os.environ['OMP_THREAD_LIMIT'] = '1'
	

	file_list.sort()
	for file_name in file_list:
		if file_name == '.DS_Store':
			continue
		fileCounters = fileCounters + 1
		file = os.path.join(in_dir, file_name)

		thread = threading.Thread(target=imageToText, args=(in_dir,file,binData,errors,metadata,totalImagesArg,))
		threadsPool.append(thread)

	i=0
	while i <len(threadsPool):
		runningThread = threadsPool[i:i+max_pool]		
		print('Processing file from ',i+1,' to ',max_pool + i + 1,' / ',totalFrame)
		for th in runningThread:
			th.start()
		for th in runningThread:
			th.join()
		i = max_pool + i
		print(i, ' Files processed => (newfile=',metadata['newfile'],') & Success Rate :',metadata['sucess'],'/',metadata['totalFiles'])
		

	#decrypt binary : generate 00-output.7

	#delete succefful duplicated image
	for fnb in binData :
		if fnb in errors:
			del errors[fnb]

	totalFiles = metadata['totalFiles']
	print('Total files = ',totalFiles)
	print('errors = ',errors)
	with open('errors.txt','a') as f :
		f.write('\nerrors : '+str(errors))

	filesComplete = True

	for i in range(1,totalImagesArg+1):
		if i not in binData:
			filesComplete = False
			#print('Missing files : ',i)
			with open('errors.txt','a') as f :
				f.write('\nMissing files : ' +str(i) +  '/'+str(totalImagesArg))

	if filesComplete :
		encdata = ''
		for i in range(1,len(binData)+1):
			encdata = encdata + binData[i]

		print('Total string encdata ',len(encdata))
		decryptData(encdata)




