from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license_text = f.read()

setup(
    name='pyshelem',
    version='0.1.0',
    description='A python engine to play Shelem',
    long_description=readme,
    author='Majid Laali',
    author_email='mjlaali@gmail.com',
    url='https://github.com/mjlaali/pyshelem',
    license=license_text,
    packages=find_packages(exclude=('tests', 'docs'))
)