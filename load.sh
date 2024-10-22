#!/bin/bash

# Create necessary directories
sudo mkdir -p /usr/local/aws-rotation
sudo mkdir -p /var/log/aws-rotation

# Copy scripts
sudo cp rotate.py /usr/local/aws-rotation/
sudo chmod +x /usr/local/aws-rotation/rotate.py

# Create LaunchDaemon
cat << 'EOF' | sudo tee /Library/LaunchDaemons/com.aws.credrotate.plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aws.credrotate</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/aws-rotation/rotate.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key>
        <integer>0</integer>
        <key>Hour</key>
        <integer>0</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/var/log/aws-rotation/rotate.log</string>
    <key>StandardErrorPath</key>
    <string>/var/log/aws-rotation/error.log</string>
    <key>SkipMissed</key>
    <false/>
</dict>
</plist>
EOF

# Load daemon
sudo launchctl load /Library/LaunchDaemons/com.aws.credrotate.plist