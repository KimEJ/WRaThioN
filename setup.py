from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name                = 'WRaThioN',
    version             = '0.1.0',
    description         = 'WRaThioN: WRTN Client For Python',
    author              = 'kimuj5090',
    author_email        = 'kimuj5090@gmail.com',
    url                 = 'https://github.com/KimEJ/WRaThioN',
    # download_url        = 'https://github.com/KimEJ/WRaThioN/archive/0.0.tar.gz',
    install_requires    =  ['pyjwt', 'sseclient-py', 'requests', 'argparse',],
    packages            = find_packages(exclude = ['pyjwt', 'sseclient-py', 'requests', 'argparse',]),
    keywords            = ['WRTN', 'WRaThioN'],
    python_requires     = '>=3',
    package_data        = {},
    license             = 'MIT',
    long_description    = long_description,
    long_description_content_type='text/markdown',
    classifiers         = [
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
    ],
)
