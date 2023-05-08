#! /bin/bash
yes | sudo apt update -y && sudo apt install -y software-properties-common || true
yes | sudo add-apt-repository -y ppa:ethereum/ethereum || true
yes | sudo apt-get -y update || true
yes | sudo apt-get install ethereum || true
yes | sudo apt-get install tree || true