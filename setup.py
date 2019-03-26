
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flairjsonnlp",
    version="0.0.1",
    author="Damir Cavar, Oren Baldinger, Maanvitha Gongalla, Anurag Kumar, Murali Kammili",
    author_email="damir@cavar.me",
    description="The Python Flair JSON-NLP package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dcavar/Flair-JSON-NLP",
    packages=setuptools.find_packages(),
    install_requires=[
        'flair>=0.4.1',
        'pyjsonnlp>=0.2.1'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
