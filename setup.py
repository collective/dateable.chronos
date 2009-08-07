from setuptools import setup, find_packages
import sys, os

f = open('dateable/chronos/version.txt')
version = f.read().strip()
f.close()

f = open('doc/README.txt')
readme = f.read()
f.close()

f = open('doc/CHANGES.txt')
changes = f.read()
f.close()

setup(name='dateable.chronos',
      version=version,
      description="Dateable calendaring views",
      long_description=readme + '\n\n' + changes,
      classifiers=[
          'Framework :: Zope3',
          'Framework :: Plone',
          'Programming Language :: Python',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
      keywords='Dateable Calendaring calendar event icalendar',
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
          'dateable.kalends >= 0.4',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
