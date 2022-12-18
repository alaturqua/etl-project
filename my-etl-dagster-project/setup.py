from setuptools import find_packages, setup

if __name__ == "__main__":
    setup(
        name="my_etl_dagster_project",
        packages=find_packages(exclude=["my_etl_dagster_project_tests"]),
        install_requires=[
            "dagster",
        ],
        extras_require={"dev": ["dagit", "pytest"]},
    )
