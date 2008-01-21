try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='oyoyo_bot_insult',
    version="",
    description='oyoyo_bot plugin to give/store insults ',
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
    insult = oyoyo_bot_insult:OyoyoInsult
    """,
)
