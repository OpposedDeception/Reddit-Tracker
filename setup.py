from setuptools import setup

setup(
    name='reddit-tracker',
    version='1.0.',
    author='OpposedDeception',
    description='A console app for tracking Reddit users and subreddits',
    py_modules=['reddit_tracker'],
    install_requires=[
        'requests',
        'beautifulsoup4',
        'argparse',
        'rich',
        'pyfiglet'
    ],
    entry_points='''
        [console_scripts]
        reddit-tracker=reddit_tracker:main
    ''',
)
