from setuptools import setup

setup(
    name='reddit-tracker',
    version='1.3',
    author='OpposedDeception',
    description='A console app for tracking Reddit users and subreddits',
    py_modules=['reddit_tracker'],
    install_requires=[
        'requests',
        'praw',
        'argparse',
        'rich',
        'pyfiglet',
        'csv'
    ],
    entry_points='''
        [console_scripts]
        reddit-tracker=reddit_tracker:main
    ''',
)
