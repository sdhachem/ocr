
param (
    [string]$filePath,
    [string]$directoryPath,
    [int]$Screen_length,
    [int]$screen_width,
    [int]$round
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


#TODO remaining file
function convertSourceFile ([string]$filePath, [string]$directoryPath, [string]$round) {
    
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
    $space_kw=' '
    $substringSize = $Screen_length*$screen_width
    $totalBinSize = 8*$binaryDataLen
    $nbOfFiles = [math]::DivRem($totalBinSize, $substringSize, [ref]0) #[int]($totalBinSize/$substringSize)
    if($totalBinSize % $substringSize -ne 0){$nbOfFiles += 1}
    write-host "nbOfFiles  = $nbOfFiles substringSize=$substringSize totalBinSize=$totalBinSize"
    $fileNb = [System.Convert]::ToString($nbOfFiles,2).PadLeft(20, '0')
    $findex=1
    $Screen_lengthStr = [System.Convert]::ToString($Screen_length,2).PadLeft(20, '0')
    $screen_widthStr = [System.Convert]::ToString($screen_width,2).PadLeft(20, '0')
    $cdate = Get-Date
    Write-host "$cdate => Start generating Files line leng = $Screen_length filePath=$filePath "
    $k=1
    $lineLen = $Screen_length
    foreach ($byte in $binaryData) {
        
        $binaryString += [convert]::ToString($byte, 2).PadLeft(8, '0')
        $currentSubstrLen = $binaryString.length
        #if ((( $currentSubstrLen % $substringSize) -eq 0) -or ($k -eq $binaryDataLen)) {
        if (( $currentSubstrLen -ge $substringSize ) -or ($k -eq $binaryDataLen)) {
            
            
            $fileIndex = [System.Convert]::ToString($findex,2).PadLeft(20, '0')     
            $magicHeader= $fileIndex + $fileNb + $Screen_lengthStr + $screen_widthStr
            $crc =[System.Text.Encoding]::ASCII.GetBytes($binaryString) | Get-CRC32
            $crcbin = [System.Convert]::ToString($crc,2).PadLeft(32, '0')
            
            $substringWithNewLines=$space_kw
            for ($j =0; $j -lt $currentSubstrLen; $j++) {           
                if($lineLen+$j -gt $currentSubstrLen){$lineLen = $currentSubstrLen-$j}
                if($j  % $Screen_length -eq 0){$substringWithNewLines = $substringWithNewLines  +  $binaryString.substring($j,$lineLen) + $newLine + $space_kw  }
            }
        
            $content = $newLine + $space_kw + $crcbin+ $magicHeader  + $newLine + $substringWithNewLines
            $outFilePath = "$directoryPath\files\$findex.txt"       
            Set-Content -Path $outFilePath -Value $content
            $substringWithNewLinesLen = $substringWithNewLines.length
            $cdate = Get-Date
            Write-host "$cdate => End Write file $findex/$nbOfFiles (round=$round) - substringWithNewLinesLen=$substringWithNewLinesLen currentSubstrLen=$currentSubstrLen" 
            $binaryString=''
            $findex += 1
            
        }   
        $k +=1
    }

    
}

if ([string]::IsNullOrEmpty($filePath)) {
    Write-Host "InputFile parameter not provided."
    exit 0
}

Remove-Item -Path $directoryPath -Recurse  -ErrorAction SilentlyContinue
New-Item -Path "$directoryPath\files" -ItemType Directory -Force 

#write-host "Start encoding the file $filePath (round=$round) "
$currentTarget = $filePath 
$previousTargetSize=0
$binaryFilesDir= "$directoryPath\files"
for ($i = 1; $i -le $round; $i++) {
    write-host "Start encoding the file $currentTarget (round=$i/$round) "
    Compress-Archive -Path $currentTarget -DestinationPath "$directoryPath\00-$i"
    #remove file in Files
    Get-ChildItem -Path $binaryFilesDir -File | ForEach-Object {Remove-Item $_.FullName}
    $zippedTarget = "$directoryPath\00-$i.zip"
    $file = Get-Item $zippedTarget
    $currentTargetSize = $file.Length
    if (($i -gt 1) -and ($currentTargetSize -ge $previousTargetSize )){
        write-host "Stop at round $round because zip > previous file"
        break
    }
    
    convertSourceFile -filePath $zippedTarget -directoryPath $directoryPath -round "$i/$round"
    $currentTarget = $binaryFilesDir
    $previousTargetSize=$currentTargetSize
    #convertSourceFile -filePath $filePath -directoryPath $directoryPath
}

$cdate = Get-Date
Write-host "$cdate => End generating Files"