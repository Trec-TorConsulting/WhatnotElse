from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

from whatnot_else import __version__ as version

setup(
    name="whatnot_else",
    version=version,
    description="Enterprise Frappe / ERPNext custom app for Whatnot live sellers",
    author="Tobey Rector",
    author_email="trecto282@cable.comcast.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)
