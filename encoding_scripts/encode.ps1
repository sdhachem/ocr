
param (
    [string]$filePath,
	[string]$directoryPath,
	[int]$Screen_length=160,#210 big screen
	[int]$screen_width=50,
	[int]$round = 10
)


#https://communary.net/2017/02/12/calculate-crc32-in-powershell/
function Get-CRC32 {
    [CmdletBinding()]
    param (
        # Array of Bytes to use for CRC calculation
        [Parameter(Position = 0, ValueFromPipeline = $true)]
        [ValidateNotNullOrEmpty()]
        [byte[]]$InputObject
    )

    Begin {

        function New-CrcTable {
            [uint32]$c = $null
            $crcTable = New-Object 'System.Uint32[]' 256

            for ($n = 0; $n -lt 256; $n++) {
                $c = [uint32]$n
                for ($k = 0; $k -lt 8; $k++) {
                    if ($c -band 1) {
                        $c = (0xEDB88320 -bxor ($c -shr 1))
                    }
                    else {
                        $c = ($c -shr 1)
                    }
                }
                $crcTable[$n] = $c
            }

            Write-Output $crcTable
        }

        function Update-Crc ([uint32]$crc, [byte[]]$buffer, [int]$length) {
            [uint32]$c = $crc

            if (-not($script:crcTable)) {
                $script:crcTable = New-CrcTable
            }

            for ($n = 0; $n -lt $length; $n++) {
                $c = ($script:crcTable[($c -bxor $buffer[$n]) -band 0xFF]) -bxor ($c -shr 8)
            }

            Write-output $c
        }

        $dataArray = @()
    }

    Process {
        foreach ($item  in $InputObject) {
            $dataArray += $item
        }
    }

    End {
        $inputLength = $dataArray.Length
        Write-Output ((Update-Crc -crc 0xffffffffL -buffer $dataArray -length $inputLength) -bxor 0xffffffffL)
    }
}



function convertSourceFile ([string]$filePath, [string]$directoryPath, [string]$round) {
	
	Write-Host "Start Reading the file $filePath "
	try {
		$binaryData = Get-Content -Path $filePath -Encoding Byte -ReadCount 0
	}
	catch {
		Write-Host "An error occurred reading the file $filePath : $_"
		exit 0
	}

	$binaryDataLen =  $binaryData.Length
	write-host "binaryDataLende=$binaryDataLen"
	#$binaryString = [convert]::ToString($binaryData, 2).PadLeft(8, '0')


	$newLine = "`n"
	$space_kw='	'
	$substringSize =  $Screen_length*$screen_width
	$totalBinSize = 8*$binaryDataLen
	$nbOfFiles = [math]::DivRem($totalBinSize, $substringSize, [ref]0) #[int]($totalBinSize/$substringSize)
	if($totalBinSize % $substringSize -ne 0){$nbOfFiles += 1}
	write-host "nbOfFiles  = $nbOfFiles substringSize=$substringSize totalBinSize=$totalBinSize"
	$fileNb = [System.Convert]::ToString($nbOfFiles,2).PadLeft(20, '0')
	$findex=1
	$Screen_lengthStr = [System.Convert]::ToString($Screen_length,2).PadLeft(20, '0')
	$screen_widthStr = [System.Convert]::ToString($screen_width,2).PadLeft(20, '0')
	$cdate = Get-Date
	Write-host "$cdate => Start generating Files line leng = $Screen_length filePath=$filePath (It will take time)"
	$k=1
	
	foreach ($byte in $binaryData) {
		
		$binaryString += [convert]::ToString($byte, 2).PadLeft(8, '0')
		$currentSubstrLen = $binaryString.length
		if (( $currentSubstrLen -ge $substringSize ) -or ($k -eq $binaryDataLen)) {
			
			$lineLen = $Screen_length			
			$fileIndex = [System.Convert]::ToString($findex,2).PadLeft(20, '0')					
			$crc =[System.Text.Encoding]::ASCII.GetBytes($binaryString) | Get-CRC32
			$crcbin = [System.Convert]::ToString($crc,2).PadLeft(32, '0')
			$magicHeader= $crcbin + $fileIndex + $fileNb + $Screen_lengthStr + $screen_widthStr
			
			
			$substringWithNewLines=$space_kw
			$binaryString =  $magicHeader + $binaryString
			$currentSubstrLen = $binaryString.length
			for ($j =0; $j -lt $currentSubstrLen; $j++) {			
				if($lineLen+$j -gt $currentSubstrLen){$lineLen = $currentSubstrLen-$j}
				if($j  % $Screen_length -eq 0){$substringWithNewLines = $substringWithNewLines  +  $binaryString.substring($j,$lineLen) + $newLine + $space_kw  }
			}
			$substringWithNewLines=$newLine + 	$substringWithNewLines
			
			$outFilePath = "$directoryPath\files\$findex.txt"		
			Set-Content -Path $outFilePath -Value $substringWithNewLines
			$substringWithNewLinesLen = $substringWithNewLines.length
			$cdate = Get-Date
			#if($k % 100 -eq 0){
				Write-host "$cdate => End Write file $findex/$nbOfFiles (round=$round) - substringWithNewLinesLen=$substringWithNewLinesLen currentSubstrLen=$currentSubstrLen"	
			#}
			$binaryString=''
			$findex += 1
			
		}	
		$k +=1
	}

	
}

if ([string]::IsNullOrEmpty($filePath) -or [string]::IsNullOrEmpty($directoryPath)) {
    Write-Host "InputFile/OutDir parameter not provided."
	exit 0
}

$start_proc_datetime = Get-Date

Remove-Item -Path $directoryPath -Recurse  -ErrorAction SilentlyContinue
New-Item -Path "$directoryPath\files" -ItemType Directory -Force 

#write-host "Start encoding the file $filePath (round=$round) "
$currentTarget = $filePath 
$previousTargetSize=0
$binaryFilesDir= "$directoryPath\files"
for ($i = 1; $i -le $round; $i++) {
	write-host "Start encoding the file $currentTarget (round=$i/$round) "
	Compress-Archive -Path $currentTarget -DestinationPath "$directoryPath\00-$i"
	$currentTarget = "$directoryPath\00-$i.zip"
	$file = Get-Item $currentTarget
	$currentTargetSize = $file.Length
	if (($i -gt 1) -and ($currentTargetSize -ge $previousTargetSize )){
		write-host "Stop at round $i because $currentTargetSize (current) > $previousTargetSize(previous) "
		break
	}
	#remove file in Files
	Get-ChildItem -Path $binaryFilesDir -File | ForEach-Object {Remove-Item $_.FullName}	
	convertSourceFile -filePath $currentTarget -directoryPath $directoryPath -round "$i/$round"
	$currentTarget = $binaryFilesDir
	$previousTargetSize=$currentTargetSize
	
	#$currentTarget = "$directoryPath\00-$i.zip"
	
	#convertSourceFile -filePath $filePath -directoryPath $directoryPath
}

$cdate = Get-Date
Write-host "$cdate => End generating Files"
$end_proc_datetime = Get-Date


$diff= New-TimeSpan -Start $start_proc_datetime -End $end_proc_datetime
Write-Output "Total Processing is: $diff"
Write-Output "use openfiles.ps1 to open files in : $binaryFilesDir"
