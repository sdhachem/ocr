import sys
import binascii
import os
import pytesseract
from PIL import Image
import pytesseract 
import cv2
import numpy as np


# Replace 'your_directory_path' with the path to the directory you want to read

def findAllRedPixel(input_image_path):
    # Load the image
    image = cv2.imread(input_image_path)

    # Define the color range for red in BGR format (OpenCV uses BGR)
    lower_red = (0, 0, 100)
    upper_red = (100, 100, 255)

    # Create a mask to identify red pixels in the image
    mask = cv2.inRange(image, lower_red, upper_red)

    # Find the coordinates of red pixels in the image
    red_pixel_coordinates = cv2.findNonZero(mask)
    redPixels = []
    if red_pixel_coordinates is not None:
        print("Red pixels found in the image.")
        for pixel in red_pixel_coordinates:
            x, y = pixel[0]
            redPixels.append(x)
            #print(f"Red pixel found at ({x}, {y})")
    else:
        print("No red pixels found in the image.")

    return redPixels


def findImageSparator(input_image_path,nbOfSeparator):

    image = Image.open(input_image_path)
    sepPositions = []

    # Open the image
    width, height = image.size
    # Define the threshold for red color detection
    red_threshold = 100

    # Create a blank white image with the same size as the original image
    output_image = Image.new("RGB", image.size, (255, 255, 255))

    # Iterate through each pixel and apply the filter

    

    redPixels = findAllRedPixel(input_image_path)


    redPixels = list(set(redPixels))    
    #print('redPixels => ',redPixels)
    print('redPixels => ',len(redPixels))
    occurences = len(redPixels)//nbOfSeparator
    for sepIndex in range(nbOfSeparator):
        #print(sepIndex,' => ',redPixels[sepIndex*occurences])
        sepPositions.append(redPixels[sepIndex*occurences])

    sepPositions = sorted(sepPositions)
    print('sepPositions => ',sepPositions)
    print('len  sepPositions => ',len(sepPositions))

    
    return sepPositions




def extractTextFromImage(input_image_path, output_folder):

    nbOfCol =40
    nbOfRow =18  
    image = Image.open(input_image_path)
    width, height = image.size

    #Loop through each row and column to split the image
    #for row in range(rows):

    sepPositions = findImageSparator(input_image_path,39)
    content = {}
    failedCoding = {}

    startVerticallOffset = 20 # Increase if there big offset before first row : findtune if you increase by one the top of first car will be lost
    rowSize = 23 
    
    # Separator size of the left
    sepSizeLeft =30
    # Separator size of the Right
    sepSizeRight = 25

    #nbOfRow = 1 # one row
    #sepPositions = sepPositions[:2]
    #nbOfCol=1
    #for column in range(nbOfCol):
    
    iteration = 1
    for row in range(nbOfRow):
        colIndex = 0
        previousUpper = startVerticallOffset + row * rowSize 
        # Calculate the cropping box for the current sub-image
        right=-sepSizeRight
        left=0
        for sepPosition in sepPositions[1:]:

            #if colIndex > -1 :
            #print('Iteration = ',iteration,'/',nbOfRow*len(sepPositions),'sepPosition ',sepPosition)
            iteration = iteration +1

            left = right + sepSizeRight
            right = sepPosition - sepSizeLeft
            previousSepator = sepPosition

            #print('Coll ',colIndex,':left',left,'=>right',right)
            upper = previousUpper #row * rowSize + startVerticallOffset   #Alwayse 0     
            lower = previousUpper + rowSize 
           

            # Crop the sub-image
            #print(left, upper, right, lower)
            sub_image = image.crop((left, upper, right, lower))
            res,text = imageToText(sub_image)
            
            if not res:#res and text=='0':
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

    # Image to text
    custom_config = r'--oem 3 --psm 10 tessedit_char_whitelist=0123456789ABCDEF'
    text = pytesseract.image_to_string(image, lang='eng',config=custom_config)
    text = text.lower().strip()
    text = fixeWithCustomConvert(text)
    #print('text ==> '+text)
    res = text in ['a','b','c','d','f','e','0','1','2','3','4','5','6','7','8','9']

    return res,text 


if __name__ == "__main__":
    #directory_path = sys.argv[1]

    #Split the file 
    output_folder = "output"
    os.system('rm -rf '+output_folder)
    os.system('mkdir '+output_folder)
    input_image_path = sys.argv[1]

    

    failedCoding,content = extractTextFromImage(input_image_path, output_folder)
    
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







