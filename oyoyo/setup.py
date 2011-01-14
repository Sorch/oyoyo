import sys
print(sys.path)

is_py3 = (sys.version_info >= (3,))

try:
    from setuptools import setup, find_packages
except ImportError as e:
    print(e)
    if is_py3:
        from distribute_setup import use_setuptools
    else:
        from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

# Call setup function, adding use_2to3 kwarg if under python 3
extras = {}
if is_py3:
    extras['use_2to3'] = True

setup(
    name='oyoyo',
    version="",
    description='a fast, simple irc module suitable for clients, bots and games',
    author='Dunk Fordyce, Daniel da Silva (current)',
    author_email='dunkfordyce@gmail.com, meltingwax@gmail.com',
    license="MIT",
    url='http://code.google.com/p/oyoyo/',
    install_requires=[],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    entry_points="""
    [console_scripts]
    oyoyo_example_bot = oyoyo.examplebot:main
    """,
    **extras
)
