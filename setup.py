from setuptools import setup

with open("README") as readme:
    setup(
        name = "tmux-master",
        version = "0.0",

        license = "GPL",
        description = readme.readline().strip(),
        long_description = readme.read().strip() or None,
        url = "https://github.com/KonishchevDmitry/tmux-master",

        install_requires = [ "psh" ],

        author = "Dmitry Konishchev",
        author_email = "konishchev@gmail.com",

        classifiers = [
            "Development Status :: 3 - Alpha",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "Intended Audience :: System Administrators",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: POSIX",
            "Operating System :: Unix",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Topic :: System :: Shells",
            "Topic :: System :: Systems Administration",
            "Topic :: Terminals",
            "Topic :: Utilities",
        ],
        platforms = [ "unix", "linux", "osx" ],

        py_modules = [ "tmux_master" ],

        entry_points = {
            "console_scripts": [ "tmux-master = tmux_master:main" ],
        },
    )
