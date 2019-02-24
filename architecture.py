'''Binary Ninja architecture for the Motorola M6800 processor'''
import struct

from binaryninja import (
    Architecture, RegisterInfo, FlagRole, LowLevelILFlagCondition, log_error, InstructionTextToken,
    InstructionTextTokenType as ITTT, InstructionInfo, BranchType,
    LowLevelILFunction, LowLevelILLabel
)

from .instructions import (AddressMode, InstructionType, INSTRUCTIONS, ADDRESS_MASK,
                           BIGGER_LOADS, LLIL_OPERATIONS, REGISTER_OR_MEMORY_DESTINATIONS)


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
        'H': FlagRole.HalfCarryFlagRole
    }

    flag_write_types = ['', 'HNZVC', 'NZVC', 'NZV', 'Z']

    flags_written_by_flag_write_type = {
        'HNZVC': ['H', 'N', 'Z', 'V', 'C'],
        'NZVC': ['N', 'Z', 'V', 'C'],
        'NZV': ['N', 'Z', 'V'],
        'Z': ['Z']
    }

    flags_required_for_flag_condition = {
        LowLevelILFlagCondition.LLFC_UGE: ['C'],
        LowLevelILFlagCondition.LLFC_UGT: ['C', 'Z'],
        LowLevelILFlagCondition.LLFC_ULE: ['C', 'Z'],
        LowLevelILFlagCondition.LLFC_ULT: ['C'],
        LowLevelILFlagCondition.LLFC_SGE: ['N', 'V'],
        LowLevelILFlagCondition.LLFC_SLT: ['N', 'V'],
        LowLevelILFlagCondition.LLFC_SGT: ['Z', 'N', 'V'],
        LowLevelILFlagCondition.LLFC_SLE: ['Z', 'N', 'V'],
        LowLevelILFlagCondition.LLFC_E: ['Z'],
        LowLevelILFlagCondition.LLFC_NE: ['Z'],
        LowLevelILFlagCondition.LLFC_NEG: ['N'],
        LowLevelILFlagCondition.LLFC_POS: ['N'],
        LowLevelILFlagCondition.LLFC_O: ['V'],
        LowLevelILFlagCondition.LLFC_NO: ['V']
    }

    stack_pointer = 'SP'

    # pylint: disable=invalid-name
    @staticmethod
    def _handle_jump(il: LowLevelILFunction, value):
        label = il.get_label_for_address(Architecture['M6800'], value)

        return il.jump(il.const(2, value)) if label is None else il.goto(label)

    # pylint: disable=invalid-name
    @staticmethod
    def _handle_branch(il: LowLevelILFunction, nmemonic, inst_length, value):
        true_label = il.get_label_for_address(Architecture['M6800'], value)

        if true_label is None:
            true_label = LowLevelILLabel()
            indirect = True
        else:
            indirect = False

        false_label_found = True

        false_label = il.get_label_for_address(
            Architecture['M6800'], il.current_address + inst_length)

        if false_label is None:
            false_label = LowLevelILLabel()
            false_label_found = False

        il.append(il.if_expr(LLIL_OPERATIONS[nmemonic](il, None, None), true_label, false_label))

        if indirect:
            il.mark_label(true_label)
            il.append(il.jump(il.const(2, value)))

        if not false_label_found:
            il.mark_label(false_label)

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
        try:
            if mode == AddressMode.RELATIVE:  # calculate absolute address here
                # should always be 2 bytes long, second byte is 2's complement
                value = addr + inst_length + int.from_bytes(data[1:2], 'big', signed=True)
                # use address mask to set value to real space
                value &= ADDRESS_MASK
            elif mode == AddressMode.IMMEDIATE:
                if inst_length == 2:
                    value = data[1]
                else:
                    value = struct.unpack('>H', data[1:3])[0]
                    # use address mask to set value to real space
                    value &= ADDRESS_MASK
            elif mode == AddressMode.EXTENDED:
                value = struct.unpack('>H', data[1:3])[0]
                # use address mask to set value to real space
                value &= ADDRESS_MASK
            elif mode in [AddressMode.INDEXED,
                          AddressMode.DIRECT]:
                value = data[1]
        except struct.error:
            raise LookupError(f'Unable to decode instruction at address 0x{addr}')

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
             inst_type, mode, value) = M6800._decode_instruction(data, addr)
        except LookupError as error:
            log_error(error.__str__())
            return None

        inst = InstructionInfo()
        inst.length = inst_length

        if inst_type == InstructionType.CONDITIONAL_BRANCH:
            if mode == AddressMode.INDEXED:
                inst.add_branch(BranchType.UnresolvedBranch)
            else:
                inst.add_branch(BranchType.TrueBranch, value)
                inst.add_branch(BranchType.FalseBranch, addr + inst_length)
        elif inst_type == InstructionType.UNCONDITIONAL_BRANCH:
            if mode == AddressMode.INDEXED:
                inst.add_branch(BranchType.UnresolvedBranch)
            else:
                inst.add_branch(BranchType.UnconditionalBranch, value)
        elif inst_type == InstructionType.CALL:
            if mode == AddressMode.INDEXED:
                inst.add_branch(BranchType.UnresolvedBranch)
            else:
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
        load_size = 2 if nmemonic in BIGGER_LOADS else 1
        operand, second_operand = None, None

        # if this is a conditional branch, handle that separately
        if inst_type == InstructionType.CONDITIONAL_BRANCH:
            M6800._handle_branch(il, nmemonic, inst_length, value)
            return inst_length

        # if this is an unconditional branch, handle that separately
        if inst_type == InstructionType.UNCONDITIONAL_BRANCH:
            M6800._handle_jump(il, value)
            return inst_length

        if mode == AddressMode.ACCUMULATOR:
            # handle the case where we need the name, not the reg, for pop
            operand = inst_operand if nmemonic == 'PUL' else il.reg(1, inst_operand)
        elif mode == AddressMode.INDEXED:
            # set the destination variable for the memory store operations
            destination = il.add(
                2,
                il.reg(2, 'IX'),
                il.const(1, value)
            )
            operand = il.load(
                load_size,
                destination
            )
        elif mode in [AddressMode.DIRECT,
                      AddressMode.EXTENDED]:
            # set the destination variable for the memory store operations
            destination = il.const(
                inst_length - 1,
                value
            )
            operand = il.load(
                load_size,
                destination
            )
        elif mode == AddressMode.IMMEDIATE:
            operand = il.const(
                inst_length - 1,
                value
            )
        elif mode == AddressMode.RELATIVE:
            # we have already calculated the absolute address
            # set the destination variable for the memory store operations
            destination = il.const(2, value)
            operand = il.load(
                load_size,
                destination
            )

        # if we are dual mode, we have to handle things special
        if inst_type == InstructionType.DUAL:
            second_operand = inst_operand

        # calculate the base LLIL
        operation = LLIL_OPERATIONS[nmemonic](il, operand, second_operand)

        # if the instruction has different destinations, set them appropriately
        if nmemonic in REGISTER_OR_MEMORY_DESTINATIONS:
            if mode == AddressMode.ACCUMULATOR:
                operation = il.set_reg(1, inst_operand, operation)
            else:
                operation = il.store(1, destination, operation)

        # Finally, calculate and append the instruction(s)
        il.append(operation)

        return inst_length
