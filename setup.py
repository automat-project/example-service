from setuptools import setup

setup(
    name='AutoMat SDK Example Service',
    version='2.0.0',
    long_description=__doc__,
    packages=['AutoMatExampleService'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask', 'requests', 'numpy', 'datetime'],
    author="Johannes Pillmann",
    author_email="johanes.pillmann@tu-dortmund.de"
)
