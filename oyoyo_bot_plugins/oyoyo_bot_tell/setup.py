try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='oyoyo_bot_tell',
    version="",
    description='oyoyo_bot plugin to give messages to users',
    author='Dunk Fordyce',
    author_email='dunkfordyce@gmail.com',
    licence="MIT",
    #url='',
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
    [oyoyo_bot.commands]
    tell = oyoyo_bot_tell:Commands

    [oyoyo_bot.listeners]
    tell = oyoyo_bot_tell:Listener

    [oyoyo_bot.config]
    tell = oyoyo_bot_tell:defaults
    """,
)
