import sys
import binascii
import os
import pytesseract
from PIL import Image
import pytesseract 
import cv2
import numpy as np


# Replace 'your_directory_path' with the path to the directory you want to read


def split_image(input_image_path, output_folder):

    #We have 57 collumn
    #We have 36 row

    nbOfCol =100
    nbOfRow =40

    # Open the input image
    image = Image.open(input_image_path)

    # Get the width and height of the input image
    width, height = image.size

    rowSize = height // nbOfRow
    collSize = width // nbOfCol
    #splitByCollumn(image,rows,columns,size,width, height)
    return splitBySquare(image,width, height,collSize,rowSize,nbOfCol,nbOfRow)


def splitByOverigting (image,output_folder):
    #col :[0,width] row [0,height]
    # width = 2484 & height = 872
    #Change all the pixel image execept the Carac we want to keep
    # x <left & x>right and y < upper and y>lower 
    #width, height
    #print('width => ',width,' height = ',height)
    blank_color = image.getpixel((0, 0)) 
    new_image = Image.new("RGB", (width, height), (255, 255, 255))
    for x in range(width):
        for y in range(height):
            if (x > left) and (x < right) and (y <lower and y > upper ):
                #print('Continue we want to keep this')                         
                new_image.putpixel((x, y), image.getpixel((x, y)))
                continue

            new_image.putpixel((x, y), blank_color)

    new_image.save(f"{output_folder}/sub_image_{row}_{column}.png")

             

def findImageSparator(image,nbOfSeparator):

    sepPositions = []

    # Open the image
    width, height = image.size
    # Define the threshold for red color detection
    red_threshold = 100

    # Create a blank white image with the same size as the original image
    output_image = Image.new("RGB", image.size, (255, 255, 255))

    # Iterate through each pixel and apply the filter
    redPixels = []
    fisrtSpeartor = width
    firstPosition = (width,height)
    lowestYPos = height
    for y in range(image.height):
        if lowestYPos < height :
            y = lowestYPos
        for x in range(image.width):        
            pixel_color = image.getpixel((x, y))

            # Check if the pixel is red based on the red_threshold
            is_red_pixel = pixel_color[0] > red_threshold and pixel_color[1] < red_threshold and pixel_color[2] < red_threshold

            if is_red_pixel:
                lowestYPos = y
                redPixels.append(x)

    redPixels = list(set(redPixels))
    #print('redPixels => ',redPixels)
    #print('redPixels => ',len(redPixels))
    occurences = len(redPixels)//nbOfSeparator
    for sepIndex in range(nbOfSeparator):
        #print(sepIndex,' => ',redPixels[sepIndex*occurences])
        sepPositions.append(redPixels[sepIndex*occurences])

    sepPositions = sorted(sepPositions)
    print('sepPositions => ',sepPositions)
    print('len  sepPositions => ',len(sepPositions))

    
    return sepPositions



def splitBySquare(image,width, height,collSize,rowSize,nbOfCol,nbOfRow):
# Loop through each row and column to split the image
    #for row in range(rows):

    sepPositions = findImageSparator(image,40)
    content = {}
    failedCoding = {}

    startVerticallOffset = 5 # Increase if there big offset before first row : findtune if you increase by one the top of first car will be lost
    rowSize = 23 
    
    # Separator size of the left
    sepSizeLeft = 10
    # Separator size of the Right
    sepSizeRight = 10

    #nbOfRow = 2 # one row
    #sepPositions = sepPositions[:2]
    #nbOfCol=1
    #for column in range(nbOfCol):
    
    iteration = 1
    for row in range(nbOfRow):
        colIndex = 0
        previousSepator = -sepSizeRight
        previousUpper = startVerticallOffset + row * rowSize 
        # Calculate the cropping box for the current sub-image
        for column in sepPositions:

            #if colIndex > -1 :
            print('Iteration = ',iteration,'/',nbOfRow*len(sepPositions))
            iteration = iteration +1

            left = previousSepator + sepSizeRight
            right = column - sepSizeLeft
            previousSepator = column

            #print('Coll ',colIndex,':',left,'=>',right)
            upper = previousUpper #row * rowSize + startVerticallOffset   #Alwayse 0     
            lower = previousUpper + rowSize 
           

            # Crop the sub-image
            #print(left, upper, right, lower)
            sub_image = image.crop((left, upper, right, lower))
            res,text = imageToText(sub_image)
            
            if not res :
                print('Saving image with error',row,colIndex,' test : ',text)
                file = f"{output_folder}/sub_image_{row}_{colIndex}.png"
                sub_image.save(file)
                if text not in failedCoding:
                    failedCoding[text]=[file]
                    print("Non-ASCII characters found in :",file,text)
                else :
                    failedCoding[text].append(file)
            else :
                
                row = int(row)

                if row in content :
                    content[row][colIndex]=text
                else :
                    content[row] = {colIndex:text}
            colIndex = colIndex + 1

    return failedCoding,content

# List all files in the directory


def fixeWithCustomConvert(car):
    customDic = {'cc':'c','td':'7','re)':'5','t':'7','9g':'9','co)':'5'}

    if car in customDic :
        return customDic[car]

    return car


def imageToText(image):

    width, height = image.size

    #Open image
    #image = cv2.imread(input_image_path, cv2.IMREAD_GRAYSCALE)
    #if image is None:
    #    print("Error: Could not open or read the image.")
    #    return

    # Preprocessig
    #_, image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY)
    
    #image = cv2.resize(image, (width*2, height*2), interpolation=cv2.INTER_AREA)
    #cv2.imwrite(input_image_path, image)
    #cv2.imwrite('/tmp/tmp.png', binary_image)
    #image = cv2.imread('/tmp/tmp.png', cv2.IMREAD_GRAYSCALE)


    # Image to text
    custom_config = r'--oem 3 --psm 10 tessedit_char_whitelist=0123456789ABCDEF'
    text = pytesseract.image_to_string(image, lang='eng',config=custom_config)
    text = text.lower().strip()
    text = fixeWithCustomConvert(text)
    #print('text ==> '+text)
    res = text in ['a','b','c','d','f','e','0','1','2','3','4','5','6','7','8','9']

    return res,text 



def imageToTextOld(directory_path):

    content = {}
    failedCoding = {}
    files = os.listdir(directory_path)
    print('imageToText : Parsing ',len(files),' Files')
    k=1
    for file in files:
        print('Iteration :',k,'/',len(files))
        k=k+1
        if os.path.isfile(os.path.join(directory_path, file)):
            #print(f"Reading file: {file}")
            input_image_path = directory_path+'/'+file
            im = Image.open(input_image_path)
            width, height = im.size

            #Open image
            image = cv2.imread(input_image_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                print("Error: Could not open or read the image.")
                return

            # Preprocessig
            #_, image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY)
            
            #image = cv2.resize(image, (width*2, height*2), interpolation=cv2.INTER_AREA)
            #cv2.imwrite(input_image_path, image)
            #cv2.imwrite('/tmp/tmp.png', binary_image)
            #image = cv2.imread('/tmp/tmp.png', cv2.IMREAD_GRAYSCALE)


            # Image to text
            custom_config = r'--oem 3 --psm 10 tessedit_char_whitelist=0123456789ABCDEF'
            text = pytesseract.image_to_string(image, lang='eng',config=custom_config)
            text = text.lower().strip()
            text = fixeWithCustomConvert(text)
            print('text ==> '+text)
            if text not in ['a','b','c','d','f','e','0','1','2','3','4','5','6','7','8','9']:
                #print("Non-ASCII characters found in :",file,non_ascii_chars)
                #raise Exception ("Non-ASCII characters found in :",file,non_ascii_chars,' text ==> ',text)
                if text not in failedCoding:
                    failedCoding[text]=[file]
                    print("Non-ASCII characters found in :",file,text)
                else :
                    failedCoding[text].append(file)

            #sub_image_{row}_{column}.png
            _,_,row,collumn = file.split('.')[0].split('_')
            #print(row,collumn)
            row = int(row)
            collumn = int(collumn)
            if row in content :
                content[row][collumn]=text
            else :
                content[row] = {collumn:text}
    #print(failedCoding)

    for f in failedCoding:
        print(f,':  count ==>',len(failedCoding[f]),' samlpe ==> ',failedCoding[f][0],failedCoding[f][len(failedCoding[f])-1])

    return len(failedCoding),content 

if __name__ == "__main__":
    #directory_path = sys.argv[1]

    #Split the file 
    output_folder = "output"
    os.system('rm -rf '+output_folder)
    os.system('mkdir '+output_folder)
    input_image_path = sys.argv[1]

    failedCoding,content = split_image(input_image_path, output_folder)
    
    for f in failedCoding:
        print(f,':  count ==>',len(failedCoding[f]),' samlpe ==> ',failedCoding[f][0],failedCoding[f][len(failedCoding[f])-1])

    if len(content) :
        output_image_path = os.path.basename(input_image_path)
        file_name, file_extension = os.path.splitext(output_image_path)
        fdir = os.path.dirname(input_image_path)
        output_image_path = fdir + '/' + file_name + '.hex'
        os.system('rm -rf '+output_image_path)

        for row in range(len(content)) :
            for col in range(len(content[row])):
                with open(output_image_path,'a') as f :
                    f.write(content[row][col])

            with open(output_image_path,'a') as f :#after eache new row
                f.write('\n')







