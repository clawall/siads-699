from setuptools import setup, find_packages

setup(
    name='tweet_financial_analysis',
    version='1.0.0',
    author='César Silveira;Darienne Stautter;Roy Spencer',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'numpy',
        'pandas',
        'scikit-learn',
        'requests'
    ]
)
