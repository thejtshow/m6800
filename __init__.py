'''Binary Ninja architecture for the Motorola M6800 processor'''
import struct

from binaryninja import (
    Architecture, RegisterInfo, FlagRole, LowLevelILFlagCondition, log_error, InstructionTextToken,
    InstructionTextTokenType as ITTT, InstructionInfo, BranchType, LowLevelILFunction
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
            nmemonic, inst_length, inst_operand, inst_type, mode = INSTRUCTIONS[opcode]
        except KeyError:
            raise LookupError(f'Opcode 0x{opcode:X} at address 0x{addr:X} is invalid.')

        value = None

        # need to collect information based on each address mode
        # INHERENT addressing => value is None
        # ACCUMULATOR addressing => value is in accumulator
        if mode == AddressMode.RELATIVE:
            # should always be 2 bytes long, second byte is 2's complement
            value = addr + inst_length + int.from_bytes(data[1:2], 'big', signed=True)
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

        return nmemonic, inst_length, inst_operand, inst_type, mode, value

    def get_instruction_text(self, data, addr):
        try:
            (nmemonic, inst_length, inst_operand,
             _, mode, value) = M6800._decode_instruction(data, addr)
        except LookupError as error:
            log_error(error.__str__())
            return None

        tokens = [
            InstructionTextToken(ITTT.InstructionToken, nmemonic)
        ]

        if mode == AddressMode.ACCUMULATOR:
            tokens.append(InstructionTextToken(ITTT.OperandSeparatorToken, ' '))
            tokens.append(InstructionTextToken(ITTT.RegisterToken, inst_operand))
        elif mode in [AddressMode.DIRECT, AddressMode.EXTENDED, AddressMode.RELATIVE]:
            tokens.append(InstructionTextToken(ITTT.OperandSeparatorToken, ' '))
            tokens.append(InstructionTextToken(ITTT.PossibleAddressToken, f'0x{value:X}', value))
        elif mode == AddressMode.IMMEDIATE:
            if inst_operand in ['ACCA', 'ACCB']:
                tokens.append(InstructionTextToken(ITTT.OperandSeparatorToken, ' '))
                tokens.append(InstructionTextToken(ITTT.RegisterToken, inst_operand))
            tokens.append(InstructionTextToken(ITTT.OperandSeparatorToken, ' '))
            tokens.append(InstructionTextToken(ITTT.IntegerToken, f'0x{value:X}', value))
        elif mode == AddressMode.INDEXED:
            if inst_operand in ['ACCA', 'ACCB']:
                tokens.append(InstructionTextToken(ITTT.OperandSeparatorToken, ' '))
                tokens.append(InstructionTextToken(ITTT.RegisterToken, inst_operand))
            tokens.append(InstructionTextToken(ITTT.OperandSeparatorToken, ' '))
            tokens.append(InstructionTextToken(ITTT.BeginMemoryOperandToken, '['))
            tokens.append(InstructionTextToken(ITTT.RegisterToken, 'IX'))
            tokens.append(InstructionTextToken(ITTT.OperandSeparatorToken, ' + '))
            tokens.append(InstructionTextToken(ITTT.IntegerToken, f'0x{value:X}', value))
            tokens.append(InstructionTextToken(ITTT.EndMemoryOperandToken, ']'))

        return tokens, inst_length

    def get_instruction_info(self, data, addr):
        try:
            (_, inst_length, _,
             inst_type, _, value) = M6800._decode_instruction(data, addr)
        except LookupError as error:
            log_error(error.__str__())
            return None

        inst = InstructionInfo()
        inst.length = inst_length

        if inst_type == InstructionType.CONDITIONAL_BRANCH:
            inst.add_branch(BranchType.TrueBranch, value)
            inst.add_branch(BranchType.FalseBranch, addr + inst_length)
        elif inst_type == InstructionType.UNCONDITIONAL_BRANCH:
            inst.add_branch(BranchType.UnconditionalBranch, value)
        elif inst_type == InstructionType.CALL:
            inst.add_branch(BranchType.CallDestination, value)
        elif inst_type == InstructionType.RETURN:
            inst.add_branch(BranchType.FunctionReturn)

        return inst

    def get_instruction_low_level_il(self, data, addr, il: LowLevelILFunction):
        try:
            (nmemonic, inst_length, inst_operand,
             inst_type, mode, value) = M6800._decode_instruction(data, addr)
        except LookupError as error:
            log_error(error.__str__())
            return None

        # Figure out what the instruction uses
        if mode == AddressMode.ACCUMULATOR:
            operand = il.reg(1, inst_operand)
        elif mode == AddressMode.INDEXED:
            operand = il.load(
                1,
                il.add(
                    2,
                    il.reg(2, 'IX'),
                    il.const(1, value)
                )
            )
        elif mode in [AddressMode.DIRECT,
                      AddressMode.EXTENDED]:
            operand = il.load(
                1,
                il.const(
                    inst_length - 1,
                    value
                )
            )
        elif mode == AddressMode.IMMEDIATE:
            operand = il.const(inst_length - 1, value)
        elif mode == AddressMode.RELATIVE:  # we have already calculated the absolute address
            operand = il.const(2, value)
        elif mode == AddressMode.IMPLIED:  # these will be different for each instruction
            operand, second_operand = IMPLIED_OPERANDS[inst_operand](il)
        # if we are dual mode, we have to handle things special
        if inst_type == InstructionType.DUAL:
            second_operand = inst_operand

        il.append(LLIL_OPERATIONS[nmemonic](il, operand, second_operand))

        return inst_length


# Perform Binary Ninja loading
M6800.register()
