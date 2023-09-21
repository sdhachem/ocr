
if [ -z $1 ]; then echo "source video is unset";exit; fi
if [ -z $2 ]; then echo "split rate is unset (20 is good)";exit; fi

echo "ffmpeg src_video fps outputdir"

dirname=`dirname $1`
fname=`basename $1 .mov`

out="$dirname/00-frames"
echo "out==$out"
mkdir $out
#exit
ffmpeg -i $1  -vf fps=$2  $out/Frame_$fname-%10d.png


#Copy video 2mn starting from 19mn
#ffmpeg -i 01-py_rsc/video/rsc.mov  -ss 00:19:00 -t 00:02:00 -c copy 01-py_rsc/video/rsc_part1.mov
