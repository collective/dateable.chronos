from setuptools import setup, find_packages
import sys, os

version = '0.1dev'

readme = open('doc/README.txt')
long_description = readme.read()
readme.close()

setup(name='dateable.chronos',
      version=version,
      description="Dateable calendaring views",
      long_description=long_description,
      classifiers=[
          'Framework :: Zope3',
          'Framework :: Plone',
          'Programming Language :: Python',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
      keywords='Dateable Calendaring',
      author='Lennart Regebro',
      author_email='regebro@gmail.com',
      url='http://plone.org/products/dateable',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['dateable'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
