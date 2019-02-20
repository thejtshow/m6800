'''Binary Ninja architecture for the Motorola M6800 processor'''
import struct

from binaryninja import (
    Architecture, RegisterInfo, FlagRole, LowLevelILFlagCondition, log_error, InstructionTextToken,
    InstructionTextTokenType, InstructionInfo, BranchType
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
        'I': FlagRole.SpecialFlagRole,  # Interrupt Flag
        'H': FlagRole.HalfCarryFlagRole
    }

    # TODO: figure out how half-carry fits into this
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
            nmemonic, inst_length, accumulator, mode = INSTRUCTIONS[opcode]
        except KeyError:
            raise LookupError(f'Opcode 0x{opcode:X} at address 0x{addr:X} is invalid.')

        true_location = None
        false_location = None

        if opcode in CALL_INSTRUCTIONS + JMP_INSTRUCTIONS + BRANCH_INSTRUCTIONS:
            if inst_length == 2:
                true_location = addr + 2 + data[1]
            else:
                true_location = struct.unpack('>H', data[1:3])[0]
            if opcode in BRANCH_INSTRUCTIONS:  # conditionals have a false location
                false_location = addr + inst_length
        return (opcode, nmemonic, inst_length, accumulator, mode, true_location, false_location)

    def get_instruction_text(self, data, addr):
        try:
            (_, nmemonic, inst_length,
             accumulator, mode, true_location, _) = M6800._decode_instruction(data, addr)
        except LookupError as error:
            log_error(error.__str__())
            return None

        tokens = [
            InstructionTextToken(InstructionTextTokenType.TextToken, nmemonic)
        ]
        if accumulator:
            tokens.append(
                InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ' ')
            )
            tokens.append(
                InstructionTextToken(InstructionTextTokenType.RegisterToken, accumulator)
            )
        if true_location:
            tokens.append(
                InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ' ')
            )
            if mode != AddressMode.INDEXED:
                tokens.append(
                    InstructionTextToken(
                        InstructionTextTokenType.PossibleAddressToken, f'{true_location:X}'
                    )
                )
            else:
                tokens.append(
                    InstructionTextToken(
                        InstructionTextTokenType.TextToken, 'INDEXED'
                    )
                )
        return tokens, inst_length

    def get_instruction_info(self, data, addr):
        try:
            (opcode, _, inst_length,
             _, mode, true_location, false_location) = M6800._decode_instruction(data, addr)
        except LookupError as error:
            log_error(error.__str__())
            return None

        inst = InstructionInfo()
        inst.length = inst_length

        if (opcode in BRANCH_INSTRUCTIONS + CALL_INSTRUCTIONS + JMP_INSTRUCTIONS
                and mode == AddressMode.INDEXED):
            inst.add_branch(BranchType.UnresolvedBranch)
        elif opcode in BRANCH_INSTRUCTIONS:
            inst.add_branch(BranchType.TrueBranch, true_location)
            inst.add_branch(BranchType.FalseBranch, false_location)
        elif opcode in CALL_INSTRUCTIONS:
            inst.add_branch(BranchType.CallDestination, true_location)
        elif opcode in JMP_INSTRUCTIONS:
            inst.add_branch(BranchType.UnconditionalBranch, true_location)
        elif opcode in RETURN_INSTRUCTIONS:
            inst.add_branch(BranchType.FunctionReturn)

        return inst

    def get_instruction_low_level_il(self, data, addr, il):
        return None


# Perform Binary Ninja loading
M6800.register()
