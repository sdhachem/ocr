# ocr
Exfiltrating data through OCR ()

The objective of this project is to showcase the potential for data exfiltration through Optical Character Recognition (OCR) technology. The intention is to raise awareness among managers about the risks associated with recording devices and advocate for stricter access controls to critical sections.

Through this project, you can provide evidence to your management that even with a seemingly innocuous device like an iPhone, it is possible to exfiltrate sensitive data from highly secured Windows workstations, which may have stringent restrictions such as no USB access, no internet connectivity, and so on.

It structured in three directories :
1. encoding_scripts : contains two script that you have to write manually in the Target Workstation 
    1.1 encode.ps1 : encode the target File and took two manadatory parameters and two optional. Mandatory parameters are :
       1.1.1 input  : File/Directory willing to exfiltrate
       1.1.2 output : Where the encoding files will be stored
    1.2 openfiles.ps1 : Allows to open the encoded files for screen recording

2. decoding_scripts : contain three scripts
   2.1 ffmpeg.sh : split the recording into frames saved in ./00-frames 
       examples : ffmpeg.sh video.mov 10 (will create 00-frames in current directory)
   2.2 extractor.py : convert the frames into text files savd in ./00-frames/02-validText 
      example : python3 extractor.py  00-frames > /dev/null 2>&1 &
      Check logs : tail -f ./ocr.log
  2.3 decode.py : rebuild the exfiltrated document from the text extracted by OCR engine.
     It took two parameters :
       - First parameter is the text files extracted from the video
       - Second parameter is the name of the resulting file (zip file)
     example : python3 decode.py 00-frames/02-validText/ prouve.zip  
   
4. samples : 
  The directory contain a recording on which you can apply the decoding scripts and get prouve.txt.
  Submit the Token as a comment :-)



How to use it :

1. Copy the scripts encoding_scripts into the target workstation
2. run encode.ps1 PATH_TO_SECRET_FILE OUTPUT_PATH
3. Prepare and start the recording (Screen recording or any external device)
4. run openfiles.ps1 OUTPUT_PATH/files
5. Stop the recording once all files are opned
   
