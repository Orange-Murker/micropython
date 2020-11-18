# Python Modules

The .py files in this directory will be frozen into micropython.

The BioRobotics classes are put into a single file such that it represents a single package.  
Trickery with relative imports from `__init__.py` do not work with frozen modules in micropython. 
