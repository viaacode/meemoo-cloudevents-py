from setuptools import find_packages, setup

setup(
    name="meemoo-cloudevents",
    version="0.1.0-rc.2",
    url="https://github.com/viaacode/meemoo-cloudevents-py",
    license="GPL",
    author="Meemoo dev, Maarten De Schrijver et al.",
    author_email="maarten.deschrijver@meemoo.be",
    description="Meemoo's implementation of CloudEvents",
    packages=find_packages(exclude=["tests"]),
    long_description=open("README.md", encoding="utf8").read(),
    zip_safe=False,
    setup_requires=["wheel"],
    install_requires=[
    ],
)
