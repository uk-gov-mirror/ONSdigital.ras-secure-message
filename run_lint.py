import os
import pylint.lint

if __name__ == '__main__':
    os.system('flake8 --count --format=pylint')
    pylint.lint.Run(['--reports=n', '--output-format=colorized', '--rcfile=.pylintrc', '-j', '0', './app', './tests'])
    # pylint.lint.Run(['--errors-only', '--output-format=colorized', '--rcfile=.pylintrc', './app', './tests'])