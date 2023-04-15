#! /bin/bash

sudo apt-get install python3-pip
pip3 install paramiko

export PROJ_PARENT="$(dirname "$(pwd)")"
export PROJ_HOME=$(pwd)

# install oh-my-zsh
yes | sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# install fzf
yes | git clone https://github.com/unixorn/fzf-zsh-plugin.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/fzf-zsh-plugin

yes | sudo apt-get -y update

# update tmux
yes | sudo apt-get -y install tmux
yes | sudo apt-get -y install vim

# vim plug
yes | curl -fLo ~/.vim/autoload/plug.vim --create-dirs \
    https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
