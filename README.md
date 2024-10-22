# AWS Credential Rotation

This script rotates the AWS credentials for your profile on your mac every every 7 days on Sunday at 12:00 AM.

## Installation

### Prerequisites

1. Install Python 3.10 or later.
2. Install pip3.

### Installation

1. Update the `local_profile_name` in the `rotate.py` file to the name of the profile you want to use.
2. Run the `install.sh` script.

The script will log the output to `/var/log/aws-rotation/aws-rotation.log`.


## Validation

Run the `validate.sh` script to verify if the cron job is set up correctly.

## Uninstallation

Run the `unload.sh` script.

