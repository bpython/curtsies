from setuptools import setup
import curtsies

setup(name='curtsies',
      version=curtsies.__version__,
      description='Curses-like terminal wrapper, with colored strings!',
      url='https://github.com/thomasballinger/curtsies',
      author='Thomas Ballinger',
      author_email='thomasballinger@gmail.com',
      license='MIT',
      packages=['curtsies'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          ],
      zip_safe=False)
