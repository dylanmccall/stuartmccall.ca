from setuptools import setup, find_packages

setup(
    name="web-stuartmccall-ca",
    version="1.0",
    author="Dylan McCall",
    author_email="dylan@dylanmccall.com",
    url="http://www.stuartmccall.ca",
    packages=find_packages(),
    scripts=['manage.py'],
    python_requires='>=3.4',
    setup_requires=[
        'wheel>=0.31.1'
    ],
    install_requires=[
        'django-compressor-autoprefixer>=0.1.0',
        'django-compressor>=2.2',
        'django-dbbackup>=3.2.0',
        'django-extensions>=1.9.7',
        'django-simplemde>=0.1.0',
        'django-tinycontent>=0.7.1',
        'django-sort-order-field==0.1',
        'Django>=1.11.18,<1.12',
        'Markdown>=2.6.9',
        'Pillow>=4.3.0',
        'python-memcached>=1.58',
        'pytz==2018.5',
        'sorl-thumbnail>=12.4.1'
    ],
    dependency_links=[
        'git+ssh://git@github.com/dylanmccall/django-sort-order-field.git#egg=django-sort-order-field-0.1'
    ],
    tests_require=[
        'nose2>=0.8.0'
    ]
)
