#!/bin/bash
#
# Author: Yang,Ying-chao <yangyingchao@g-data.com>, 2017-09-18
#
top=`dir`

cd ~
ln -sf ${top}/.fvwm ~/.fvwm

cd ~/.config

ln -sf ${top}/config/* .
