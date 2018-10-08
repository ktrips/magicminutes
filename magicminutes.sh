#!/bin/bash --rcfile

source /etc/bash.bashrc
source ~/.bashrc

cat /etc/aiyprojects.info

#echo "Dev terminal is ready! See the demos in 'src/examples' to get started."
#echo "Note: the MagPi Essentials are not up-to-date. See https://goo.gl/8hEcfo"

cd ~/mic_array

python kws_doa.py --model blk

cd ~/AIY-projects-python

echo "AIY terminal is on. Push to start for Magic Minutes"

src/examples/voice/cloudspeech_demo.py --mail kenichi.yoshida@blackrock.com

echo "Magic Minutes for blackrock.com"
