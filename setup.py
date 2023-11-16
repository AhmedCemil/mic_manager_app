from setuptools import setup

setup(
    name="mic_manager_app",
    version="0.1",
    packages=['mic_manager_app'],
    url='https://github.com/AhmedCemil/mic_manager_app',
    license='MIT',
    author="Ahmed Cemil Bilgin",
    author_email="ahmed.c.bilgin@gmail.com",
    description="Mic Manager App",
    install_requires=[
        'pycaw',
        'notify-py',
        'infi.systray',
    ],
)
