from setuptools import setup, find_packages

version = '1.0'

f = open('README.txt')
readme = f.read()
f.close()

f = open('CHANGES.txt')
changes = f.read()
f.close()

setup(name='dateable.chronos',
      version=version,
      description="Dateable calendaring views",
      long_description=readme + '\n\n' + changes,
      classifiers=[
          'Framework :: Plone',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
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
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
