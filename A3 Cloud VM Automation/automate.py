# Tyler Ykema
# 1062564
# 10/11/2021
# CIS*4010 A3

import configparser
import os
import re
import json
from azure.identity import AzureCliCredential
import getpass
from azure.cli.core import get_default_cli
import subprocess
from datetime import datetime

#check is user is logged, if not run az logins

def get_password():
    password = ''
    while(True):
        password = input("Enter an admin password: ")
        contains_lower = False
        contains_upper = False
        contains_digit = False
        contains_spec = False

        for c in password:
            if c.islower():
                contains_lower = True
            elif c.isupper():
                contains_upper = True
            elif c.isdigit():
                contains_digit = True
            elif not c.isalnum():
                contains_spec = True
        
        three_of_four = int(contains_lower) + int(contains_upper) + int(contains_digit) + int(contains_spec)
        print(three_of_four)
        print(password)
                
        if((len(password) >= 12 and len(password) <= 123) and three_of_four >= 3):
            break
        else:
            print("The admin password for Windows servers must be between 12 and 123 characters in length and must have the 3 of the following: 1 lower case character, 1 upper case character, 1 number and 1 special character")
    return password

def is_valid_vm_list(vm_list, platform):
    vm_number = 0
    for i in vm_list:
        temp = re.compile("([a-zA-Z]+)([0-9]+)")
        res = temp.match(i).groups()

        old_vm_num = vm_number
        vm_number = int(res[1])

        #check if the the different vm's in the file are validly named/numbered
        if 0 > vm_number < 10 or vm_number - old_vm_num != 1:
            print("Invalid VM, please check format")
            return False
    return True

def cli_output_to_dict(out):
    out = str(out).replace("b'", "")
    out = str(out).replace("\\r", "")
    out = str(out).replace("\\n", "")
    out = str(out).replace("'", "")
    out = str(out).replace(" ", "")
    return json.loads(out)

def cli_output_to_string(out):
    out = str(out).replace("b'", "")
    out = str(out).replace("\\r", " ")
    out = str(out).replace("\\n", "\n")
    out = str(out).replace("   ", " ")
    out = str(out).replace("  ", " ")
    out = str(out).replace("'", "")
    return out

def rename_conf_file(filename):
    time = datetime.now()
    date_string = time.strftime("%Y-%m-%d-%H-%M-%S")
    new_filename = (filename.split('.'))[0] + "_" + date_string + "." + (filename.split('.'))[1]
    os.rename(filename, new_filename)
    return

def create_azure_vm(vm_list, filename):
    if (not is_valid_vm_list(vm_list, 'azure')):
        print("Not a valid az conf file")
        return -1
    
    for i in vm_list:
        if not 'name' in vm_list[i].keys():
            print("Error: there is no name for VM: " + i)
            break
        if not 'resource-group' in vm_list[i].keys():
            print("Error: no-resource group for VM: " + i)
            break
        if not 'image' in vm_list[i].keys():
            print("Error: no image for VM: " + i)
            break
        if not 'location' in vm_list[i].keys():
            print("Error: no location for VM: " + i)
            break
        if not 'admin-username' in vm_list[i].keys():
            print("Error: no admin-username for VM: " + i)
            break

        name = vm_list[i]['name']
        resource_group_name = vm_list[i]['resource-group']
        location = vm_list[i]['location']
        image = vm_list[i]['image']
        public_ip = 'Standard'
        os_name = vm_list[i]['os']
        purpose = vm_list[i]['purpose']
        team = vm_list[i]['purpose']

        #create resource group to house VM
        resource_group = ['az', 'group', 'create', "--name", resource_group_name, "--location", location]
        print("Creating resource group: '" + ' '.join(resource_group) + "'")

        resource_group_result = subprocess.Popen(resource_group, shell = True, stdout = subprocess.PIPE)

        #provision VM
        username = vm_list[i]['admin-username']
        password = get_password()

        vm_details = ['az', 'vm', 'create', "--resource-group", resource_group_name, "--name", name, "--image", image, "--public-ip-sku", public_ip, "--admin-username", username, "--admin-password", password]
        print("Creating VM: '" + ' '.join(vm_details) + "'")

        vm_result = subprocess.Popen(vm_details, shell = True, stdout = subprocess.PIPE)
        vm_result_string = cli_output_to_dict(vm_result.communicate()[0])
        print(vm_result_string)

        '''
        if 'open-port' in vm_list[i].keys():
            port_command = ['az', 'vm', 'open-port', '--port', vm_list[i]['open-port'], "--resource-group", resource_group_name, "--name", name]
            print("Opening port " + vm_list[i]['open-port'] + ": '" + ' '.join(port_command) + "'")
            port_res = subprocess.Popen(port_command, shell = True, stdout = subprocess.PIPE)
            #port_res.wait()
        '''

        time = datetime.now()
        time_string = time.strftime("%Y-%m-%d:%H:%M:%S")
        date_string = time.strftime("%Y-%m-%d-%H-%M-%S")
        user = getpass.getuser()


        doc_info = "Date created: " + time_string + "\nUser: " + user + "\nName: " + name + "\nProject: " + resource_group_name + "\nPurpose: " + purpose
        doc_info = doc_info + "\nTeam: " + team + "\nOS: " + os_name + "\nAdvanced VM info:\n\tLocation:"  + vm_result_string['location'] + "\n\tMacAddress: " + vm_result_string['macAddress']
        doc_info = doc_info + "\n\tInternal IP: " + vm_result_string['privateIpAddress'] + "\n\tExternal IP: " + vm_result_string['publicIpAddress'] + "\nState: " + vm_result_string['powerState'] + "\n"
        print(doc_info)

        #write documentation file
        f = open("VMcreation_" + date_string + ".txt", "w")
        f.write(doc_info)
        f.close()

    rename_conf_file(filename)

    return 1

def create_gcp_vm(vm_list, filename):
    if (not is_valid_vm_list(vm_list, 'gcp')):
        print("Not a valid gcp conf file")
        return -1

    for i in vm_list:
        if not 'name' in vm_list[i].keys():
            print("Error: there is no name for GCP VM: " + i)
            break
        if not 'imageproject' in vm_list[i].keys():
            print("Error: imageproject group for GCP VM: " + i)
            break
        if not 'image' in vm_list[i].keys():
            print("Error: no image for GCP VM: " + i)
            break
        if not 'zone' in vm_list[i].keys():
            print("Error: no zone for GCP VM: " + i)
            break

        name = vm_list[i]['name']
        project_name = vm_list[i]['project']
        image = vm_list[i]['image']
        image_project = vm_list[i]['imageproject']
        os_name = vm_list[i]['os']
        purpose = vm_list[i]['purpose']
        team = vm_list[i]['team']
        location = vm_list[i]['zone']

        vm_command = ['gcloud', 'compute', 'instances', 'create', name, "--image=" + image, "--image-project=" + image_project, "--zone=" + location]
        print("Creating VM: '" + ' '.join(vm_command) + "'\n")

        vm_create = subprocess.Popen(vm_command, shell=True, stdout=subprocess.PIPE)
        vm_create.wait()

        vm_result = cli_output_to_string(vm_create.communicate()[0])
        if not vm_result:
            print("Error creating vm, please try again\n")
            continue
        vm_result = vm_result.split("\n")
        vm_result = " ".join(vm_result[1].split())
        vm_result = vm_result.split()

        time = datetime.now()
        time_string = time.strftime("%Y-%m-%d:%H:%M:%S")
        date_string = time.strftime("%Y-%m-%d-%H-%M-%S")
        user = getpass.getuser()

        doc_info = "Date created: " + time_string + "\nUser: " + user + "\nName: " + name + "\nProject: " + project_name + "\nPurpose: " + purpose
        doc_info = doc_info + "\nTeam: " + team + "\nOS: " + os_name + "\nAdvanced VM info:\n\tLocation: "  + vm_result[1] + "\n\tHardware: " + vm_result[2]
        doc_info = doc_info + "\n\tInternal IP: " + vm_result[3] + "\n\tExternal IP: " + vm_result[4] + "\nState: " + vm_result[5] + "\n"
        print(doc_info)

        f = open("VMcreation_" + date_string + ".txt", "w")
        f.write(doc_info)
        f.close()

    rename_conf_file(filename)

    return 1

config = configparser.ConfigParser()

while(True):
    choice = input("Enter 'az' for Azure or 'gcp' for Google Cloud (or 'x' to exit): ")
    if choice == 'az':
        az_filename = input("Enter Azure location/filename: ")

        config.read(az_filename)
        az_dict = {s:dict(config.items(s)) for s in config.sections()}
        try:
            create_azure_vm(az_dict, az_filename)
        except:
            print("Error, try again")
        
    elif choice == 'gcp':
        gcp_filename = input("Enter GCP location/filename: ")

        config.read(gcp_filename)
        gcp_dict = {s:dict(config.items(s)) for s in config.sections()}
        try:
            create_gcp_vm(gcp_dict, gcp_filename)
        except:
            print("Error, try again")

    elif choice == 'x':
        break
