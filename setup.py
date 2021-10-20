import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyeletric",
    version="1.0.0",
    author="luanws",
    author_email="luan.w.silveira@gmail.com",
    description="Python package for electric circuits",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/luanws/pyeletric",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'numpy',
    ],
    python_requires='>=3.7',
)
