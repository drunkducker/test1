from setuptools import setup

setup(
    name='CodeReviewer',
    version='0.1',
    description='A Mycroft skill for reviewing and explaining code',
    author='Your Name',
    author_email='your@email.com',
    packages=['CodeReviewer'],
    install_requires=['mycroft-core', 'pygments', 'pydoc', 'subprocess', 'cursed', 'sqlite3'],
    entry_points={
        'console_scripts': [
            'CodeReviewer = CodeReviewer:main'
        ]
    }
)