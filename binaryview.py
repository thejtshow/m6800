'''Binary View for the Motorola M6800 Processor'''
import struct

from binaryninja import (BinaryView, Architecture, SegmentFlag, SectionSemantics)

from .instructions import ADDRESS_MASK


class M6800BinaryView(BinaryView):
    '''M6800 BinaryView class.'''

    name = 'M6800'
    long_name = 'Motorola M6800'

    def __init__(self, data):
        super().__init__(file_metadata=data.file, parent_view=data)
        self.raw = data

    @classmethod
    def is_valid_for_data(self, unused_data):
        return True

    def init(self):
        self.platform = Architecture[M6800BinaryView.name].standalone_platform
        self.arch = Architecture[M6800BinaryView.name]

        # Create RAM Segment
        self.add_auto_segment(
            0, 0x200, 0, 0x200,
            (SegmentFlag.SegmentContainsData |
             SegmentFlag.SegmentReadable |
             SegmentFlag.SegmentWritable)
        )

        # Create Program RAM Section
        self.add_auto_section(
            'Program Memory', 0, 0x100, SectionSemantics.ReadWriteDataSectionSemantics
        )

        # Create CMOS RAM Section
        self.add_auto_section(
            'CMOS Memory', 0x100, 0x100, SectionSemantics.ReadWriteDataSectionSemantics
        )

        # Create Exectuable Segment
        self.add_auto_segment(
            0x5800, 0x2800, 0x5800, 0x2800,
            (SegmentFlag.SegmentContainsCode |
             SegmentFlag.SegmentReadable |
             SegmentFlag.SegmentExecutable)
        )

        # Add Game OS Section
        self.add_auto_section(
            'Game OS', 0x5800, 0x1000, SectionSemantics.ReadOnlyCodeSectionSemantics
        )

        # Add Flipper OS Section
        self.add_auto_section(
            'Flipper OS', 0x6800, 0x1800, SectionSemantics.ReadOnlyCodeSectionSemantics
        )

        # Find the start address
        start_address_pointer = 0xFFFE & ADDRESS_MASK
        entry_addr = struct.unpack(
            '>H', self.raw.read(start_address_pointer, 2))[0] & ADDRESS_MASK

        # Add the start address to the BinaryView
        self.add_entry_point(entry_addr)
        return False

    def perform_get_address_size(self):
        return 2

    def perform_is_executable(self):
        return True

    def perform_get_entry_point(self):
        return self.entry_point
