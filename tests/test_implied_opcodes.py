import unittest

from unittest.mock import Mock, patch
from emupy6502.memory_controller import MemoryController
from emupy6502.registers import Registers
from emupy6502.opcodes import OpCode


class OpCodeTests(unittest.TestCase):
    
    def test_execute_nop(self):

        opcode = OpCode()
        registers = Registers()

        with patch.object(MemoryController, 'read', return_value = None) as mock_memory_controller:
            count = opcode.execute(0xEA, registers, mock_memory_controller)
            self.assertEqual(count, 2)
            mock_memory_controller.assert_not_called()
            self.assertTrue(registers == Registers())

    def test_execute_brk(self):

        opcode = OpCode()
        registers = Registers()
        registers.sp = 0x200

        mock_memory_controller = Mock()
        mock_memory_controller.read.side_effect = [0x00, 0x21]

        registers.pc += 1 #need to fake the cpu reading the opcode        
        count = opcode.execute(0x0, registers, mock_memory_controller)
        self.assertEqual(count, 7)
        self.assertEqual(mock_memory_controller.read.call_count, 2)
        self.assertEqual(mock_memory_controller.write.call_count, 3)
        self.assertEqual(mock_memory_controller.write.call_args_list[0], unittest.mock.call(0x200, 1))
        self.assertEqual(mock_memory_controller.write.call_args_list[1], unittest.mock.call(0x1ff, 0))
        self.assertEqual(mock_memory_controller.write.call_args_list[2], unittest.mock.call(0x1fe, registers.status_register()))
        self.assertEqual(registers.pc, 0x2100)

    def test_execute_tax(self):

        opcode = OpCode()
        registers = Registers()
        dummy_value = 0x7c # (positive, not zero)
        registers.accumulator =  dummy_value

        with patch.object(MemoryController, 'read', return_value = None) as mock_memory_controller:
            count = opcode.execute(0xAA, registers, mock_memory_controller)
            self.assertEqual(count, 2)
            mock_memory_controller.assert_not_called()
            self.assertEqual(registers.accumulator, dummy_value)
            self.assertEqual(registers.accumulator, registers.x_index)
            self.assertFalse(registers.negative_flag)
            self.assertFalse(registers.zero_flag)

    def test_execute_tay(self):

        opcode = OpCode()
        registers = Registers()
        dummy_value = 0x7c # (positive, not zero)
        registers.accumulator =  dummy_value

        with patch.object(MemoryController, 'read', return_value = None) as mock_memory_controller:
            count = opcode.execute(0xA8, registers, mock_memory_controller)
            self.assertEqual(count, 2)
            mock_memory_controller.assert_not_called()
            self.assertEqual(registers.accumulator, dummy_value)
            self.assertEqual(registers.accumulator, registers.y_index)
            self.assertFalse(registers.negative_flag)
            self.assertFalse(registers.zero_flag)

    def test_execute_txa(self):

        opcode = OpCode()
        registers = Registers()
        dummy_value = 0x7c # (positive, not zero)
        registers.x_index =  dummy_value

        with patch.object(MemoryController, 'read', return_value = None) as mock_memory_controller:
            count = opcode.execute(0x8A, registers, mock_memory_controller)
            self.assertEqual(count, 2)
            mock_memory_controller.assert_not_called()
            self.assertEqual(registers.x_index, dummy_value)
            self.assertEqual(registers.accumulator, registers.x_index)
            self.assertFalse(registers.negative_flag)
            self.assertFalse(registers.zero_flag)

    def test_execute_tya(self):

        opcode = OpCode()
        registers = Registers()
        dummy_value = 0x7c # (positive, not zero)
        registers.y_index =  dummy_value

        with patch.object(MemoryController, 'read', return_value = None) as mock_memory_controller:
            count = opcode.execute(0x98, registers, mock_memory_controller)
            self.assertEqual(count, 2)
            mock_memory_controller.assert_not_called()
            self.assertEqual(registers.y_index, dummy_value)
            self.assertEqual(registers.accumulator, registers.y_index)
            self.assertFalse(registers.negative_flag)
            self.assertFalse(registers.zero_flag)

    def test_execute_tsx(self):

        opcode = OpCode()
        registers = Registers() # leave sp with default
        old_sp = registers.sp

        with patch.object(MemoryController, 'read', return_value = None) as mock_memory_controller:
            count = opcode.execute(0xBA, registers, mock_memory_controller)
            self.assertEqual(count, 2)
            mock_memory_controller.assert_not_called()
            self.assertEqual(registers.x_index, old_sp)
            self.assertEqual(registers.sp, old_sp)
            self.assertTrue(registers.negative_flag) # default sp should be $fd
            self.assertFalse(registers.zero_flag)

    def test_execute_txs(self):

        opcode = OpCode()
        registers = Registers() 
        dummy_value = 0x7c # (positive, not zero)
        registers.x_index = dummy_value

        with patch.object(MemoryController, 'read', return_value = None) as mock_memory_controller:
            count = opcode.execute(0x9A, registers, mock_memory_controller)
            self.assertEqual(count, 2)
            mock_memory_controller.assert_not_called()
            self.assertEqual(registers.x_index, dummy_value)
            self.assertEqual(registers.sp, dummy_value)
            self.assertFalse(registers.negative_flag) # default sp should be $fd
            self.assertFalse(registers.zero_flag)

    def test_execute_inx_0_to_1(self):

        opcode = OpCode()
        registers = Registers() 
        dummy_value = 0x0
        registers.x_index = dummy_value

        with patch.object(MemoryController, 'read', return_value = None) as mock_memory_controller:
            count = opcode.execute(0xE8, registers, mock_memory_controller)
            self.assertEqual(count, 2)
            mock_memory_controller.assert_not_called()
            self.assertEqual(registers.x_index, dummy_value + 1)
            self.assertFalse(registers.negative_flag)
            self.assertFalse(registers.zero_flag)

    def test_execute_inx_127_to_128(self):

        opcode = OpCode()
        registers = Registers() 
        dummy_value = 0x7f
        registers.x_index = dummy_value
        
        opcode.execute(0xE8, registers, None)
        self.assertEqual(registers.x_index, dummy_value + 1)
        self.assertTrue(registers.negative_flag)
        self.assertFalse(registers.zero_flag)

    def test_execute_inx_255_to_0(self):

        opcode = OpCode()
        registers = Registers() 
        registers.x_index = 0xff

        opcode.execute(0xE8, registers, None)
        self.assertEqual(registers.x_index, 0)
        self.assertFalse(registers.negative_flag)
        self.assertTrue(registers.zero_flag)

    def test_execute_iny_0_to_1(self):

        opcode = OpCode()
        registers = Registers() 
        dummy_value = 0x0
        registers.y_index = dummy_value

        with patch.object(MemoryController, 'read', return_value = None) as mock_memory_controller:
            count = opcode.execute(0xC8, registers, mock_memory_controller)
            self.assertEqual(count, 2)
            mock_memory_controller.assert_not_called()
            self.assertEqual(registers.y_index, dummy_value + 1)
            self.assertFalse(registers.negative_flag)
            self.assertFalse(registers.zero_flag)

    def test_execute_iny_127_to_128(self):

        opcode = OpCode()
        registers = Registers() 
        dummy_value = 0x7f
        registers.y_index = dummy_value
        
        opcode.execute(0xC8, registers, None)
        self.assertEqual(registers.y_index, dummy_value + 1)
        self.assertTrue(registers.negative_flag)
        self.assertFalse(registers.zero_flag)

    def test_execute_iny_255_to_0(self):

        opcode = OpCode()
        registers = Registers() 
        registers.y_index = 0xff

        opcode.execute(0xC8, registers, None)
        self.assertEqual(registers.y_index, 0)
        self.assertFalse(registers.negative_flag)
        self.assertTrue(registers.zero_flag)

    def test_execute_dex_1_to_0(self):

        opcode = OpCode()
        registers = Registers() 
        registers.x_index = 1

        with patch.object(MemoryController, 'read', return_value = None) as mock_memory_controller:
            count = opcode.execute(0xCA, registers, mock_memory_controller)
            self.assertEqual(count, 2)
            mock_memory_controller.assert_not_called()
            self.assertEqual(registers.x_index, 0)
            self.assertFalse(registers.negative_flag)
            self.assertTrue(registers.zero_flag)

    def test_execute_dex_128_to_127(self):

        opcode = OpCode()
        registers = Registers() 
        registers.x_index = 0x80
        
        opcode.execute(0xCA, registers, None)
        self.assertEqual(registers.x_index, 0x7f)
        self.assertFalse(registers.negative_flag)
        self.assertFalse(registers.zero_flag)

    def test_execute_dex_0_to_minus1(self):

        opcode = OpCode()
        registers = Registers() 
        registers.x_index = 0

        opcode.execute(0xCA, registers, None)
        self.assertEqual(registers.x_index, 255)
        self.assertTrue(registers.negative_flag)
        self.assertFalse(registers.zero_flag)

    def test_execute_dey_1_to_0(self):

        opcode = OpCode()
        registers = Registers() 
        registers.y_index = 1

        with patch.object(MemoryController, 'read', return_value = None) as mock_memory_controller:
            count = opcode.execute(0x88, registers, mock_memory_controller)
            self.assertEqual(count, 2)
            mock_memory_controller.assert_not_called()
            self.assertEqual(registers.y_index, 0)
            self.assertFalse(registers.negative_flag)
            self.assertTrue(registers.zero_flag)

    def test_execute_dey_128_to_127(self):

        opcode = OpCode()
        registers = Registers() 
        registers.y_index = 0x80
        
        opcode.execute(0x88, registers, None)
        self.assertEqual(registers.y_index, 0x7f)
        self.assertFalse(registers.negative_flag)
        self.assertFalse(registers.zero_flag)

    def test_execute_dey_0_to_minus1(self):

        opcode = OpCode()
        registers = Registers() 
        registers.y_index = 0

        opcode.execute(0x88, registers, None)
        self.assertEqual(registers.y_index, 255)
        self.assertTrue(registers.negative_flag)
        self.assertFalse(registers.zero_flag)

if __name__ == '__main__':
    unittest.main()