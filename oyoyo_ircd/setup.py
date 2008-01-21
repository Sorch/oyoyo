try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='oyoyo_ircd',
    version="",
    description='a mini irc daemon',
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
    [console_scripts]
    oyoyo_ircd = oyoyo_ircd.app:make_app
    """,
)
