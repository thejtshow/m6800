'''Binary Ninja architecture for the Motorola M6800 processor'''
import struct

from binaryninja import (
    Architecture, RegisterInfo, FlagRole, LowLevelILFlagCondition, log_error, InstructionTextToken,
    InstructionTextTokenType as ITTT, InstructionInfo, BranchType
)

# pylint: disable=wildcard-import
from .instructions import *


# pylint: disable=abstract-method
class M6800(Architecture):
    '''M6800 Architecture class.'''
    name = 'M6800'
    address_size = 2
    default_int_size = 2

    regs = {
        'SP': RegisterInfo('SP', 2),        # Stack Pointer
        'PC': RegisterInfo('PC', 2),        # Program Counter
        'IX': RegisterInfo('IX', 2),        # Index Register
        'ACCA': RegisterInfo('ACCA', 1),    # Accumulator A
        'ACCB': RegisterInfo('ACCB', 1)     # Accumulator B
    }

    flags = ['C', 'V', 'Z', 'N', 'I', 'H']

    flag_roles = {
        'C': FlagRole.CarryFlagRole,
        'V': FlagRole.OverflowFlagRole,
        'Z': FlagRole.ZeroFlagRole,
        'N': FlagRole.NegativeSignFlagRole,
        'I': FlagRole.SpecialFlagRole,      # Interrupt Flag
        'H': FlagRole.HalfCarryFlagRole     # may be able to ignore -- no branch uses it
    }

    flags_required_for_flag_condition = {
        LowLevelILFlagCondition.LLFC_UGE: ['C'],
        LowLevelILFlagCondition.LLFC_UGT: ['C', 'Z'],
        LowLevelILFlagCondition.LLFC_ULT: ['C'],
        LowLevelILFlagCondition.LLFC_SGE: ['N', 'V'],
        LowLevelILFlagCondition.LLFC_SLT: ['N', 'V'],
        LowLevelILFlagCondition.LLFC_SGT: ['Z', 'N', 'V'],
        LowLevelILFlagCondition.LLFC_E: ['Z'],
        LowLevelILFlagCondition.LLFC_NE: ['Z'],
        LowLevelILFlagCondition.LLFC_NEG: ['N'],
        LowLevelILFlagCondition.LLFC_POS: ['N']
    }

    stack_pointer = 'SP'

    @staticmethod
    def _decode_instruction(data, addr):
        opcode = data[0]
        try:
            nmemonic, inst_length, accumulator, inst_type, mode = INSTRUCTIONS[opcode]
        except KeyError:
            raise LookupError(f'Opcode 0x{opcode:X} at address 0x{addr:X} is invalid.')

        value = None

        # need to collect information based on each address mode
        # INHERENT addressing => value is None
        # ACCUMULATOR addressing => value is in accumulator
        if mode == AddressMode.RELATIVE:
            # should always be 2 bytes long, second byte is 2's complement
            value = addr + inst_length + data[1].to_bytes(1, 'big', signed=True)
        elif mode == AddressMode.IMMEDIATE:
            if inst_length == 2:
                value = data[1]
            else:
                value = struct.unpack('>H', data[1:3])[0]
        elif mode == AddressMode.EXTENDED:
            value = struct.unpack('>H', data[1:3])[0]
        elif mode in [AddressMode.INDEXED,
                      AddressMode.DIRECT]:
            value = data[1]

        return nmemonic, inst_length, accumulator, inst_type, mode, value

    def get_instruction_text(self, data, addr):
        try:
            (nmemonic, inst_length, accumulator,
             _, mode, value) = M6800._decode_instruction(data, addr)
        except LookupError as error:
            log_error(error.__str__())
            return None

        tokens = [
            InstructionTextToken(ITTT.InstructionToken, nmemonic)
        ]

        if mode == AddressMode.ACCUMULATOR:
            tokens.append(InstructionTextToken(ITTT.OperandSeparatorToken, ' '))
            tokens.append(InstructionTextToken(ITTT.RegisterToken, accumulator))
        elif mode in [AddressMode.DIRECT, AddressMode.EXTENDED, AddressMode.RELATIVE]:
            tokens.append(InstructionTextToken(ITTT.OperandSeparatorToken, ' '))
            tokens.append(InstructionTextToken(ITTT.BeginMemoryOperandToken, '['))
            tokens.append(InstructionTextToken(ITTT.PossibleAddressToken, f'0x{value:X}', value))
            tokens.append(InstructionTextToken(ITTT.EndMemoryOperandToken, ']'))
        elif mode == AddressMode.IMMEDIATE:
            if accumulator:
                tokens.append(InstructionTextToken(ITTT.OperandSeparatorToken, ' '))
                tokens.append(InstructionTextToken(ITTT.RegisterToken, accumulator))
            tokens.append(InstructionTextToken(ITTT.OperandSeparatorToken, ' '))
            tokens.append(InstructionTextToken(ITTT.IntegerToken, f'0x{value:X}', value))
        elif mode == AddressMode.INDEXED:
            if accumulator:
                tokens.append(InstructionTextToken(ITTT.OperandSeparatorToken, ' '))
                tokens.append(InstructionTextToken(ITTT.RegisterToken, accumulator))
            tokens.append(InstructionTextToken(ITTT.OperandSeparatorToken, ' '))
            tokens.append(InstructionTextToken(ITTT.RegisterToken, 'IX'))
            tokens.append(InstructionTextToken(ITTT.OperandSeparatorToken, ' + '))
            tokens.append(InstructionTextToken(ITTT.IntegerToken, f'0x{value:X}', value))

        return tokens, inst_length

    def get_instruction_info(self, data, addr):
        try:
            (nmemonic, inst_length, accumulator,
             inst_type, mode, value) = M6800._decode_instruction(data, addr)
        except LookupError as error:
            log_error(error.__str__())
            return None

        inst = InstructionInfo()
        inst.length = inst_length

        return inst

    def get_instruction_low_level_il(self, data, addr, il):
        return None


# Perform Binary Ninja loading
M6800.register()
