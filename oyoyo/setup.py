import sys
print sys.path
try:
    from setuptools import setup, find_packages
except ImportError, e:
    print e
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='oyoyo',
    version="",
    description='a fast, simple irc module suitable for clients, bots and games',
    author='Dunk Fordyce',
    author_email='dunkfordyce@gmail.com',
    license="MIT",
    url='http://code.google.com/p/oyoyo/',
    install_requires=[],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    #package_data={'fdweb': ['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors = {'fdweb': [
    #        ('**.py', 'python', None),
    #        ('templates/**.mako', 'mako', None),
    #        ('public/**', 'ignore', None)]},
    entry_points="""
    [console_scripts]
    oyoyo_log = oyoyo.logclient:make_app
    """,
)
