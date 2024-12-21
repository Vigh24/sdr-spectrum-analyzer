from setuptools import setup, find_packages

setup(
    name="sdr-analyzer",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'numpy>=1.26.0',
        'matplotlib>=3.8.0',
        'PyQt6>=6.5.0',
        'scipy>=1.11.0',
        'pyqtgraph>=0.13.3',
        'colorcet>=3.0.1',
        'sounddevice>=0.4.6',
        'pandas>=2.0.0',
        'scikit-learn>=1.3.0'
    ]
) 