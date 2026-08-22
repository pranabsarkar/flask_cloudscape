from setuptools import setup, find_packages

setup(
    name="flask-cloudscape",
    version="1.0.0",
    description="AWS Cloudscape Design System integration for Flask & Jinja2",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Pranab Sarkar",
    license="Apache-2.0",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "Flask>=2.0.0",
        "MarkupSafe>=2.0.0",
    ],
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Framework :: Flask",
    ],
)
