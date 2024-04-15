from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='pixel_bugs',
    version='0.1',
    packages=find_packages(),
    description='ALife szimuláció',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        'setuptools',
        'pygame',
        'numpy',
        'pytest',
        'scipy',
        
    ],
)