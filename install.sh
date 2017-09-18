#!/bin/bash
#
# Author: Yang,Ying-chao <yangyingchao@g-data.com>, 2017-09-18
#

TOP=$PWD
DRY_RUN=1


die() {
    set +x
    local IFS=$' \t\n'
    set +e

    echo -e "$@" | while read -r ; do
        echo " $BAD*$NORMAL $RC_INDENTATION$REPLY" >&2
    done
    exit 1
}

my_exec()
{
    if [ -z $DRY_RUN ]; then
        eval "$*"
    else
        echo "EXEC: $*"
    fi
}


my_link()
{
    local src=$1
    local dst=$2

    [ -e $dst ] && my_exec rm -rf $dst || die "Deleting failed.."
    my_exec  ln -sf $src $dst || die "linking failed.."
}

my_link ${TOP}/.fvwm ~/.fvwm
my_link ${TOP}/.gtkrc-2.0.mine ~/.gtkrc-2.0.mine

for item in ${TOP}/config/*; do
    my_link $item ~/.config/`basename $item`
done

