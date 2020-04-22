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
    sys.exit("Pleas run this script as root!")

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
                prot = rule['protocol'].split('/')
                for i in range(len(prot)):
                    rules.append("iptables -A INPUT -p {} --dport {} ".format(prot[i], rule['port']))
            else:
                rules.append("iptables -A INPUT -p {} --dport {} ".format(rule['protocol'], rule['port']))
            while index < len(rules):
                if  'rule[\'allowedSource\']' in globals():
                    rules[index] += "-s {} -j ACCEPT".format(rule['allowedSource'])
                else:
                    rules[index] += "-j ACCEPT"
                index += 1

print("\n\n\n\n\n\nWARNING: Please check the iptables below!")
print("---------------------")
for r in rules:
    print("# {}".format(r))
print("---------------------")
print("It is possible that you loose your connections if you are connection via SSH!")
print("\nPlease notice that the following rules are temporary! \nIf you restart you Server they will be reseted. ")
print("If you want to save them, please search for the right method for your distribution.")

if query_yes_no("Add this rules to your Server?"):
    for r in rules:
        print(subprocess.Popen(r, shell=True, stdout=subprocess.PIPE).stdout.read())
else:
    sys.exit("Canceled!");
