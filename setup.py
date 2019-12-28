import setuptools

with open("README.MD", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyatomic", 
    version="0.0.2",
    author="k.r. goger",
    author_email="k.r.goger+pyatomic@gmail.com",
    description="Atomic makes your code thread safe",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kr-g/pyatomic",
    packages=setuptools.find_packages(),
    license = 'MIT',
    keywords = 'python threading lock sequence',
    install_requires=[],    
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: POSIX :: Linux',
        'Intended Audience :: Developers',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
)

