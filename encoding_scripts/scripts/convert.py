import sys
import os
import binascii
import hashlib

def appendInFile(fname,car):
    with open(fname,'a') as f :
        f.write(car)
def convertToBin(car) :
    #print(car)
    car = bin(int(car,16))[2:]
    length = len(car)
    padding = 4 - (length % 4) if length % 4 !=0 else 0
    car = "0" * padding + car
    #print(car)
    return car

        
  
def encodehex(hexstr):
    
    fsize = 2800
    hexlen = len(hexstr)
    print(hexlen)
    nbOfFiles = hexlen // fsize
    if(fsize % hexlen):
        nbOfFiles =  nbOfFiles+ 1
    print('nbOfFiles ',nbOfFiles)
    md5path = label + '/md5.txt'
    
    #Calculate md5 here
    zmd5 = hashlib.md5(hexstr.encode()).hexdigest()
    md5content = 'all;'+ zmd5 + '\n'
    appendInFile(md5path,md5content)
    
    debug_md5 = ''
    
    for i in range(nbOfFiles):
        fname = label+'/hex/'+str(i+1)+'.txt'
        nbOfFilesAsBin = format(nbOfFiles,'20b').replace(' ','0') 
        fileIndex = format(i+1,'20b').replace(' ','0') 
        appendInFile(fname,'\n      '+ fileIndex)
        appendInFile(fname,nbOfFilesAsBin)
        appendInFile(fname,'\n      ')
        
        startIndex = i*fsize
        endIndex = startIndex + fsize
        if endIndex > hexlen :
            endIndex = hexlen
            
        subhex = hexstr[startIndex:endIndex]
        nbOfWritedCar = 0
        
        for car in subhex :
            car = convertToBin(car)
            nbOfWritedCar = 1 + nbOfWritedCar
            appendInFile(fname,car)
            if nbOfWritedCar == 55 :
                appendInFile(fname,'\n      ')
                nbOfWritedCar = 0
                
        #Calculate md5 here
        zmd5 = hashlib.md5(subhex.encode()).hexdigest()
        md5content = str(i+1)+';'+ zmd5 + '\n'
        appendInFile(md5path,md5content)
        
        debug_md5  =  debug_md5     + subhex 
    
    #Calculate md5 here
    zmd5 = hashlib.md5(debug_md5.encode()).hexdigest()
    md5content = 'end;'+ zmd5 + '\n'
    appendInFile(md5path,md5content)    

filename = sys.argv[1]
label = sys.argv[2]
os.system('rmdir /s /q '+label)
os.system('mkdir  '+label+'\hex')
print("start")
print(filename)

with open (filename,'rb') as f:
    content = f.read()

hexstr = binascii.hexlify(content).decode()
#print(hexstr)

encodehex(hexstr)
