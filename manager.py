
import os
import sys
import subprocess
import json
import boto3

def main():

    # load up the config
    config_filename = os.environ.get('SSH_CONFIG', 'config.json')
    with open(config_filename) as config_file:
        config = json.load(config_file)
        environments = config['environments']

    # load in simple params
    if len(sys.argv) < 2:
        print "Available environments: "
        for key in environments:
            print key
        exit()
    else:
        profile = sys.argv[1]

    # validate environment
    if profile not in environments:
        print "Environment '%s' not found!" % profile
        exit()

    # read in config data
    hosts = environments[profile].get('hosts', [])
    elbs = environments[profile].get('elbs', [])
    region = environments[profile].get('region', 'us-east-1')

    # go through config and show hostnames (expect ~/.aws/credentials)
    # http://boto3.readthedocs.io/en/latest/guide/configuration.html#shared-credentials-file
    fetcher = Fetcher(profile, region)

    # get all hostanmes into an ordered list
    hostnames = []
    hostnames = hostnames + fetcher.get_instances(hosts)
    hostnames.sort()

    elb_hostnames = []
    elb_hostnames = fetcher.get_elb_backend_hosts(elbs)
    elb_hostnames = sorted(elb_hostnames, key=lambda k: k['name'])

    options = []
    index = 1
    def add_option(hostname):
        index = len(options) + 1
        print "%s: %s" % (index, hostname)
        options.append(hostname)

    # display available hostnames with no elb
    print ""
    for hostname in hostnames:
        add_option(hostname)
    print ""

    # display available hostnames under elbs and elb name
    for elb in elb_hostnames:
        print "ELB: %s" % elb['name']
        hosts = elb['hosts']
        hosts.sort()
        for hostname in hosts:
            add_option(hostname)
        print ""

    # determine the SSH user to use
    ssh_user = None
    if 'SSH_USER' in os.environ:
        ssh_user = os.environ['SSH_USER']
    else:
        ssh_user = raw_input("SSH User: ")

    # make a selection and SSH into it
    host_index = raw_input("Select host to SSH into: ")
    try:
        selected_host = options[int(host_index) - 1]
    except:
        print "FATAL ERROR: Could not find host at index %s!" % host_index
        exit()
    subprocess.call(["ssh", "-v", "%s@%s" % (ssh_user, selected_host)])

class Fetcher(object):

    def __init__(self, profile, region):
        session = boto3.Session(region_name=region, profile_name=profile)
        self.elb = session.client('elb')
        self.ec2 = session.client('ec2')

    # extract tag values from list of reservation objects
    def _get_tag_values(self, reservations, name):
        values = []
        for reservation in reservations:
            for instance in reservation['Instances']:
                for tag in instance['Tags']:
                    if tag['Key'] == name:
                        values.append(tag['Value'])
        return values

    # get all instances with name tags matching
    def get_instances(self, names):
        if len(names) == 0:
            return []
        result = self.ec2.describe_instances(Filters=[
            { 'Name' : 'tag-value' , 'Values' : names },
            { 'Name' : 'tag-key' , 'Values' : ['Name'] }
        ])
        return self._get_tag_values(result['Reservations'], 'Name')

    # get all hostnames of instances behind an elb
    def get_elb_backend_hosts(self, elb_names):
        if len(elb_names) == 0:
            return []
        elbs = []
        result = self.elb.describe_load_balancers(LoadBalancerNames=elb_names)
        for load_balancer in result['LoadBalancerDescriptions']:
            elb = {
                'name'  : load_balancer['LoadBalancerName'],
                'hosts' : []
            }
            instance_ids = [a['InstanceId'] for a in load_balancer['Instances']]
            if len(instance_ids) > 0:
                result = self.ec2.describe_instances(InstanceIds=instance_ids)
                elb['hosts'].extend(self._get_tag_values(result['Reservations'], 'Name'))
            elbs.append(elb)
        return elbs

if __name__ == '__main__':
    main()
