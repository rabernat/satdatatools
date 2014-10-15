from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='satdatatools',
      version='0.1',
      description='Tools for analyzing ocean satellite data',
      url='https://github.com/rabernat/satdatatools',
      author='Ryan Abernathey',
      author_email='rpa@ldeo.columbia.edu',
      license='MIT',
      packages=['satdatatools'],
      install_requires=[
          'numpy','scipy'
      ],
      test_suite = 'nose.collector',
      zip_safe=False)
