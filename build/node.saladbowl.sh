
#! /bin/bash
echo Session=saladbowl
tmux switch -t saladbowl
        tmux select-window -t '=node1'
tmux send-keys -t 0 "yes '' | geth init --datadir /users/Girish/FuseMnt/datadir /users/Girish/FuseMnt/ethereum/genesis.json |& tee -a /users/Girish/FuseMnt/datadir/logs.txt" Enter
tmux send-keys -t 0 "sleep 5" Enter
tmux send-keys -t 0 "tree -a /users/Girish/FuseMnt |& tee -a /users/Girish/FuseMnt/datadir/logs.txt" Enter
tmux send-keys -t 0 "ifconfig |& tee -a /users/Girish/FuseMnt/datadir/logs.txt" Enter

    tmux send-keys -t 0 "sleep 30" Enter
tmux send-keys -t 1 "geth --datadir /users/Girish/FuseMnt/datadir --networkid 16 --port 30306 --mine --miner.threads 10 --miner.etherbase  --bootnodes 'bootnode_enr' " Enter
tmux send-keys -t 0 "geth attach /users/Girish/FuseMnt/datadir/geth.ipc" Enter
            tmux select-window -t '=node2'
tmux send-keys -t 0 "yes '' | geth init --datadir /users/Girish/FuseMnt/datadir /users/Girish/FuseMnt/ethereum/genesis.json |& tee -a /users/Girish/FuseMnt/datadir/logs.txt" Enter
tmux send-keys -t 0 "sleep 5" Enter
tmux send-keys -t 0 "tree -a /users/Girish/FuseMnt |& tee -a /users/Girish/FuseMnt/datadir/logs.txt" Enter
tmux send-keys -t 0 "ifconfig |& tee -a /users/Girish/FuseMnt/datadir/logs.txt" Enter

    tmux send-keys -t 0 "sleep 30" Enter
tmux send-keys -t 1 "geth --datadir /users/Girish/FuseMnt/datadir --networkid 16 --port 30307  --bootnodes 'bootnode_enr' " Enter
tmux send-keys -t 0 "geth attach /users/Girish/FuseMnt/datadir/geth.ipc" Enter
            