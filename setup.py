'''
Created on Jul 4, 2012

@author: Geert
'''
from distutils.core import setup
import py2exe

setup(console=['__init__.py'],
      packages=['tracklistscrobbler'],
      package_dir={'tracklistscrobbler': 'src/tracklistscrobbler'}
      )