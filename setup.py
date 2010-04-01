from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='clitter',
      version=version,
      description="Clitter Twitter Client",
      long_description="""\
A Unix CLI based Twitter client""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='twitter',
      author='Kyle Terry',
      author_email='kyle@kyleterry.com',
      url='http://kyleterry.com/p/clitter',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
