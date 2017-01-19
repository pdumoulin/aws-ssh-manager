
# aws-ssh-manager
Script that manages connection profiles for multiple AWS accounts.

## Setup

1. Install python library [requirements](https://github.com/pdumoulin/aws-ssh-manager/blob/master/requirements.txt) (using virtualenv if desired)

1. Create aws access keys via *[IAM Management Console](https://console.aws.amazon.com/iam/home#/home) > Users > Your User > Security Credentials* for each account

1. Paste keys to file at ~/.aws/credentials 

  Example Credentials File:
  ```
  [dev]
  aws_access_key_id=devkeyhere
  aws_secret_access_key=devsecrethere

  [prod]
  aws_access_key_id=prodkeyhere
  aws_secret_access_key=prodsecrethere
  ```

1. **Never ever** commit the credentials file to a repository. It must be kept it private. If the key is exposed it needs to be deactivated and replaced in the [IAM Management Console](https://console.aws.amazon.com/iam/home#/home).

## Configuration

1. Set **SSH_CONFIG** environment variable (default is config.json)

1. Set **SSH_USER** environment variable (default is raw input step)

1. Create JSON Config file containing:
  1. List of environments whose names correspond to aws credentials
    1. Region (default is us-east-1)
    1. List of regular expressions to search for hostnames (default is empty array)
    1. List of elbs to query for backend hosts (default is empty array)

## Run
Sample .bashrc
```
export SSH_USER='myusername'
export SSH_CONFIG='/Users/me/aws-ssh-manager/conf/config.json'
alias s='python ~/aws-ssh-manager/manager.py'
```

Sample Output:
```
[15:52:46] me@mylaptop ~/aws-ssh-manager $ python manager.py
Available environments:
stg
prod
dev
[15:52:48] me@mylaptop ~/aws-ssh-manager $ python manager.py prod

1: worker-034514bd8d3a9fb73.example.com
2: worker-1216a91d.example.com
3: worker-70f3ade8.example.com
4: cron-01.example.com

ELB: my-app-elb
5: api-01.example.com
6: api-02.example.com
7: api-03.example.com

Select host to SSH into:
```

## References
* [Example config](https://github.com/pdumoulin/aws-ssh-manager/blob/master/conf/jwplayer.json)
* [Read the docs guide on credential setup](http://boto3.readthedocs.io/en/latest/guide/configuration.html#shared-credentials-file)
