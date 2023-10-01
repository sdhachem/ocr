 
 param (
    [string]$directoryPath,
	[string]$fontSize=10
)

 
 
 if ([string]::IsNullOrEmpty($directoryPath)) {
    Write-Host "InputFile/OutDir parameter not provided."
 }
 
 #Set NotePad default font
 # Define the font settings
$fontName = "Courier New"

write-host "Please open note pad and set Font size and style Recommanded (Courier New/10 for screen recording)"

 # Get all files in the directory
$files = Get-ChildItem -Path $directoryPath -File
# Display the list of files
for ($findex = 1; $findex -le $files.Length; $findex++) {	
	
	$file = "$directoryPath\$findex.txt"
    Write-Host "File: $file"
	#cmd.exe /c start /max C:\Windows\notepad.exe "$file"
	Start-Process -FilePath "notepad.exe" -ArgumentList $file -WindowStyle Maximized
	
	Start-Sleep -Milliseconds 1000
	
	#taskkill /im "notepad.exe"
	Stop-Process -Name "notepad" -Force
	Start-Sleep  -Milliseconds 500
	
}
 
 