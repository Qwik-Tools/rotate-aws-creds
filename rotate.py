import boto3
import configparser
import os

class AWSCredentialManager:
    def __init__(self, aws_username=None, local_profile_name=None):
        """
        Initializes the class with AWS username and local profile name.
        If no local profile is provided, it defaults to the active profile.
        """
        self.aws_username = aws_username
        self.local_profile_name = local_profile_name
        self.session = boto3.Session(profile_name=local_profile_name)
        self.iam_client = self.session.client('iam')
        self.new_access_key_id = None  # This will store the new access key ID

    def get_current_user_identity(self):
        """Fetches the identity of the currently authenticated user."""
        sts_client = self.session.client('sts')
        identity = sts_client.get_caller_identity()
        account_id = identity['Account']
        user_arn = identity['Arn']
        print(f"Current user ARN: {user_arn} in account {account_id}")

        # Parse the username from the ARN if aws_username is not set
        if not self.aws_username:
            # Extract the username if ARN is in format arn:aws:iam::account-id:user/username
            self.aws_username = user_arn.split("/")[-1]
            print(f"Inferred AWS username from ARN: {self.aws_username}")

        return self.aws_username

    def create_new_credentials(self):
        """Creates new access credentials for the specified or current IAM user."""
        response = self.iam_client.create_access_key(UserName=self.aws_username)
        access_key = response['AccessKey']['AccessKeyId']
        secret_key = response['AccessKey']['SecretAccessKey']
        
        # Store the newly created access key ID
        self.new_access_key_id = access_key
        print(f"New access key created for {self.aws_username}")

        return access_key, secret_key

    def update_local_credentials_file(self, access_key, secret_key):
        """Updates the local ~/.aws/credentials file with new credentials."""
        credentials_path = os.path.expanduser('~/.aws/credentials')
        config = configparser.ConfigParser()
        
        # Read the current credentials file
        config.read(credentials_path)
        
        # Use the local profile name to update the credentials
        if not self.local_profile_name:
            self.local_profile_name = self.aws_username  # Default to AWS username if no local profile is provided

        # Update the profile with the new credentials
        config[self.local_profile_name] = {
            'aws_access_key_id': access_key,
            'aws_secret_access_key': secret_key
        }

        # Write the changes back to the credentials file
        with open(credentials_path, 'w') as configfile:
            config.write(configfile)
        
        print(f"Credentials file updated for local profile {self.local_profile_name}")

    def delete_old_credentials(self):
        """Deletes old access keys from AWS and removes them from the local file, keeping the new key."""
        # Get current access keys for the user
        access_keys = self.iam_client.list_access_keys(UserName=self.aws_username)['AccessKeyMetadata']
        
        if not access_keys:
            print(f"No access keys found for {self.aws_username}")
            return
        
        # Delete old access keys (but not the newly created one)
        for key in access_keys:
            if key['AccessKeyId'] != self.new_access_key_id:
                self.iam_client.delete_access_key(UserName=self.aws_username, AccessKeyId=key['AccessKeyId'])
                print(f"Deleted old access key: {key['AccessKeyId']}")
            else:
                print(f"Skipping new access key: {key['AccessKeyId']}")

        # Update the local credentials file
        credentials_path = os.path.expanduser('~/.aws/credentials')
        config = configparser.ConfigParser()
        
        # Read the current credentials file
        config.read(credentials_path)
        
        # Remove the old profile entry, but keep the newly updated credentials
        if self.local_profile_name in config:
            if config[self.local_profile_name]['aws_access_key_id'] != self.new_access_key_id:
                config.remove_section(self.local_profile_name)

                # Write the updated credentials file back
                with open(credentials_path, 'w') as configfile:
                    config.write(configfile)

                print(f"Credentials file updated, removed old credentials for local profile {self.local_profile_name}")
            else:
                print(f"Skipping removal of new credentials for profile {self.local_profile_name}")
        else:
            print(f"No credentials found in the local file for profile {self.local_profile_name}")

    def manage_credentials(self):
        """Manages the entire flow: fetch user, create new creds, update file, delete old creds."""
        # Step 1: Get current user identity if aws_username is not explicitly set
        self.get_current_user_identity()

        # Step 2: Create new credentials
        new_access_key, new_secret_key = self.create_new_credentials()

        # Step 3: Update credentials file with the new keys
        self.update_local_credentials_file(new_access_key, new_secret_key)

        # Step 4: Delete old credentials on AWS and the local file (except the new one)
        self.delete_old_credentials()

# Example usage
if __name__ == "__main__":
    # Example: local profile name is "dev-profile", but AWS IAM user is "dev-user"
    manager = AWSCredentialManager(local_profile_name="admin")
    manager.manage_credentials()
