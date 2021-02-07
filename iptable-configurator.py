#!/usr/bin/env python3
import os, subprocess, sys, distutils, json
from distutils import util
import subprocess

def query_yes_no(question, default='no'):
    if default is None:
        prompt = " [y/n] "
    elif default == 'yes':
        prompt = " [Y/n] "
    elif default == 'no':
        prompt = " [y/N] "
    else:
        raise ValueError("Unknown setting '{default}' for default.")

    while True:
        try:
            resp = input(question + prompt).strip().lower()
            if default is not None and resp == '':
                return default == 'yes'
            else:
                return distutils.util.strtobool(resp)
        except ValueError:
            print("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")



if os.geteuid() != 0:
    sys.exit("Please run this script as root!")

rules = []

with open('rules-templates.conf') as json_file:
    data = json.load(json_file)

    #TODO: Static rules
    for st in data['staticRules']:
        rules.append(st)

    for rule in data['autoConfig']:
        if query_yes_no("Do you want to allow {}(:{})?".format(rule['name'], rule['port'])):
            index = len(rules);
            if rule['protocol'].find("/"):
                prot = rule['protocol'].split(',')
                for i in range(len(prot)):
                    rules.append("iptables -A INPUT -p {} --dport {} ".format(prot[i], rule['port']))
            else:
                rules.append("iptables -A INPUT -p {} --dport {} ".format(rule['protocol'], rule['port']))
            while index < len(rules):

                try:
                    interface = rule['interface']
                except (NameError, KeyError):
                    interface = None
                else:
                    rules[index] += "-i {} ".format(rule['interface'])

                try:
                    source = rule['allowedSource']
                except (NameError, KeyError):
                    rules[index] += "-j ACCEPT"
                else:
                    rules[index] += "-s {} -j ACCEPT".format(rule['allowedSource'])

                index += 1

print("\n\n\n\n\n\nWARNING: Please check the iptables below!")
print("---------------------")
for r in rules:
    print("# {}".format(r))
print("---------------------")
print("It is possible that you loose your connections if you are connected via SSH!")
print("\nPlease notice that the following rules are temporary!\nWhen your server restarts, they will be reset.")
print("If you want these rules to be persistent, please search for the right method for your distribution (e.g. iptables-save/iptables-restore).")

if query_yes_no("Add these rules to your server?"):
    for r in rules:
        subprocess.Popen(r, shell=True, stdout=subprocess.PIPE).communicate()[0];
        print("Added")
else:
    sys.exit("Canceled!");
