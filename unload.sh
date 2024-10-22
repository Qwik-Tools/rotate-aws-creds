sudo launchctl unload /Library/LaunchDaemons/com.aws.credrotate.plist
sudo rm -rf /Library/LaunchDaemons/com.aws.credrotate.plist
sudo rm -rf /usr/local/aws-rotation
sudo rm -rf /var/log/aws-rotation

echo "AWS Credential Rotation Uninstalled"