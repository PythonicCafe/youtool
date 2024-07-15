from setuptools import setup, find_packages

setup(
    name="youtool",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'youtool[cli]',
    ],
    extras_require={
        'cli': [
            'loguru',
            'tqdm'
        ],
        'transcription': [
            'yt-dlp'
        ],
        'livechat': [
            'chat-downloader'
        ],
        'dev': [
            'autoflake',
            'black',
            'flake8',
            'ipython',
            'isort',
            'pytest',
            'pytest-dependency',
            'twine',
            'wheel'
        ],
        'base': [
            'isodate',
            'requests'
        ],
    },
    entry_points={
        'console_scripts': [
            'youtool=youtool.cli:main',
        ],
    },
)
