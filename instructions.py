'''File containing all instructions for the M6800 assembly language.'''

BRANCH_INSTRUCTIONS = [
    0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a, 0x2b, 0x2c, 0x2d, 0x2e, 0x2f
]

JMP_INSTRUCTIONS = [
    0x20, 0x6E, 0x7E  # 0x20 is unconditional branch, the other two are unconditional jumps
]

CALL_INSTRUCTIONS = [0x8D, 0xAD, 0xBD]

RETURN_INSTRUCTIONS = [0x39]

INSTRUCTIONS = {
    # Opcode: (mnemonic, length, accumulator, address mode)
    0x01: ('NOP', 1, None, None),
    0x06: ('TAP', 1, None, None),
    0x07: ('TPA', 1, None, None),
    0x08: ('INX', 1, None, None),
    0x09: ('DEX', 1, None, None),
    0x0A: ('CLV', 1, None, None),
    0x0B: ('SEV', 1, None, None),
    0x0C: ('CLC', 1, None, None),
    0x0D: ('SEC', 1, None, None),
    0x0E: ('CLI', 1, None, None),
    0x0F: ('SEI', 1, None, None),
    0x10: ('SBA', 1, None, None),
    0x11: ('CBA', 1, None, None),
    0x16: ('TAB', 1, None, None),
    0x17: ('TBA', 1, None, None),
    0x19: ('DAA', 1, None, None),
    0x1B: ('ABA', 1, None, None),
    0x20: ('BRA', 2, None, 'REL'),
    0x22: ('BHI', 2, None, 'REL'),
    0x23: ('BLS', 2, None, 'REL'),
    0x24: ('BCC', 2, None, 'REL'),
    0x25: ('BCS', 2, None, 'REL'),
    0x26: ('BNE', 2, None, 'REL'),
    0x27: ('BEQ', 2, None, 'REL'),
    0x28: ('BVC', 2, None, 'REL'),
    0x29: ('BVS', 2, None, 'REL'),
    0x2A: ('BPL', 2, None, 'REL'),
    0x2B: ('BMI', 2, None, 'REL'),
    0x2C: ('BGE', 2, None, 'REL'),
    0x2D: ('BLT', 2, None, 'REL'),
    0x2E: ('BGT', 2, None, 'REL'),
    0x2F: ('BLE', 2, None, 'REL'),
    0x30: ('TSX', 1, None, None),
    0x31: ('INS', 1, None, None),
    0x32: ('PUL', 1, 'A', None),
    0x33: ('PUL', 1, 'B', None),
    0x34: ('DES', 1, None, None),
    0x35: ('TXS', 1, None, None),
    0x36: ('PSH', 1, 'A', None),
    0x37: ('PSH', 1, 'B', None),
    0x39: ('RTS', 1, None, None),
    0x3B: ('RTI', 1, None, None),
    0x3E: ('WAI', 1, None, None),
    0x3F: ('SWI', 1, None, None),
    0x40: ('NEG', 1, 'A', None),
    0x43: ('COM', 1, 'A', None),
    0x44: ('LSR', 1, 'A', None),
    0x46: ('ROR', 1, 'A', None),
    0x47: ('ASR', 1, 'A', None),
    0x48: ('ASL', 1, 'A', None),
    0x49: ('ROL', 1, 'A', None),
    0x4A: ('DEC', 1, 'A', None),
    0x4C: ('INC', 1, 'A', None),
    0x4D: ('TST', 1, 'A', None),
    0x4F: ('CLR', 1, 'A', None),
    0x50: ('NEG', 1, 'B', None),
    0x53: ('COM', 1, 'B', None),
    0x54: ('LSR', 1, 'B', None),
    0x56: ('ROR', 1, 'B', None),
    0x57: ('ASR', 1, 'B', None),
    0x58: ('ASL', 1, 'B', None),
    0x59: ('ROL', 1, 'B', None),
    0x5A: ('DEC', 1, 'B', None),
    0x5C: ('INC', 1, 'B', None),
    0x5D: ('TST', 1, 'B', None),
    0x5F: ('CLR', 1, 'B', None),
    0x60: ('NEG', 2, None, 'IND'),
    0x63: ('COM', 2, None, 'IND'),
    0x64: ('LSR', 2, None, 'IND'),
    0x66: ('ROR', 2, None, 'IND'),
    0x67: ('ASR', 2, None, 'IND'),
    0x68: ('ASL', 2, None, 'IND'),
    0x69: ('ROL', 2, None, 'IND'),
    0x6A: ('DEC', 2, None, 'IND'),
    0x6C: ('INC', 2, None, 'IND'),
    0x6D: ('TST', 2, None, 'IND'),
    0x6E: ('JMP', 2, None, 'IND'),
    0x6F: ('CLR', 2, None, 'IND'),
    0x70: ('NEG', 3, None, 'EXT'),
    0x73: ('COM', 3, None, 'EXT'),
    0x74: ('LSR', 3, None, 'EXT'),
    0x76: ('ROR', 3, None, 'EXT'),
    0x77: ('ASR', 3, None, 'EXT'),
    0x78: ('ASL', 3, None, 'EXT'),
    0x79: ('ROL', 3, None, 'EXT'),
    0x7A: ('DEC', 3, None, 'EXT'),
    0x7C: ('INC', 3, None, 'EXT'),
    0x7D: ('TST', 3, None, 'EXT'),
    0x7E: ('JMP', 3, None, 'EXT'),
    0x7F: ('CLR', 3, None, 'EXT'),
    0x80: ('SUB', 2, 'A', 'IMM'),
    0x81: ('CMP', 2, 'A', 'IMM'),
    0x82: ('SBC', 2, 'A', 'IMM'),
    0x84: ('AND', 2, 'A', 'IMM'),
    0x85: ('BIT', 2, 'A', 'IMM'),
    0x86: ('LDA', 2, 'A', 'IMM'),
    0x88: ('EOR', 2, 'A', 'IMM'),
    0x89: ('ADC', 2, 'A', 'IMM'),
    0x8A: ('ORA', 2, 'A', 'IMM'),
    0x8B: ('ADD', 2, 'A', 'IMM'),
    0x8C: ('CPX', 3, 'A', 'IMM'),
    0x8D: ('BSR', 2, None, 'REL'),
    0x8E: ('LOS', 2, None, 'IMM'),
    0x90: ('SUB', 2, 'A', 'DIR'),
    0x91: ('CMP', 2, 'A', 'DIR'),
    0x92: ('SBC', 2, 'A', 'DIR'),
    0x94: ('AND', 2, 'A', 'DIR'),
    0x95: ('BIT', 2, 'A', 'DIR'),
    0x96: ('LDA', 2, 'A', 'DIR'),
    0x97: ('STA', 2, 'A', 'DIR'),
    0x98: ('EOR', 2, 'A', 'DIR'),
    0x99: ('ADC', 2, 'A', 'DIR'),
    0x9A: ('ORA', 2, 'A', 'DIR'),
    0x9B: ('ADD', 2, 'A', 'DIR'),
    0x9C: ('CPX', 2, None, 'DIR'),
    0x9E: ('LOS', 2, None, 'DIR'),
    0x9F: ('STS', 2, None, 'DIR'),
    0xA0: ('SUB', 2, 'A', 'IND'),
    0xA1: ('CMP', 2, 'A', 'IND'),
    0xA2: ('SBC', 2, 'A', 'IND'),
    0xA4: ('AND', 2, 'A', 'IND'),
    0xA5: ('BIT', 2, 'A', 'IND'),
    0xA6: ('LDA', 2, 'A', 'IND'),
    0xA7: ('STA', 2, 'A', 'IND'),
    0xA8: ('EOR', 2, 'A', 'IND'),
    0xA9: ('ADC', 2, 'A', 'IND'),
    0xAA: ('ORA', 2, 'A', 'IND'),
    0xAB: ('ADD', 2, 'A', 'IND'),
    0xAC: ('CPX', 2, None, 'IND'),
    0xAD: ('JSR', 2, None, 'IND'),
    0xAE: ('LOS', 2, None, 'IND'),
    0xAF: ('STS', 2, None, 'IND'),
    0xB0: ('SUB', 3, 'A', 'EXT'),
    0xB1: ('CMP', 3, 'A', 'EXT'),
    0xB2: ('SBC', 3, 'A', 'EXT'),
    0xB4: ('AND', 3, 'A', 'EXT'),
    0xB5: ('BIT', 3, 'A', 'EXT'),
    0xB6: ('LDA', 3, 'A', 'EXT'),
    0xB7: ('STA', 3, 'A', 'EXT'),
    0xB8: ('EOR', 3, 'A', 'EXT'),
    0xB9: ('ADC', 3, 'A', 'EXT'),
    0xBA: ('ORA', 3, 'A', 'EXT'),
    0xBB: ('ADD', 3, 'A', 'EXT'),
    0xBC: ('CPX', 3, None, 'EXT'),
    0xBD: ('JSR', 3, None, 'EXT'),
    0xBE: ('LOS', 3, None, 'EXT'),
    0xBF: ('STS', 3, None, 'EXT'),
    0xC0: ('SUB', 2, 'B', 'IMM'),
    0xC1: ('CMP', 2, 'B', 'IMM'),
    0xC2: ('SBC', 2, 'B', 'IMM'),
    0xC4: ('AND', 2, 'B', 'IMM'),
    0xC5: ('BIT', 2, 'B', 'IMM'),
    0xC6: ('LDA', 2, 'B', 'IMM'),
    0xC8: ('EOR', 2, 'B', 'IMM'),
    0xC9: ('ADC', 2, 'B', 'IMM'),
    0xCA: ('ORA', 2, 'B', 'IMM'),
    0xCB: ('ADD', 2, 'B', 'IMM'),
    0xCE: ('LDX', 3, None, 'IMM'),
    0xD0: ('SUB', 2, 'B', 'DIR'),
    0xD1: ('CMP', 2, 'B', 'DIR'),
    0xD2: ('SBC', 2, 'B', 'DIR'),
    0xD4: ('AND', 2, 'B', 'DIR'),
    0xD5: ('BIT', 2, 'B', 'DIR'),
    0xD6: ('LDA', 2, 'B', 'DIR'),
    0xD7: ('STA', 2, 'B', 'DIR'),
    0xD8: ('EOR', 2, 'B', 'DIR'),
    0xD9: ('ADC', 2, 'B', 'DIR'),
    0xDA: ('ORA', 2, 'B', 'DIR'),
    0xDB: ('ADD', 2, 'B', 'DIR'),
    0xDE: ('LDX', 2, None, 'DIR'),
    0xDF: ('STX', 2, None, 'DIR'),
    0xE0: ('SUB', 2, 'B', 'IND'),
    0xE1: ('CMP', 2, 'B', 'IND'),
    0xE2: ('SBC', 2, 'B', 'IND'),
    0xE4: ('AND', 2, 'B', 'IND'),
    0xE5: ('BIT', 2, 'B', 'IND'),
    0xE6: ('LDA', 2, 'B', 'IND'),
    0xE7: ('STA', 2, 'B', 'IND'),
    0xE8: ('EOR', 2, 'B', 'IND'),
    0xE9: ('ADC', 2, 'B', 'IND'),
    0xEA: ('ORA', 2, 'B', 'IND'),
    0xEB: ('ADD', 2, 'B', 'IND'),
    0xEE: ('LDX', 2, None, 'IND'),
    0xEF: ('STX', 2, None, 'IND'),
    0xF0: ('SUB', 3, 'B', 'EXT'),
    0xF1: ('CMP', 3, 'B', 'EXT'),
    0xF2: ('SBC', 3, 'B', 'EXT'),
    0xF4: ('AND', 3, 'B', 'EXT'),
    0xF5: ('BIT', 3, 'B', 'EXT'),
    0xF6: ('LDA', 3, 'B', 'EXT'),
    0xF7: ('STA', 3, 'B', 'EXT'),
    0xF8: ('ADC', 3, 'B', 'EXT'),
    0xF9: ('ADC', 3, 'B', 'EXT'),
    0xFA: ('ORA', 3, 'B', 'EXT'),
    0xFB: ('ADD', 3, 'B', 'EXT'),
    0xFE: ('LDX', 3, None, 'EXT'),
    0xFF: ('STX', 3, None, 'EXT')
}
