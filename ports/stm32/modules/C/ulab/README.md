# ulab

ulab from https://github.com/v923z/micropython-ulab is included as a submodule here to be built into micropython.

Note that the `*.mk` of ulab is inside the `code/` directory, making it unreachable for the user modules crawler in the 
build. So instead ulab in included in an extra sub-directory and a copy of the `*.mk` was made to suit the new file
paths.
