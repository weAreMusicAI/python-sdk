from setuptools import setup, find_packages

setup(
    name='musicai',
    version='0.1.0',
    author='Music.AI',
    author_email='support@music.ai',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    description='A Python client library for the Music.ai API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/music-ai/python-client',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)