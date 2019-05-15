
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flairjsonnlp",
    version="0.0.6",
    author="Damir Cavar, Oren Baldinger, Maanvitha Gongalla, Anurag Kumar, Murali Kammili, Boli Fang",
    author_email="damir@cavar.me",
    description="The Python Flair JSON-NLP package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dcavar/Flair-JSON-NLP",
    packages=setuptools.find_packages(),
    install_requires=[
        'flair>=0.4.1',
        'pyjsonnlp>=0.2.6'
    ],
    setup_requires=["pytest-runner"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    test_suite="tests",
    tests_require=["pytest", "coverage"]
)
