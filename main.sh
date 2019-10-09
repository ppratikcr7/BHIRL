export PATH="/home/parth/anaconda3/bin:$PATH"

sudo apt install mercurial libfreetype6-dev libsdl-dev libsdl-image1.2-dev libsdl-ttf2.0-dev libsmpeg-dev libportmidi-dev libavformat-dev libsdl-mixer1.2-dev libswscale-dev libjpeg-dev

conda env create -f env.yml

source activate BHIRL3

cd pymunk-pymunk-4.0.0

python3 setup.py install

cd ..

python3  main.py
