from fabric.api import env, local, lcd, shell_env
from fabric.colors import red, green
from fabric.decorators import task, runs_once
from fabric.operations import prompt
from fabric.utils import abort
from zipfile import ZipFile

import datetime
import fileinput
import importlib
import os
import random
import re
import subprocess
import sys
import time

PROJ_ROOT = os.path.dirname(env.real_fabfile)
env.project_name = 'domain_discovery_tool'
env.python = 'python' if 'VIRTUAL_ENV' in os.environ else 'bin/python'
env.elastic = os.environ['ELASTICSEARCH_SERVER'] if 'ELASTICSEARCH_SERVER' in os.environ else 'http://localhost:9200'
env.ache = os.environ['ACHE_HOME'] if 'ACHE_HOME' in os.environ else '~/ache'
env.nltk_data = PROJ_ROOT+'/nltk_data';
env.pythonpath = PROJ_ROOT+'/seeds_generator:.';
env.word2vec = PROJ_ROOT+'/ranking'

@task
def setup():
    """
    Set up a local development environment

    This command must be run with Fabric installed globally (not inside a
    virtual environment)
    """
    if os.getenv('VIRTUAL_ENV') or hasattr(sys, 'real_prefix'):
        abort(red('Deactivate any virtual environments before continuing.'))
    make_settings()
    make_virtual_env()
    install_nltk_data()
    download_word2vec_file()
    compile_seeds_generator()
    symlink_packages()
    #install_node_packages()
    print ('\nDevelopment environment successfully created.')

@task
@runs_once
def make_settings():
    """
    Generate a local settings file.

    Without any arguments, this file will go in vis/config.conf.
    """
    with lcd(PROJ_ROOT):
        settings_file = 'vis/config.conf'
        local('if [ ! -f {0} ]; then cp {1} {0}; fi'.format(
            settings_file, 'vis/config.conf-in'))
        for line in fileinput.input(settings_file, inplace=True):
            print line.replace("tools.staticdir.root = .",
                               "tools.staticdir.root = {0}/{1}".format(
                                   PROJ_ROOT,'vis/html')),

        settings_file = 'config.conf'
        local('if [ ! -f {0} ]; then cp {1} {0}; fi'.format(
            settings_file, 'config.conf-in'))

@task
def runserver():
    "Run the development server"
    with lcd(PROJ_ROOT), \
      shell_env(NLTK_DATA=env['nltk_data'],
                PYTHONPATH=env['pythonpath'],
                ACHE_HOME=env['ache'],
                DDT_HOME=PROJ_ROOT):
        local('{python} models/seed_crawler_model.py'.format(**env))
        #local('{python} manage.py runserver --traceback'.format(**env))

@task
def runvis():
    "Run the development server"
    with lcd(PROJ_ROOT), \
      shell_env(NLTK_DATA=env['nltk_data'],
                PYTHONPATH=env['pythonpath'],
                ACHE_HOME=env['ache'],
                DDT_HOME=PROJ_ROOT):
        local('{python} vis/server.py'.format(**env))

@task
def install_dependencies():
    make_virtual_env()
    symlink_packages()
    install_nltk_data()
    download_word2vec_file()

def make_virtual_env():
    "Make a virtual environment for local dev use"
    with lcd(PROJ_ROOT):
        local('virtualenv .')
        local('./bin/pip install -r requirements.txt')

def install_node_packages():
    "Install requirements from NPM."
    with lcd(PROJ_ROOT):
        local('npm install')

def install_nltk_data():
    "Install data files for NLTK."
    with lcd(PROJ_ROOT), shell_env(NLTK_DATA=env['nltk_data']):
        local("if [ ! -d {nltk_data} ]; then mkdir {nltk_data}; fi".format(**env))
        local('if [ ! -d {nltk_data}/chunkers ]; then {python} -m nltk.downloader -d {nltk_data} stopwords brown; fi'.format(**env))

def download_word2vec_file():
    "Download file that contains word2vec data"
    print '\nDownloading word2vec file D_cbow_pdw_8B.pkl to ' + env['word2vec']+'\n'
    local("if [ ! -d {word2vec} ]; then mkdir {word2vec}; fi".format(**env))
    with lcd(env['word2vec']), shell_env(PYTHONPATH=env['pythonpath']):
        if (not os.path.isfile(env['word2vec']+'/D_cbow_pdw_8B.pkl')):
            local('wget https://s3.amazonaws.com/vida-nyu/DDT/D_cbow_pdw_8B.pkl')
@task
def compile_seeds_generator():
    "Compile the sees generator."
    with lcd(PROJ_ROOT+'/seeds_generator'):
        local('mvn compile assembly:single')

def symlink_packages():
    "Symlink python packages not installed with pip"
    missing = []
    requirements = (req.rstrip().replace('# symlink: ', '')
                    for req in open('requirements.txt', 'r')
                    if req.startswith('# symlink: '))
    for req in requirements:
        try:
            module = importlib.import_module(req)
        except ImportError:
            missing.append(req)
            continue
        with lcd(os.path.join(PROJ_ROOT, 'lib', 'python2.7', 'site-packages')):
            local('ln -f -s {}'.format(os.path.dirname(module.__file__)))
    if missing:
        abort('Missing python packages: {}'.format(', '.join(missing)))
