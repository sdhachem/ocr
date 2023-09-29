 
 param (
    [string]$directoryPath
)

 
 
 
 # Get all files in the directory
$files = Get-ChildItem -Path $directoryPath -File
Start-Sleep -Seconds 10
# Display the list of files
foreach ($file in $files) {
    Write-Host "File: $($file.FullName)"
	cmd.exe /c start /max C:\Windows\notepad.exe "$($file.FullName)"
	$notepad = Get-Process | Where-Object { $_.ProcessName -eq "notepad" }
	if ($notepad) {
		$font = "Courie New"
		$fontSize = 10
		$notepad.MainWindowTitle | ForEach-Object {
			$windowHandle = (New-Object -ComObject 
"Shell.Application").Windows() | Where-Object { $_.LocationURL -eq $_.LocationName -and 
$_.LocationURL -eq "file://C:/path/to/your/textfile.txt" }
			if ($windowHandle) {
				$windowHandle.Document.Application.Selection.Font.Name = 
$font
				$windowHandle.Document.Application.Selection.Font.Size = 
$fontSize
			}
		}
	}

	Start-Sleep -Seconds 1
	
	taskkill /im "notepad.exe"
	
}
 
 
