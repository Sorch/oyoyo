try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='oyoyo_bot_better_auth',
    version="",
    description='oyoyo_bot plugin for better authentication',
    author='Dunk Fordyce',
    author_email='dunkfordyce@gmail.com',
    license="MIT",
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
    auth = oyoyo_bot_better_auth:Commands
    """,
)
