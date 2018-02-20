from setuptools import setup

setup(
    name='homeserver',
    packages=['homeserver', 'homeconsole'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)
