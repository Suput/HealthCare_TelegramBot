import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="test-pkg-Suput",
    version="0.0.1",
    author="Nick",
    author_email="test@gmail.com",
    description="It's a client version for HealthCare",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Suput/HealthCare_TelegramBot",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)