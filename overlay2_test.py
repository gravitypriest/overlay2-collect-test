import sys
import subprocess
import json
import argparse
import requests
import os


def get_uploader_json():
    _url = 'https://api.access.redhat.com/r/insights/v1/static/uploader.json'
    res = requests.get(_url)
    if res.status_code == 200:
        return res.json()
    else:
        sys.exit('Error getting uploader.json: ' + res.status_code)


def inspect(image_id):
    docker_inspect = subprocess.check_output(
        ['docker', 'inspect', image_id])
    return json.loads(docker_inspect)[0]


def fs_list(filesystem):
    if 'LowerDir' not in filesystem:
        return [filesystem['UpperDir']]
    return [[filesystem['UpperDir']]] + filesystem['LowerDir'].split(':')


def check_file(fil):
    return os.path.exists(fil)


def scan(updog, fs_list):
    for f in updog['files']:
        found = False
        for fs in fs_list:
            # start from top level, and break once we find the file
            file_at_level = os.path.join(fs, f['file'].lstrip('/'))
            print ('checking ' + file_at_level + '.......')
            found = check_file(file_at_level)
            if found:
                print('***FOUND***: ' + file_at_level)
                break
        if not found:
            print('File does not exist in image: ' + f['file'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--image-id',
                        action='store',
                        required=True,
                        metavar='<ID>')

    args = parser.parse_args()
    updog = get_uploader_json()
    docker_info = inspect(args.image_id)
    if docker_info['GraphDriver']['Name'] != 'overlay2':
        sys.exit('Can\'t let you do that Star Fox')
    fs_list = fs_list(docker_info['GraphDriver']['Data'])
    scan(updog, fs_list)
