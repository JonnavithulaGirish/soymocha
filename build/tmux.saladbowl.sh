#! /bin/bash
echo Session=saladbowl
tmux kill-session -t saladbowl
tmux new -d -s saladbowl
tmux new-window -d -t '=saladbowl' -n main
        
tmux new-window -d -t saladbowl -n node0
tmux select-window -t '=node0'
tmux split-window -h
tmux send-keys -t 0 "ssh -oStrictHostKeyChecking=no -p 22 Girish@c220g5-110502.wisc.cloudlab.us" Enter
tmux send-keys -t 1 "ssh -oStrictHostKeyChecking=no -p 22 Girish@c220g5-110502.wisc.cloudlab.us" Enter
    
tmux new-window -d -t saladbowl -n node1
tmux select-window -t '=node1'
tmux split-window -h
tmux send-keys -t 0 "ssh -oStrictHostKeyChecking=no -p 22 Girish@c220g5-110531.wisc.cloudlab.us" Enter
tmux send-keys -t 1 "ssh -oStrictHostKeyChecking=no -p 22 Girish@c220g5-110531.wisc.cloudlab.us" Enter
    
tmux new-window -d -t saladbowl -n node2
tmux select-window -t '=node2'
tmux split-window -h
tmux send-keys -t 0 "ssh -oStrictHostKeyChecking=no -p 22 Girish@c220g5-110501.wisc.cloudlab.us" Enter
tmux send-keys -t 1 "ssh -oStrictHostKeyChecking=no -p 22 Girish@c220g5-110501.wisc.cloudlab.us" Enter
    
tmux select-window -t '=main'
        