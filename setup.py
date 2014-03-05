try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='pycoinbase',
    version='0.1.0-dev',
    description='Coinbase API',
    license='MIT',
    url='https://github.com/dmpayton/pycoinbase',
    author='Derek Payton',
    author_email='derek.payton@gmail.com',
    py_modules=['pycoinbase'],
    install_requires=['requests'],
    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ),
)
