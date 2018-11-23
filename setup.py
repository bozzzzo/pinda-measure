import os
from setuptools import setup


ROOT_DIR = os.path.dirname(__file__)


with open(os.path.join(ROOT_DIR, "requirements.txt")) as fp:
    install_requires = [i for i in map(str.strip, fp)
                        if i and not i.startswith("#")]

print(install_requires)
setup(
    name="pinda_measure",
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    description="P.I.N.D.A. measurements",
    url="https://github.com/bozzzzo/pinda_measure",
    license="GPLv3",
    packages=["pinda_measure"],
    install_requires=install_requires,
    python_requires='>3.5.2',
    entry_points={
        "console_scripts": [
            "pinda_measure = pinda_measure.command:call_main",
        ]},
    classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Prusa i3 MK3 owners',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Operating System :: MacOS',
          'Operating System :: OS Independent',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: PINDA Calibration'
      ],
)
