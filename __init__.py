'''Binary Ninja plugin for the Motorola M6800 processor'''
from .architecture import M6800
from .binaryview import M6800BinaryView


# Register Architecture with Binary Ninja
M6800.register()

# Register BinaryView with Binary Ninja
M6800BinaryView.register()
