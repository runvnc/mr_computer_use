from setuptools import setup, find_packages

setup(
    name="mr_computer_use",
    version="1.1.0",
    packages=find_packages(where="src"),
    package_dir={"":"src"},
    package_data={
        "mr_computer_use": [
            "static/js/*.js",
            "templates/*.jinja2",
            "inject/*.jinja2",
            "override/*.jinja2"
        ],
    },
    install_requires=[
        "docker",
        "aiohttp",
        "pillow"
    ],
    python_requires=">=3.7",
)
