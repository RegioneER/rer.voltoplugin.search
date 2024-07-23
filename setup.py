"""Installer for the rer.volto.search package."""

from setuptools import find_packages
from setuptools import setup


long_description = "\n\n".join(
    [
        open("README.rst").read(),
        open("CONTRIBUTORS.rst").read(),
        open("CHANGES.rst").read(),
    ]
)


setup(
    name="rer.volto.search",
    version="1.0.0.dev0",
    description="Add-on RER for Plone to manage search results in Volto",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 6.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Development Status :: 5 - Production/Stable",
    ],
    keywords="Python Plone CMS",
    author="RedTurtle Technology",
    author_email="sviluppo@redturtle.it",
    url="https://github.com/collective/rer.volto.search",
    project_urls={
        "PyPI": "https://pypi.org/project/rer.volto.search/",
        "Source": "https://github.com/collective/rer.volto.search",
        "Tracker": "https://github.com/collective/rer.volto.search/issues",
        # 'Documentation': 'https://rer.volto.search.readthedocs.io/en/latest/',
    },
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["rer", "rer.volto"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[
        "setuptools",
        # -*- Extra requirements: -*-
        "plone.api>=1.8.4",
    ],
    extras_require={
        "test": [
            "gocept.pytestlayer",
            "plone.app.testing",
            "plone.restapi[test]",
            "pytest-cov",
            "pytest-plone>=0.2.0",
            "pytest-docker",
            "pytest-mock",
            "pytest",
            "zest.releaser[recommended]",
            "zestreleaser.towncrier",
            "pytest-mock",
            "requests-mock",
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = rer.volto.search.locales.update:update_locale
    """,
)
