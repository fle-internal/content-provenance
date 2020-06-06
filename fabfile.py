import json
import os
import time
import requests
from jinja2 import Template


from fabric.api import env, task, local, sudo, run
from fabric.api import get, put, require
from fabric.colors import red, green, blue, yellow
from fabric.context_managers import cd, prefix, show, hide, shell_env
from fabric.contrib.files import exists, sed, upload_template
from fabric.utils import puts


# PREREQUISITES
# 1. SusOps engineer be part of the GCP project kolibri-demo-servers
# 2. The username $USER must be one of the default accounts created on instances, see:
#    https://console.cloud.google.com/compute/metadata?project=kolibri-demo-servers


# FAB SETTTINGS
################################################################################
env.user = os.environ.get('USER')  # assume ur local username == remote username
CONFIG_DIR = './config'



# CONSTANTS
################################################################################

env.roledefs = {
    'alejandro-demo': { 'hosts':['35.227.71.104'] }
}


SAMPLE_CURATED_CHANNELS = [
    # curated
    '32b5fc156a7d46ddb8cea9663a1871be',
    '591b7e1bc89645ef846c1685a7dd7b50',
    '335b8e0ed8a3426580e4c58f62810d25',
    'fdab6fb66ba24d05acd011e85bdb36ba',
    '54aa253a3266416da0c847e16e64aa7b',
    'e006726b1f35487eb7b2aa7cb11caf4c',
    '8111ac9ab99646a1be9984f13b29167d',
    '0543f0f0516b4eeebf281854e80d3e14',
    'ae8f138108c1410aa4c6d8bf734ebf57',
    'be30cd98263244768c8684320441eecb',
    '0a9cd3c76a36402e87d6bf80a997901f',
    '6f63fe92ad1044fdb3b3c17d54d0978e',
    '9e5305326ed742d0892479dea825a514',
    '292583c17e6d4199b81f0423bec58766',
    '34fd6722dd734687bc5291fc717d2d7f',
    'a68a5bf4aa8a475197658c7a0da528c7',
]

SAMPLE_CHANNELS_INFO = {
    'Camara Tanzania': {
        'a68a5bf4aa8a475197658c7a0da528c7': 'Camara Education Tanzania'
    },
    'KICD': {
        '591b7e1bc89645ef846c1685a7dd7b50': 'KICD Biology Curriculum (DRAFT)',
        '32b5fc156a7d46ddb8cea9663a1871be': 'KICD Chemistry Curriculum (DRAFT)',
        '335b8e0ed8a3426580e4c58f62810d25': 'KICD Life Skills Curriculum (DRAFT)',
        'fdab6fb66ba24d05acd011e85bdb36ba': 'KICD Mathematics Curriculum (DRAFT)',
        '54aa253a3266416da0c847e16e64aa7b': 'KICD Physics Curriculum (DRAFT)'
    },
    'Nalanda India': {
        'ae8f138108c1410aa4c6d8bf734ebf57': 'Nalanda Math',
        # 'be30cd98263244768c8684320441eecb': 'Math Olympiad (The Nalanda Project)',    # not PUBLISHed
        # '0a9cd3c76a36402e87d6bf80a997901f': 'Maharashtra 6,7,8',                      # not PUBLISHed
        '6f63fe92ad1044fdb3b3c17d54d0978e': 'BodhaGuru CBSE English Channel',
        # '9e5305326ed742d0892479dea825a514': 'CBSE English Medium Class 3 to 8',   # filtered out because does not load
        # '292583c17e6d4199b81f0423bec58766': 'CBSE KA English Class 6 to 9',       # filtered because unique constraint fails
        '34fd6722dd734687bc5291fc717d2d7f': 'CBSE Khan Academy Math 6-9 (English)'
    },
    'UNICEF Uganda': {
        'e006726b1f35487eb7b2aa7cb11caf4c': 'Secondary School',
        '8111ac9ab99646a1be9984f13b29167d': 'Youth Center',
        # '0543f0f0516b4eeebf281854e80d3e14': 'Teacher Resources'                   # skipped because not publshing
    }
}


# GET DATA FROM STUDIO
################################################################################

@task
def download_sankey_graph_data_file(channel_id, destdir='data_v2'):
    filename = channel_id + '.json'
    url = 'https://studio.learningequality.org/content/exports/importsdata/sankey/' + filename
    response = requests.get(url)
    destpath = os.path.join(destdir, filename)
    with open(destpath, 'wb') as destfile:
        destfile.write(response.content)
    puts(green('Saved Sankey graph data file ' + destpath))


@task
def download_sankey_graph_data():
    for channel_id in SAMPLE_CURATED_CHANNELS:
        download_sankey_graph_data_file(channel_id)



# BUILD
################################################################################

@task
def build():
    local('rm -rf build/*')
    local('cp -r components build/')
    local('cp -r fonts build/')
    local('cp sankeyTest.js build/')
    local('cp style.css build/')
    for org, channels_info in SAMPLE_CHANNELS_INFO.items():
        for channel_id, channel_name in channels_info.items():
            print(channel_id)
            assert channel_id in SAMPLE_CURATED_CHANNELS
            build_page(channel_id)
    build_listing_page(SAMPLE_CHANNELS_INFO)


def get_channel_data(channel_id):
    filename = channel_id + '.json'
    data_path = 'data_v2/' + filename
    # load channel_data
    graph_data = json.load(open(data_path))
    channel_data = graph_data['nodes'][channel_id]
    return channel_data


def build_page(channel_id):
    destdir = 'build/' + channel_id
    local('mkdir ' + destdir)
    local('mkdir ' + destdir + '/data_v2')

    # copy data into place
    filename = channel_id + '.json'
    data_path = 'data_v2/' + filename
    local('cp ' + data_path + ' ' + destdir+'/data_v2/')

    # load channel_data
    channel_data = get_channel_data(channel_id)

    # load template
    template_path = 'index_html_template.jinja2'
    template_src = open(template_path).read()
    template = Template(template_src)
    
    # render template
    index_html = template.render(
        title='Import counts for channel ' + channel_data['name'] + ' (' + channel_data['channel_id'] + ')',
        data_path=data_path,
    )
    with open(os.path.join(destdir, 'index.html'), 'w') as outf:
        outf.write(index_html)

def build_listing_page(sample_channels_info):
    # load template
    template_path = 'listing_template.jinja2'
    template_src = open(template_path).read()
    template = Template(template_src)

    # render template
    index_html = template.render(
        title='Studio Channel content import provenanance',
        description='These charts show the aggregate counts of content is imported from to create channels aligned to particular curriculum in different countries.',
        sample_channels_info=sample_channels_info,
    )
    with open(os.path.join('build', 'index.html'), 'w') as outf:
        outf.write(index_html)
    

# DEPLOY
################################################################################

DEPLOY_ZIPNAME = 'webroot.zip'

@task
def deploy():
    if os.path.exists(DEPLOY_ZIPNAME):
        os.remove(DEPLOY_ZIPNAME)
    local('zip -r %s build/' % DEPLOY_ZIPNAME)
    remote_zip_path = '/var/www/' + DEPLOY_ZIPNAME
    if exists(remote_zip_path):
        print('removing old zip', remote_zip_path)
        sudo('rm %s' % remote_zip_path)
    put(DEPLOY_ZIPNAME, remote_zip_path)
    with cd('/var/www/'):
        sudo('unzip %s ' % DEPLOY_ZIPNAME)
        sudo('rm -rf importcounts')
        sudo('mv build importcounts')
    # cleanup zip files
    if exists(remote_zip_path):
        print('removing old zip', remote_zip_path)
        sudo('rm %s' % remote_zip_path)
    if os.path.exists(DEPLOY_ZIPNAME):
        os.remove(DEPLOY_ZIPNAME)

