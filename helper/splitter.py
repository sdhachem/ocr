from PIL import Image
import sys,os

def split_image(input_image_path, output_folder, size):

	#We have 57 collumn
	#We have 36 row

	nbOfCol =57
	nbOfRow = 36

	# Open the input image
	image = Image.open(input_image_path)

	# Get the width and height of the input image
	width, height = image.size

	# Calculate the number of rows and columns for the smaller images
	rows = height // size
	columns = width // size

	rowSize = height // nbOfRow
	collSize = width // nbOfCol
	#splitByCollumn(image,rows,columns,size,width, height)
	splitBySquare(image,rows,columns,width, height,collSize,rowSize,nbOfCol,nbOfRow)


def splitBySquare(image,rows,columns,width, height,collSize,rowSize,nbOfCol,nbOfRow):
# Loop through each row and column to split the image
    #for row in range(rows):

    startVerticalOffset = 12
    #startHorizontalOffset = 0

    #rowSize = 40
    print(rowSize)
    row = 0
    for column in range(nbOfCol):
    	for row in range(nbOfRow):
	        # Calculate the cropping box for the current sub-image
	        left = column * collSize
	        right = (column + 1) * collSize
	        upper = row * rowSize  + startVerticalOffset #Alwayse 0     
	        lower = (row + 1) * rowSize + startVerticalOffset

	        # Crop the sub-image
	        #print(left, upper, right, lower)
	        sub_image = image.crop((left, upper, right, lower))
	        #raise
	        # Save the sub-image with a unique name
	        sub_image.save(f"{output_folder}/sub_image_{row}_{column}.png")


def splitByCollumn(image,rows,columns,size,width, height):
# Loop through each row and column to split the image
    #for row in range(rows):


    row = 0
    for column in range(columns):
        # Calculate the cropping box for the current sub-image
        left = column * size
        right = (column + 1) * size
        upper = row * size   #Alwayse 0     
        lower = width

        # Crop the sub-image
        #print(left, upper, right, lower)
        sub_image = image.crop((left, upper, right, lower))
        #raise
        # Save the sub-image with a unique name
        sub_image.save(f"{output_folder}/sub_image_{row}_{column}.png")


def splitBySquareOriginal(image,rows,columns,size):
# Loop through each row and column to split the image
    for i in range(rows):
        for j in range(columns):
            # Calculate the cropping box for the current sub-image
            left = j * size
            upper = i * size
            right = (j + 1) * size
            lower = (i + 1) * size

            # Crop the sub-image
            #print(left, upper, right, lower)
            sub_image = image.crop((left, upper, right, lower))
            #raise
            # Save the sub-image with a unique name
            sub_image.save(f"{output_folder}/sub_image_{i}_{j}.png")

if __name__ == "__main__":
    input_image_path = sys.argv[1]  # Replace with the path to your input image
    os.system('rm -rf output')
    os.system('mkdir output')

    output_folder = "output"  # Replace with the folder where you want to save the sub-images
    size = 40  # Specify the size of each sub-image

    split_image(input_image_path, output_folder, size)
