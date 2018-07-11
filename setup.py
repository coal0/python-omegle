try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open("README.rst") as file:
    long_description = file.read()


setup(
    name="python-omegle",
    version="1.0.3",
    url="https://github.com/coal0/python-omegle",

    author="coal0",
    author_email="daniel_x3@protonmail.com",

    description="A simple Python API for the Omegle text chat service",
    long_description=long_description,
    long_description_content_type="text/x-rst",

    keywords="omegle chat webchat api",
    classifiers=(
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Communications :: Chat"
    ),

    packages=["python_omegle"],
    install_requires=["requests"],
)
