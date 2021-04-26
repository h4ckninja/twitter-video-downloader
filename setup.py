from setuptools import setup

requirements = [
    'requests',
    'm3u8',
    'ffmpeg-python',
]

setup(
    name='twitter-video-downloader',
    version='0.1.0',
    description='Library for Twitter video downloading',
    author='Jorge Arévalo (based on the original scripy by h4ckninja)',
    author_email='jorgeas80@tuta.io',
    license='MIT',
    url='https://github.com/jorgeas80/twitter-video-downloader',
    keywords=['twitter', 'video', 'download'],
    install_requires=requirements,
    extras_require={
        'dev': [
            'ipython',
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Topic :: Multimedia :: Video',
        'Topic :: Multimedia :: Video :: Conversion',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ]
)
