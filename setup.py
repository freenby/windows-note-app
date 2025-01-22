from setuptools import setup, find_packages

setup(
    name="my-note",
    version="1.0.0",
    description="A feature-rich note-taking application with reminder functionality",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        'tkcalendar>=1.6.1',
        'pillow>=10.0.0',
        'pywin32>=306',
        'keyboard>=0.13.5',
        'pystray>=0.19.5',
    ],
    entry_points={
        'console_scripts': [
            'my-note=main:main',
        ],
    },
    python_requires='>=3.6',
    include_package_data=True,
    package_data={
        '': ['data/*.json'],  # 包含所有data目录下的json文件
    },
)
