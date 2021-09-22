from setuptools import setup, find_packages

setup(
    name="web-stuartmccall-ca",
    version="1.0",
    author="Dylan McCall",
    author_email="dylan@dylanmccall.ca",
    url="http://www.stuartmccall.ca",
    packages=find_packages(),
    include_package_data=True,
    scripts=['manage.py'],
    python_requires='>=3.4',
    setup_requires=[
        'wheel>=0.31.1'
    ],
    install_requires=[
        'django-compressor-autoprefixer>=0.1.0',
        'django-compressor>=2.4',
        'django-dbbackup>=3.3.0',
        'django-extensions>=2.2.9',
        'django-simplemde>=0.1.3',
        'django-tinycontent>=0.8.0',
        'django-sort-order-field>=1.2',
        'Django>=2.2,<2.3',
        'Markdown>=3.2.1',
        'Pillow>=7.1.2,<8.4.0',
        'python-memcached>=1.59',
        'pytz==2021.1',
        'sorl-thumbnail>=12.6.3'
    ],
    tests_require=[
        'nose2>=0.8.0'
    ]
)
