from setuptools import find_packages, setup


def read_requirements(filename="requirements.txt"):
    "Read the requirements"
    with open(filename) as f:
        return [
            line.strip()
            for line in f
            if line.strip() and line[0].strip() != "#" and not line.startswith("-e ")
        ]


def get_version(filename="directory/version.py", name="VERSION"):
    "Get the version"
    with open(filename) as f:
        s = f.read()
        d = {}
        exec(s, d)
        return d[name]


setup(
    name="django-dept-directory",
    version=get_version(),
    author="Dave Gabrielson",
    author_email="Dave_Gabrielson@UManitoba.CA",
    description="Basic directory services for Django: core models for people and places.",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=read_requirements(),
    license="GNU Lesser General Public License (LGPL) 3.0",
)
