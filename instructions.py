'''File containing all instructions for the M6800 assembly language.'''

from enum import IntEnum

from binaryninja import LowLevelILFlagCondition

# USE THIS VARIABLE TO SET YOUR MAX ADDRESS SPACE
ADDRESS_MASK = 0x7FFF


class AddressMode(IntEnum):
    '''All of the various addressing modes for the M6800'''
    ACCUMULATOR = 0     # ACCA or ACCB
    IMMEDIATE = 1       # (0-65535)
    DIRECT = 2          # [(0-255)]
    EXTENDED = 3        # [(0-65535)]
    INDEXED = 4         # [IX + (0-255)]
    IMPLIED = 5         # inherent to the instruction
    RELATIVE = 6        # [addr + 2 + (0-255)]


class InstructionType(IntEnum):
    '''All of the various instruction types for the M6800'''
    CONDITIONAL_BRANCH = 0      # sometimes jump
    UNCONDITIONAL_BRANCH = 1    # always jump
    CALL = 2                    # call subroutine
    RETURN = 3                  # return from subroutine
    NOP = 4                     # no-op
    DUAL = 5                    # instructions that have dual operands


INSTRUCTIONS = {
    # Opcode: (mnemonic, length, operand, instruction type, address mode)
    0x01: ('NOP', 1, None, InstructionType.NOP, AddressMode.IMPLIED),
    0x06: ('TAP', 1, 'Flags', None, AddressMode.IMPLIED),
    0x07: ('TPA', 1, 'Flags', None, AddressMode.IMPLIED),
    0x08: ('INX', 1, 'IX', None, AddressMode.IMPLIED),
    0x09: ('DEX', 1, 'IX', None, AddressMode.IMPLIED),
    0x0A: ('CLV', 1, 'V', None, AddressMode.IMPLIED),
    0x0B: ('SEV', 1, 'V', None, AddressMode.IMPLIED),
    0x0C: ('CLC', 1, 'C', None, AddressMode.IMPLIED),
    0x0D: ('SEC', 1, 'C', None, AddressMode.IMPLIED),
    0x0E: ('CLI', 1, 'I', None, AddressMode.IMPLIED),
    0x0F: ('SEI', 1, 'I', None, AddressMode.IMPLIED),
    0x10: ('SBA', 1, 'BA', None, AddressMode.IMPLIED),
    0x11: ('CBA', 1, 'AB', None, AddressMode.IMPLIED),
    0x16: ('TAB', 1, 'AB', None, AddressMode.IMPLIED),
    0x17: ('TBA', 1, 'BA', None, AddressMode.IMPLIED),
    0x19: ('DAA', 1, 'ACCA', None, AddressMode.IMPLIED),
    0x1B: ('ABA', 1, 'BA', None, AddressMode.IMPLIED),
    0x20: ('BRA', 2, None, InstructionType.UNCONDITIONAL_BRANCH, AddressMode.RELATIVE),
    0x22: ('BHI', 2, None, InstructionType.CONDITIONAL_BRANCH, AddressMode.RELATIVE),
    0x23: ('BLS', 2, None, InstructionType.CONDITIONAL_BRANCH, AddressMode.RELATIVE),
    0x24: ('BCC', 2, None, InstructionType.CONDITIONAL_BRANCH, AddressMode.RELATIVE),
    0x25: ('BCS', 2, None, InstructionType.CONDITIONAL_BRANCH, AddressMode.RELATIVE),
    0x26: ('BNE', 2, None, InstructionType.CONDITIONAL_BRANCH, AddressMode.RELATIVE),
    0x27: ('BEQ', 2, None, InstructionType.CONDITIONAL_BRANCH, AddressMode.RELATIVE),
    0x28: ('BVC', 2, None, InstructionType.CONDITIONAL_BRANCH, AddressMode.RELATIVE),
    0x29: ('BVS', 2, None, InstructionType.CONDITIONAL_BRANCH, AddressMode.RELATIVE),
    0x2A: ('BPL', 2, None, InstructionType.CONDITIONAL_BRANCH, AddressMode.RELATIVE),
    0x2B: ('BMI', 2, None, InstructionType.CONDITIONAL_BRANCH, AddressMode.RELATIVE),
    0x2C: ('BGE', 2, None, InstructionType.CONDITIONAL_BRANCH, AddressMode.RELATIVE),
    0x2D: ('BLT', 2, None, InstructionType.CONDITIONAL_BRANCH, AddressMode.RELATIVE),
    0x2E: ('BGT', 2, None, InstructionType.CONDITIONAL_BRANCH, AddressMode.RELATIVE),
    0x2F: ('BLE', 2, None, InstructionType.CONDITIONAL_BRANCH, AddressMode.RELATIVE),
    0x30: ('TSX', 1, 'SX', None, AddressMode.IMPLIED),
    0x31: ('INS', 1, 'SP', None, AddressMode.IMPLIED),
    0x32: ('PUL', 1, 'ACCA', None, AddressMode.ACCUMULATOR),
    0x33: ('PUL', 1, 'ACCB', None, AddressMode.ACCUMULATOR),
    0x34: ('DES', 1, 'SP', None, AddressMode.IMPLIED),
    0x35: ('TXS', 1, 'XS', None, AddressMode.IMPLIED),
    0x36: ('PSH', 1, 'ACCA', None, AddressMode.ACCUMULATOR),
    0x37: ('PSH', 1, 'ACCB', None, AddressMode.ACCUMULATOR),
    0x39: ('RTS', 1, None, InstructionType.RETURN, AddressMode.IMPLIED),
    0x3B: ('RTI', 1, None, None, AddressMode.IMPLIED),
    0x3E: ('WAI', 1, None, None, AddressMode.IMPLIED),
    0x3F: ('SWI', 1, None, None, AddressMode.IMPLIED),
    0x40: ('NEG', 1, 'ACCA', None, AddressMode.ACCUMULATOR),
    0x43: ('COM', 1, 'ACCA', None, AddressMode.ACCUMULATOR),
    0x44: ('LSR', 1, 'ACCA', None, AddressMode.ACCUMULATOR),
    0x46: ('ROR', 1, 'ACCA', None, AddressMode.ACCUMULATOR),
    0x47: ('ASR', 1, 'ACCA', None, AddressMode.ACCUMULATOR),
    0x48: ('ASL', 1, 'ACCA', None, AddressMode.ACCUMULATOR),
    0x49: ('ROL', 1, 'ACCA', None, AddressMode.ACCUMULATOR),
    0x4A: ('DEC', 1, 'ACCA', None, AddressMode.ACCUMULATOR),
    0x4C: ('INC', 1, 'ACCA', None, AddressMode.ACCUMULATOR),
    0x4D: ('TST', 1, 'ACCA', None, AddressMode.ACCUMULATOR),
    0x4F: ('CLR', 1, 'ACCA', None, AddressMode.ACCUMULATOR),
    0x50: ('NEG', 1, 'ACCB', None, AddressMode.ACCUMULATOR),
    0x53: ('COM', 1, 'ACCB', None, AddressMode.ACCUMULATOR),
    0x54: ('LSR', 1, 'ACCB', None, AddressMode.ACCUMULATOR),
    0x56: ('ROR', 1, 'ACCB', None, AddressMode.ACCUMULATOR),
    0x57: ('ASR', 1, 'ACCB', None, AddressMode.ACCUMULATOR),
    0x58: ('ASL', 1, 'ACCB', None, AddressMode.ACCUMULATOR),
    0x59: ('ROL', 1, 'ACCB', None, AddressMode.ACCUMULATOR),
    0x5A: ('DEC', 1, 'ACCB', None, AddressMode.ACCUMULATOR),
    0x5C: ('INC', 1, 'ACCB', None, AddressMode.ACCUMULATOR),
    0x5D: ('TST', 1, 'ACCB', None, AddressMode.ACCUMULATOR),
    0x5F: ('CLR', 1, 'ACCB', None, AddressMode.ACCUMULATOR),
    0x60: ('NEG', 2, None, None, AddressMode.INDEXED),
    0x63: ('COM', 2, None, None, AddressMode.INDEXED),
    0x64: ('LSR', 2, None, None, AddressMode.INDEXED),
    0x66: ('ROR', 2, None, None, AddressMode.INDEXED),
    0x67: ('ASR', 2, None, None, AddressMode.INDEXED),
    0x68: ('ASL', 2, None, None, AddressMode.INDEXED),
    0x69: ('ROL', 2, None, None, AddressMode.INDEXED),
    0x6A: ('DEC', 2, None, None, AddressMode.INDEXED),
    0x6C: ('INC', 2, None, None, AddressMode.INDEXED),
    0x6D: ('TST', 2, None, None, AddressMode.INDEXED),
    0x6E: ('JMP', 2, None, InstructionType.UNCONDITIONAL_BRANCH, AddressMode.INDEXED),
    0x6F: ('CLR', 2, None, None, AddressMode.INDEXED),
    0x70: ('NEG', 3, None, None, AddressMode.EXTENDED),
    0x73: ('COM', 3, None, None, AddressMode.EXTENDED),
    0x74: ('LSR', 3, None, None, AddressMode.EXTENDED),
    0x76: ('ROR', 3, None, None, AddressMode.EXTENDED),
    0x77: ('ASR', 3, None, None, AddressMode.EXTENDED),
    0x78: ('ASL', 3, None, None, AddressMode.EXTENDED),
    0x79: ('ROL', 3, None, None, AddressMode.EXTENDED),
    0x7A: ('DEC', 3, None, None, AddressMode.EXTENDED),
    0x7C: ('INC', 3, None, None, AddressMode.EXTENDED),
    0x7D: ('TST', 3, None, None, AddressMode.EXTENDED),
    0x7E: ('JMP', 3, None, InstructionType.UNCONDITIONAL_BRANCH, AddressMode.EXTENDED),
    0x7F: ('CLR', 3, None, None, AddressMode.EXTENDED),
    0x80: ('SUB', 2, 'ACCA', InstructionType.DUAL, AddressMode.IMMEDIATE),
    0x81: ('CMP', 2, 'ACCA', InstructionType.DUAL, AddressMode.IMMEDIATE),
    0x82: ('SBC', 2, 'ACCA', InstructionType.DUAL, AddressMode.IMMEDIATE),
    0x84: ('AND', 2, 'ACCA', InstructionType.DUAL, AddressMode.IMMEDIATE),
    0x85: ('BIT', 2, 'ACCA', InstructionType.DUAL, AddressMode.IMMEDIATE),
    0x86: ('LDA', 2, 'ACCA', InstructionType.DUAL, AddressMode.IMMEDIATE),
    0x88: ('EOR', 2, 'ACCA', InstructionType.DUAL, AddressMode.IMMEDIATE),
    0x89: ('ADC', 2, 'ACCA', InstructionType.DUAL, AddressMode.IMMEDIATE),
    0x8A: ('ORA', 2, 'ACCA', InstructionType.DUAL, AddressMode.IMMEDIATE),
    0x8B: ('ADD', 2, 'ACCA', InstructionType.DUAL, AddressMode.IMMEDIATE),
    0x8C: ('CPX', 3, None, None, AddressMode.IMMEDIATE),
    0x8D: ('BSR', 2, None, InstructionType.CALL, AddressMode.RELATIVE),
    0x8E: ('LDS', 2, None, None, AddressMode.IMMEDIATE),
    0x90: ('SUB', 2, 'ACCA', InstructionType.DUAL, AddressMode.DIRECT),
    0x91: ('CMP', 2, 'ACCA', InstructionType.DUAL, AddressMode.DIRECT),
    0x92: ('SBC', 2, 'ACCA', InstructionType.DUAL, AddressMode.DIRECT),
    0x94: ('AND', 2, 'ACCA', InstructionType.DUAL, AddressMode.DIRECT),
    0x95: ('BIT', 2, 'ACCA', InstructionType.DUAL, AddressMode.DIRECT),
    0x96: ('LDA', 2, 'ACCA', InstructionType.DUAL, AddressMode.DIRECT),
    0x97: ('STA', 2, 'ACCA', InstructionType.DUAL, AddressMode.DIRECT),
    0x98: ('EOR', 2, 'ACCA', InstructionType.DUAL, AddressMode.DIRECT),
    0x99: ('ADC', 2, 'ACCA', InstructionType.DUAL, AddressMode.DIRECT),
    0x9A: ('ORA', 2, 'ACCA', InstructionType.DUAL, AddressMode.DIRECT),
    0x9B: ('ADD', 2, 'ACCA', InstructionType.DUAL, AddressMode.DIRECT),
    0x9C: ('CPX', 2, None, None, AddressMode.DIRECT),
    0x9E: ('LDS', 2, None, None, AddressMode.DIRECT),
    0x9F: ('STS', 2, None, None, AddressMode.DIRECT),
    0xA0: ('SUB', 2, 'ACCA', InstructionType.DUAL, AddressMode.INDEXED),
    0xA1: ('CMP', 2, 'ACCA', InstructionType.DUAL, AddressMode.INDEXED),
    0xA2: ('SBC', 2, 'ACCA', InstructionType.DUAL, AddressMode.INDEXED),
    0xA4: ('AND', 2, 'ACCA', InstructionType.DUAL, AddressMode.INDEXED),
    0xA5: ('BIT', 2, 'ACCA', InstructionType.DUAL, AddressMode.INDEXED),
    0xA6: ('LDA', 2, 'ACCA', InstructionType.DUAL, AddressMode.INDEXED),
    0xA7: ('STA', 2, 'ACCA', InstructionType.DUAL, AddressMode.INDEXED),
    0xA8: ('EOR', 2, 'ACCA', InstructionType.DUAL, AddressMode.INDEXED),
    0xA9: ('ADC', 2, 'ACCA', InstructionType.DUAL, AddressMode.INDEXED),
    0xAA: ('ORA', 2, 'ACCA', InstructionType.DUAL, AddressMode.INDEXED),
    0xAB: ('ADD', 2, 'ACCA', InstructionType.DUAL, AddressMode.INDEXED),
    0xAC: ('CPX', 2, None, None, AddressMode.INDEXED),
    0xAD: ('JSR', 2, None, InstructionType.CALL, AddressMode.INDEXED),
    0xAE: ('LDS', 2, None, None, AddressMode.INDEXED),
    0xAF: ('STS', 2, None, None, AddressMode.INDEXED),
    0xB0: ('SUB', 3, 'ACCA', InstructionType.DUAL, AddressMode.EXTENDED),
    0xB1: ('CMP', 3, 'ACCA', InstructionType.DUAL, AddressMode.EXTENDED),
    0xB2: ('SBC', 3, 'ACCA', InstructionType.DUAL, AddressMode.EXTENDED),
    0xB4: ('AND', 3, 'ACCA', InstructionType.DUAL, AddressMode.EXTENDED),
    0xB5: ('BIT', 3, 'ACCA', InstructionType.DUAL, AddressMode.EXTENDED),
    0xB6: ('LDA', 3, 'ACCA', InstructionType.DUAL, AddressMode.EXTENDED),
    0xB7: ('STA', 3, 'ACCA', InstructionType.DUAL, AddressMode.EXTENDED),
    0xB8: ('EOR', 3, 'ACCA', InstructionType.DUAL, AddressMode.EXTENDED),
    0xB9: ('ADC', 3, 'ACCA', InstructionType.DUAL, AddressMode.EXTENDED),
    0xBA: ('ORA', 3, 'ACCA', InstructionType.DUAL, AddressMode.EXTENDED),
    0xBB: ('ADD', 3, 'ACCA', InstructionType.DUAL, AddressMode.EXTENDED),
    0xBC: ('CPX', 3, None, None, AddressMode.EXTENDED),
    0xBD: ('JSR', 3, None, InstructionType.CALL, AddressMode.EXTENDED),
    0xBE: ('LDS', 3, None, None, AddressMode.EXTENDED),
    0xBF: ('STS', 3, None, None, AddressMode.EXTENDED),
    0xC0: ('SUB', 2, 'ACCB', InstructionType.DUAL, AddressMode.IMMEDIATE),
    0xC1: ('CMP', 2, 'ACCB', InstructionType.DUAL, AddressMode.IMMEDIATE),
    0xC2: ('SBC', 2, 'ACCB', InstructionType.DUAL, AddressMode.IMMEDIATE),
    0xC4: ('AND', 2, 'ACCB', InstructionType.DUAL, AddressMode.IMMEDIATE),
    0xC5: ('BIT', 2, 'ACCB', InstructionType.DUAL, AddressMode.IMMEDIATE),
    0xC6: ('LDA', 2, 'ACCB', InstructionType.DUAL, AddressMode.IMMEDIATE),
    0xC8: ('EOR', 2, 'ACCB', InstructionType.DUAL, AddressMode.IMMEDIATE),
    0xC9: ('ADC', 2, 'ACCB', InstructionType.DUAL, AddressMode.IMMEDIATE),
    0xCA: ('ORA', 2, 'ACCB', InstructionType.DUAL, AddressMode.IMMEDIATE),
    0xCB: ('ADD', 2, 'ACCB', InstructionType.DUAL, AddressMode.IMMEDIATE),
    0xCE: ('LDX', 3, None, None, AddressMode.IMMEDIATE),
    0xD0: ('SUB', 2, 'ACCB', InstructionType.DUAL, AddressMode.DIRECT),
    0xD1: ('CMP', 2, 'ACCB', InstructionType.DUAL, AddressMode.DIRECT),
    0xD2: ('SBC', 2, 'ACCB', InstructionType.DUAL, AddressMode.DIRECT),
    0xD4: ('AND', 2, 'ACCB', InstructionType.DUAL, AddressMode.DIRECT),
    0xD5: ('BIT', 2, 'ACCB', InstructionType.DUAL, AddressMode.DIRECT),
    0xD6: ('LDA', 2, 'ACCB', InstructionType.DUAL, AddressMode.DIRECT),
    0xD7: ('STA', 2, 'ACCB', InstructionType.DUAL, AddressMode.DIRECT),
    0xD8: ('EOR', 2, 'ACCB', InstructionType.DUAL, AddressMode.DIRECT),
    0xD9: ('ADC', 2, 'ACCB', InstructionType.DUAL, AddressMode.DIRECT),
    0xDA: ('ORA', 2, 'ACCB', InstructionType.DUAL, AddressMode.DIRECT),
    0xDB: ('ADD', 2, 'ACCB', InstructionType.DUAL, AddressMode.DIRECT),
    0xDE: ('LDX', 2, None, None, AddressMode.DIRECT),
    0xDF: ('STX', 2, None, None, AddressMode.DIRECT),
    0xE0: ('SUB', 2, 'ACCB', InstructionType.DUAL, AddressMode.INDEXED),
    0xE1: ('CMP', 2, 'ACCB', InstructionType.DUAL, AddressMode.INDEXED),
    0xE2: ('SBC', 2, 'ACCB', InstructionType.DUAL, AddressMode.INDEXED),
    0xE4: ('AND', 2, 'ACCB', InstructionType.DUAL, AddressMode.INDEXED),
    0xE5: ('BIT', 2, 'ACCB', InstructionType.DUAL, AddressMode.INDEXED),
    0xE6: ('LDA', 2, 'ACCB', InstructionType.DUAL, AddressMode.INDEXED),
    0xE7: ('STA', 2, 'ACCB', InstructionType.DUAL, AddressMode.INDEXED),
    0xE8: ('EOR', 2, 'ACCB', InstructionType.DUAL, AddressMode.INDEXED),
    0xE9: ('ADC', 2, 'ACCB', InstructionType.DUAL, AddressMode.INDEXED),
    0xEA: ('ORA', 2, 'ACCB', InstructionType.DUAL, AddressMode.INDEXED),
    0xEB: ('ADD', 2, 'ACCB', InstructionType.DUAL, AddressMode.INDEXED),
    0xEE: ('LDX', 2, None, None, AddressMode.INDEXED),
    0xEF: ('STX', 2, None, None, AddressMode.INDEXED),
    0xF0: ('SUB', 3, 'ACCB', InstructionType.DUAL, AddressMode.EXTENDED),
    0xF1: ('CMP', 3, 'ACCB', InstructionType.DUAL, AddressMode.EXTENDED),
    0xF2: ('SBC', 3, 'ACCB', InstructionType.DUAL, AddressMode.EXTENDED),
    0xF4: ('AND', 3, 'ACCB', InstructionType.DUAL, AddressMode.EXTENDED),
    0xF5: ('BIT', 3, 'ACCB', InstructionType.DUAL, AddressMode.EXTENDED),
    0xF6: ('LDA', 3, 'ACCB', InstructionType.DUAL, AddressMode.EXTENDED),
    0xF7: ('STA', 3, 'ACCB', InstructionType.DUAL, AddressMode.EXTENDED),
    0xF8: ('ADC', 3, 'ACCB', InstructionType.DUAL, AddressMode.EXTENDED),
    0xF9: ('ADC', 3, 'ACCB', InstructionType.DUAL, AddressMode.EXTENDED),
    0xFA: ('ORA', 3, 'ACCB', InstructionType.DUAL, AddressMode.EXTENDED),
    0xFB: ('ADD', 3, 'ACCB', InstructionType.DUAL, AddressMode.EXTENDED),
    0xFE: ('LDX', 3, None, None, AddressMode.EXTENDED),
    0xFF: ('STX', 3, None, None, AddressMode.EXTENDED),
}

# These instructions operate on a word, not a byte
BIGGER_LOADS = ['CPX', 'LDS', 'LDX']

# These instructions have different possibilities for destinations
REGISTER_OR_MEMORY_DESTINATIONS = [
    'ASL', 'ASR', 'CLR', 'COM', 'DEC', 'INC', 'LSR', 'NEG', 'ROL', 'ROR'
]

LLIL_OPERATIONS = {
    'ABA': lambda il, op_1, op_2: il.set_reg(
        1,
        'ACCA',
        il.add(
            1,
            il.reg(1, 'ACCA'),
            il.reg(1, 'ACCB'),
            flags='HNZVC'
        )
    ),
    'ADC': lambda il, op_1, op_2: il.set_reg(
        1,
        op_2,
        il.add_carry(
            1,
            il.reg(1, op_2),
            op_1,
            il.flag('C'),
            flags='HNZVC'
        )
    ),
    'ADD': lambda il, op_1, op_2: il.set_reg(
        1,
        op_2,
        il.add(
            1,
            il.reg(1, op_2),
            op_1,
            flags='HNZVC'
        )
    ),
    'AND': lambda il, op_1, op_2: il.set_reg(
        1,
        op_2,
        il.and_expr(
            1,
            il.reg(1, op_2),
            op_1,
            flags='NZV'
        )
    ),
    'ASL': lambda il, op_1, op_2: il.shift_left(
        1,
        op_1,
        il.const(1, 1),
        flags='NZVC'
    ),
    'ASR': lambda il, op_1, op_2: il.arith_shift_right(
        1,
        op_1,
        il.const(1, 1),
        flags='NZVC'
    ),
    'BCC': lambda il, op_1, op_2: il.flag_condition(
        LowLevelILFlagCondition.LLFC_UGE
    ),
    'BCS': lambda il, op_1, op_2: il.flag_condition(
        LowLevelILFlagCondition.LLFC_ULT
    ),
    'BEQ': lambda il, op_1, op_2: il.flag_condition(
        LowLevelILFlagCondition.LLFC_E
    ),
    'BGE': lambda il, op_1, op_2: il.flag_condition(
        LowLevelILFlagCondition.LLFC_SGE
    ),
    'BGT': lambda il, op_1, op_2: il.flag_condition(
        LowLevelILFlagCondition.LLFC_SGT
    ),
    'BHI': lambda il, op_1, op_2: il.flag_condition(
        LowLevelILFlagCondition.LLFC_UGT
    ),
    'BIT': lambda il, op_1, op_2: il.and_expr(
        1,
        il.reg(1, op_2),
        op_1,
        flags='NZV'
    ),
    'BLE': lambda il, op_1, op_2: il.flag_condition(
        LowLevelILFlagCondition.LLFC_SLE
    ),
    'BLS': lambda il, op_1, op_2: il.flag_condition(
        LowLevelILFlagCondition.LLFC_ULE
    ),
    'BLT': lambda il, op_1, op_2: il.flag_condition(
        LowLevelILFlagCondition.LLFC_ULT
    ),
    'BMI': lambda il, op_1, op_2: il.flag_condition(
        LowLevelILFlagCondition.LLFC_NEG
    ),
    'BNE': lambda il, op_1, op_2: il.flag_condition(
        LowLevelILFlagCondition.LLFC_NE
    ),
    'BPL': lambda il, op_1, op_2: il.flag_condition(
        LowLevelILFlagCondition.LLFC_POS
    ),
    # implemented in _handle_jump
    'BRA': lambda il, op_1, op_2: il.unimplemented(),
    'BSR': lambda il, op_1, op_2: il.call(op_1),
    'BVC': lambda il, op_1, op_2: il.flag_condition(
        LowLevelILFlagCondition.LLFC_NO
    ),
    'BVS': lambda il, op_1, op_2: il.flag_condition(
        LowLevelILFlagCondition.LLFC_O
    ),
    'CBA': lambda il, op_1, op_2: il.sub(
        1,
        il.reg(1, 'ACCA'),
        il.reg(1, 'ACCB'),
        flags='NZVC'
    ),
    'CLC': lambda il, op_1, op_2: il.flag_bit(1, 'C', 0),
    'CLI': lambda il, op_1, op_2: il.flag_bit(1, 'I', 0),
    'CLR': lambda il, op_1, op_2: il.and_expr(
        1,
        op_1,
        il.const(1, 0),
        flags='NZVC'
    ),
    'CLV': lambda il, op_1, op_2: il.flag_bit(1, 'V', 0),
    'CMP': lambda il, op_1, op_2: il.sub(
        1,
        il.reg(1, op_2),
        op_1,
        flags='NZVC'
    ),
    'COM': lambda il, op_1, op_2: il.not_expr(
        1,
        op_1,
        flags='NZVC'
    ),
    'CPX': lambda il, op_1, op_2: il.sub(
        2,
        il.reg(2, 'IX'),
        op_1,
        flags='NZV'
    ),
    # TODO: not really sure how to tackle this instruction...
    'DAA': lambda il, op_1, op_2: il.unimplemented(),
    'DEC': lambda il, op_1, op_2: il.sub(
        1,
        op_1,
        il.const(1, 1),
        flags='NZV'
    ),
    'DES': lambda il, op_1, op_2: il.set_reg(
        2,
        'SP',
        il.sub(
            2,
            il.reg(2, 'SP'),
            il.const(2, 1)
        )
    ),
    'DEX': lambda il, op_1, op_2: il.set_reg(
        2,
        'IX',
        il.sub(
            2,
            il.reg(2, 'IX'),
            il.const(2, 1),
            flags='Z'
        )
    ),
    'EOR': lambda il, op_1, op_2: il.set_reg(
        1,
        op_2,
        il.xor_expr(
            1,
            il.reg(1, op_2),
            op_1,
            flags='NZV'
        )
    ),
    'INC': lambda il, op_1, op_2: il.add(
        1,
        op_1,
        il.const(1, 1),
        flags='NZV'
    ),
    'INS': lambda il, op_1, op_2: il.set_reg(
        2,
        'SP',
        il.add(
            2,
            il.reg(2, 'SP'),
            il.const(2, 1)
        )
    ),
    'INX': lambda il, op_1, op_2: il.set_reg(
        2,
        'IX',
        il.add(
            2,
            il.reg(2, 'IX'),
            il.const(2, 1),
            flags='Z'
        )
    ),
    # implemented in _handle_jump
    'JMP': lambda il, op_1, op_2: il.unimplemented(),
    'JSR': lambda il, op_1, op_2: il.call(op_1),
    'LDA': lambda il, op_1, op_2: il.set_reg(
        1,
        op_2,
        op_1,
        flags='NZV'
    ),
    'LDS': lambda il, op_1, op_2: il.set_reg(
        2,
        'SP',
        op_1,
        flags='NZV'
    ),
    'LDX': lambda il, op_1, op_2: il.set_reg(
        2,
        'IX',
        op_1,
        flags='NZV'
    ),
    'LSR': lambda il, op_1, op_2: il.logical_shift_right(
        1,
        op_1,
        il.const(1, 1),
        flags='NZVC'
    ),
    'NEG': lambda il, op_1, op_2: il.neg_expr(
        1,
        op_1,
        flags='NZVC'
    ),
    'NOP': lambda il, op_1, op_2: il.nop(),
    'ORA': lambda il, op_1, op_2: il.set_reg(
        1,
        op_2,
        il.or_expr(
            1,
            il.reg(1, op_2),
            op_1,
            flags='NZV'
        )
    ),
    'PSH': lambda il, op_1, op_2: il.push(
        1,
        op_1
    ),
    'PUL': lambda il, op_1, op_2: il.set_reg(
        1,
        op_1,
        il.pop(1)
    ),
    'ROL': lambda il, op_1, op_2: il.rotate_left_carry(
        1,
        op_1,
        il.const(1, 1),
        il.flag('C'),
        flags='NZVC'
    ),
    'ROR': lambda il, op_1, op_2: il.rotate_right_carry(
        1,
        op_1,
        il.const(1, 1),
        il.flag('C'),
        flags='NZVC'
    ),
    # TODO: figure out how to handle interrupts
    'RTI': lambda il, op_1, op_2: il.unimplemented(),
    'RTS': lambda il, op_1, op_2: il.ret(il.pop(2)),
    'SBA': lambda il, op_1, op_2: il.set_reg(
        1,
        'ACCA',
        il.sub(
            1,
            il.reg(1, 'ACCA'),
            il.reg(1, 'ACCB'),
            flags='NZVC'
        )
    ),
    'SBC': lambda il, op_1, op_2: il.set_reg(
        1,
        op_2,
        il.sub_borrow(
            1,
            il.reg(1, op_2),
            op_1,
            il.flag('C'),
            flags='NZVC'
        )
    ),
    'SEC': lambda il, op_1, op_2: il.flag_bit(1, 'C', 0),
    'SEI': lambda il, op_1, op_2: il.flag_bit(1, 'I', 0),
    'SEV': lambda il, op_1, op_2: il.flag_bit(1, 'V', 0),
    'STA': lambda il, op_1, op_2: il.store(
        1,
        op_1,
        il.reg(1, op_2),
        flags='NZV'
    ),
    'STS': lambda il, op_1, op_2: il.store(
        2,
        op_1,
        il.reg(2, 'SP'),
        flags='NZV'
    ),
    'STX': lambda il, op_1, op_2: il.store(
        2,
        op_1,
        il.reg(2, 'IX'),
        flags='NZV'
    ),
    'SUB': lambda il, op_1, op_2: il.set_reg(
        1,
        op_2,
        il.sub(
            1,
            il.reg(1, op_2),
            op_1
        )
    ),
    'SWI': lambda il, op_1, op_2: il.unimplemented(),
    'TAB': lambda il, op_1, op_2: il.set_reg(
        1,
        'ACCB',
        il.reg(1, 'ACCA'),
        flags='NZV'
    ),
    'TAP': lambda il, op_1, op_2: il.unimplemented(),
    'TBA': lambda il, op_1, op_2: il.set_reg(
        1,
        'ACCA',
        il.reg(1, 'ACCB'),
        flags='NZV'
    ),
    'TPA': lambda il, op_1, op_2: il.unimplemented(),
    'TST': lambda il, op_1, op_2: il.sub(
        1,
        op_1,
        il.const(1, 0),
        flags='NZVC'
    ),
    'TSX': lambda il, op_1, op_2: il.set_reg(
        2,
        'IX',
        il.add(
            2,
            il.reg(2, 'SP'),
            il.const(2, 1)
        )
    ),
    'TXS': lambda il, op_1, op_2: il.set_reg(
        2,
        'SP',
        il.sub(
            2,
            il.reg(2, 'IX'),
            il.const(2, 1)
        )
    ),
    'WAI': lambda il, op_1, op_2: il.unimplemented()
}
