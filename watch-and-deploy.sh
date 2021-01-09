#!/usr/bin/env bash

ln -sf $(pwd) ~/.local/share/ulauncher/extensions/

# restart ulauncher
pkill ulauncher
ulauncher --no-extensions --dev -v > /tmp/ulauncher.log 2>&1 &

sleep 2

# redeploy app when files change
export VERBOSE=1 
export ULAUNCHER_WS_API=ws://127.0.0.1:5054/ulauncher-toggl 
export PYTHONPATH=/usr/lib/python3/dist-packages 

startExtension() {
    /usr/bin/python3 $HOME/.local/share/ulauncher/extensions/ulauncher-toggl/main.py >> /tmp/ulauncher-extension.log 2>&1 &
    pid=$(echo $!)
}

startExtension

echo "Waiting for file changes ..."
while inotifywait -qqre modify "$(pwd)/"; do
    echo "Files have changed..."
    echo "Killing extension process: $pid"
    kill $pid
    startExtension
    echo "Restarted extension. New PID: $pid"
done
