


write-host "Start opening file"
$dir=$args[0]
$start=$args[1]
$end=$args[2]


$missing = @(169,381,1058,1581,1583,1686,1692,1692,1702,1703,1704,1722,1747,1773,1778,1795,1820,1828,1845,1859,1864,1961,1976,2021,2558,2718,2881,3146,3148)
write-host "start at $start to $end"

for($i=$start; $i -le $end ; $i=$i+1){
#foreach ($i in $missing){
    $fn = "$dir/$i.txt"
    write-host $fn
    taskkill /im "notepad++.exe"
    start-sleep 1    
    start-process -FilePath "C:\Program Files\Notepad++\notepad++.exe" -ArgumentList $fn
    start-sleep 2

    
}