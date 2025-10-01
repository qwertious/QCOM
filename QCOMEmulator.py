import pygame
import sys
import os

#  QQQQ   CCC   OOO  MM MM
# Q    Q C   C O   O M M M
# Q  Q Q C     O   O M M M
# Q   Q  C   C O   O M M M
#  QQQ Q  CCC   OOO  M M M

# QCOM Official emulator

# ============================
# Check for ROM argument
# ============================
if len(sys.argv) < 2:
    print("Usage: python emulator.py <rom_file>")
    sys.exit(1)

rom_path = sys.argv[1]
if not os.path.exists(rom_path):
    print(f"Error: File '{rom_path}' does not exist.")
    sys.exit(1)

# ============================
# Load ROM into memory
# ============================
with open(rom_path, "rb") as f:
    memory = list(f.read())

# Ensure memory is at least 256 bytes, pad with zeros if smaller
MEMORY_SIZE = 256
if len(memory) < MEMORY_SIZE:
    memory.extend([0] * (MEMORY_SIZE - len(memory)))

pc = 0x90  # Program Counter (pointer into memory)
display_value = 0

# Registers (8 general purpose for now)
registers = [0] * 8

# ============================
# Instruction Handling
# ============================

# Utility to set or clear the zero flag (bit 0 of register 3)
def set_zero_flag(value):
    if value == 0:
        registers[7] |= 0b00000001  # Set bit 0
    else:
        registers[7] &= 0b11111110  # Clear bit 0

def get_zero_flag():
    return registers[7] & 0b00000001

def effective_address(addr):
    # Get page from R7 (upper 4 bits)
    page = (registers[7] >> 4) & 0x0F
    return ((page << 8) | (addr & 0xFF)) % len(memory)

def byte_to_pixels(byte_val):
    # Left pixel (bits 7-5)
    r1 = (byte_val >> 7) & 0x1
    g1 = (byte_val >> 6) & 0x1
    b1 = (byte_val >> 5) & 0x1
    # Scale to 0/255
    color1 = (r1 * 255, g1 * 255, b1 * 255)

    # Right pixel (bits 3-1)
    r2 = (byte_val >> 3) & 0x1
    g2 = (byte_val >> 2) & 0x1
    b2 = (byte_val >> 1) & 0x1
    color2 = (r2 * 255, g2 * 255, b2 * 255)

    return color1, color2

def fetch_byte():
    global pc
    if pc < len(memory):
        val = memory[pc]
        pc += 1
        return val
    else:
        return 0

def handle_instruction(opcode):
    global display_value, pc
    # DIS
    if opcode == 0x01:  # DIS IMM
        imm = fetch_byte()
        display_value = imm & 0xFF
        print(f"DIS IMM {display_value}")

    elif opcode == 0x02:  # DIS REG
        reg = fetch_byte() & 0x07
        display_value = registers[reg] & 0xFF
        print(f"DIS R{reg} = {display_value}")

    elif opcode == 0x03:  # DIS ADDR
        addr = effective_address(fetch_byte())
        display_value = memory[addr] & 0xFF
        print(f"DIS MEM[{addr}] = {display_value}")

    # IN
    elif opcode == 0x04:  # IN REG
        reg = fetch_byte() & 0x07
        registers[reg] = memory[0x80] & 0xFF
        set_zero_flag(registers[reg])
        print(f"IN R{reg} <- MEM[0x80] ({registers[reg]:08b})")

    # OUT
    elif opcode == 0x05:  # OUT IMM, IMM
        port = fetch_byte()
        val = fetch_byte() & 0xFF
        print(f"OUT port {port}, value {val}")

    elif opcode == 0x06:  # OUT IMM, REG
        port = fetch_byte()
        reg = fetch_byte() & 0x07
        print(f"OUT port {port}, R{reg}={registers[reg] & 0xFF}")

    elif opcode == 0x07:  # OUT IMM, ADDR
        port = fetch_byte()
        addr = effective_address(fetch_byte())
        print(f"OUT port {port}, MEM[{addr}]={memory[addr] & 0xFF}")

    # BRK
    elif opcode == 0x0F:
        print("BRK - Break / Halt")
        pygame.quit()
        sys.exit()

    # MOV
    elif opcode == 0x10:  # MOV REG, IMM
        reg = fetch_byte() & 0x07
        imm = fetch_byte() & 0xFF
        old = int(registers[reg])
        registers[reg] = imm
        set_zero_flag(registers[reg])
        print(f"MOV R{reg}, {imm} | old={old} -> new={registers[reg]}")

    elif opcode == 0x11:  # MOV ADDR, REG
        addr = effective_address(fetch_byte())
        reg = fetch_byte() & 0x07
        old = int(memory[addr])
        memory[addr] = registers[reg] & 0xFF
        set_zero_flag(memory[addr])
        print(f"MOV MEM[{addr}], R{reg} | old={old} -> new={memory[addr]}")

    elif opcode == 0x12:  # MOV REG, ADDR
        reg = fetch_byte() & 0x07
        addr = effective_address(fetch_byte())
        old = int(registers[reg])
        registers[reg] = memory[addr] & 0xFF
        set_zero_flag(registers[reg])
        print(f"MOV R{reg}, MEM[{addr}] | old={old} -> new={registers[reg]}")

    elif opcode == 0x13:  # MOV REG, REG
        reg1 = fetch_byte() & 0x07
        reg2 = fetch_byte() & 0x07
        old = int(registers[reg1])
        registers[reg1] = registers[reg2] & 0xFF
        set_zero_flag(registers[reg1])
        print(f"MOV R{reg1}, R{reg2} | old={old} -> new={registers[reg1]}")

    # SHW
    elif opcode == 0x14:  # SHW
        print("SHW - Show frame")
        
        # --- Render Display ---
        screen.fill((0, 0, 0))

        # --- Draw Game Board ---
        addr = 0x0
        for y in range(BOARD_SIZE):
            for x in range(0, BOARD_SIZE, 2):
                byte_val = memory[addr]
                addr += 1
                color1, color2 = byte_to_pixels(byte_val)

                rect1 = pygame.Rect(board_x + x*cell_size, board_y + y*cell_size, cell_size, cell_size)
                rect2 = pygame.Rect(board_x + (x+1)*cell_size, board_y + y*cell_size, cell_size, cell_size)

                pygame.draw.rect(screen, color1, rect1)
                pygame.draw.rect(screen, color2, rect2)

        if show_fps:
            fps = clock.get_fps()
            fps_text = fps_font.render(f"FPS: {fps:.2f}", True, (255, 255, 255))
            screen.blit(fps_text, (10, 10))

            # Display the display_value in top-right corner:
            bin_str = f"{display_value:08b}"  # 8-bit binary string
            hex_str = f"0x{display_value:02X}"

            bin_text = fps_font.render(bin_str, True, (255, 255, 255))
            hex_text = fps_font.render(hex_str, True, (255, 255, 255))

            padding = 10
            bin_pos = (WIDTH - bin_text.get_width() - padding, padding)
            hex_pos = (WIDTH - hex_text.get_width() - padding, padding + bin_text.get_height())

            screen.blit(bin_text, bin_pos)
            screen.blit(hex_text, hex_pos)

        pygame.display.flip()

    # CLS
    elif opcode == 0x15:
        color = fetch_byte() & 0xFF
        print(f"CLS - Clear screen to color {color}")

    # SBL / SBR / RBL / RBR
    elif opcode == 0x18:  # SBL REG (Shift Left)
        reg = fetch_byte() & 0x07
        registers[reg] = ((registers[reg] << 1) & 0xFF)
        set_zero_flag(registers[reg])
        print(f"SBL R{reg} -> {registers[reg]:02X}")

    elif opcode == 0x19:  # SBL ADDR (Shift Left)
        addr = effective_address(fetch_byte())
        memory[addr] = ((memory[addr] << 1) & 0xFF)
        set_zero_flag(memory[addr])
        print(f"SBL MEM[{addr}] -> {memory[addr]:02X}")

    elif opcode == 0x1A:  # SBR REG (Shift Right)
        reg = fetch_byte() & 0x07
        registers[reg] = ((registers[reg] >> 1) & 0xFF)
        set_zero_flag(registers[reg])
        print(f"SBR R{reg} -> {registers[reg]:02X}")

    elif opcode == 0x1B:  # SBR ADDR (Shift Right)
        addr = effective_address(fetch_byte())
        memory[addr] = ((memory[addr] >> 1) & 0xFF)
        set_zero_flag(memory[addr])
        print(f"SBR MEM[{addr}] -> {memory[addr]:02X}")

    elif opcode == 0x1C:  # RBL REG (Rotate Left)
        reg = fetch_byte() & 0x07
        val = registers[reg]
        registers[reg] = ((val << 1) & 0xFF) | ((val >> 7) & 0x01)
        set_zero_flag(registers[reg])
        print(f"RBL R{reg} -> {registers[reg]:02X}")

    elif opcode == 0x1D:  # RBL ADDR (Rotate Left)
        addr = effective_address(fetch_byte())
        val = memory[addr]
        memory[addr] = ((val << 1) & 0xFF) | ((val >> 7) & 0x01)
        set_zero_flag(memory[addr])
        print(f"RBL MEM[{addr}] -> {memory[addr]:02X}")

    elif opcode == 0x1E:  # RBR REG (Rotate Right)
        reg = fetch_byte() & 0x07
        val = registers[reg]
        registers[reg] = ((val >> 1) & 0xFF) | ((val & 0x01) << 7)
        set_zero_flag(registers[reg])
        print(f"RBR R{reg} -> {registers[reg]:02X}")

    elif opcode == 0x1F:  # RBR ADDR (Rotate Right)
        addr = effective_address(fetch_byte())
        val = memory[addr]
        memory[addr] = ((val >> 1) & 0xFF) | ((val & 0x01) << 7)
        set_zero_flag(memory[addr])
        print(f"RBR MEM[{addr}] -> {memory[addr]:02X}")

    # === LOGIC OPERATIONS ===
    # AND
    elif opcode == 0x20:  # AND REG, IMM
        reg = fetch_byte() & 0x07
        imm = fetch_byte() & 0xFF
        old = int(registers[reg])
        registers[reg] = (registers[reg] & imm) & 0xFF
        set_zero_flag(registers[reg])
        print(f"AND R{reg}, {imm:#04x} | {old:#04x} & {imm:#04x} = {registers[reg]:#04x}")

    elif opcode == 0x21:  # AND ADDR, REG
        addr = effective_address(fetch_byte())
        reg = fetch_byte() & 0x07
        old = int(memory[addr])
        memory[addr] = (memory[addr] & registers[reg]) & 0xFF
        set_zero_flag(memory[addr])
        print(f"AND MEM[{addr}], R{reg} | {old:#04x} & {registers[reg]:#04x} = {memory[addr]:#04x}")

    elif opcode == 0x22:  # AND REG, ADDR
        reg = fetch_byte() & 0x07
        addr = effective_address(fetch_byte())
        old = int(registers[reg])
        registers[reg] = (registers[reg] & memory[addr]) & 0xFF
        set_zero_flag(registers[reg])
        print(f"AND R{reg}, MEM[{addr}] | {old:#04x} & {memory[addr]:#04x} = {registers[reg]:#04x}")

    elif opcode == 0x23:  # AND REG, REG
        reg1 = fetch_byte() & 0x07
        reg2 = fetch_byte() & 0x07
        old = int(registers[reg1])
        registers[reg1] = (registers[reg1] & registers[reg2]) & 0xFF
        set_zero_flag(registers[reg1])
        print(f"AND R{reg1}, R{reg2} | {old:#04x} & {registers[reg2]:#04x} = {registers[reg1]:#04x}")

    # OR
    elif opcode == 0x24:  # OR REG, IMM
        reg = fetch_byte() & 0x07
        imm = fetch_byte() & 0xFF
        old = int(registers[reg])
        registers[reg] = (registers[reg] | imm) & 0xFF
        set_zero_flag(registers[reg])
        print(f"OR R{reg}, {imm:#04x} | {old:#04x} | {imm:#04x} = {registers[reg]:#04x}")

    elif opcode == 0x25:  # OR ADDR, REG
        addr = effective_address(fetch_byte())
        reg = fetch_byte() & 0x07
        old = int(memory[addr])
        memory[addr] = (memory[addr] | registers[reg]) & 0xFF
        set_zero_flag(memory[addr])
        print(f"OR MEM[{addr}], R{reg} | {old:#04x} | {registers[reg]:#04x} = {memory[addr]:#04x}")

    elif opcode == 0x26:  # OR REG, ADDR
        reg = fetch_byte() & 0x07
        addr = effective_address(fetch_byte())
        old = int(registers[reg])
        registers[reg] = (registers[reg] | memory[addr]) & 0xFF
        set_zero_flag(registers[reg])
        print(f"OR R{reg}, MEM[{addr}] | {old:#04x} | {memory[addr]:#04x} = {registers[reg]:#04x}")

    elif opcode == 0x27:  # OR REG, REG
        reg1 = fetch_byte() & 0x07
        reg2 = fetch_byte() & 0x07
        old = int(registers[reg1])
        registers[reg1] = (registers[reg1] | registers[reg2]) & 0xFF
        set_zero_flag(registers[reg1])
        print(f"OR R{reg1}, R{reg2} | {old:#04x} | {registers[reg2]:#04x} = {registers[reg1]:#04x}")
    
    # XOR
    elif opcode == 0x28:  # XOR REG, IMM
        reg = fetch_byte() & 0x07
        imm = fetch_byte() & 0xFF
        old = int(registers[reg])
        registers[reg] = (registers[reg] ^ imm) & 0xFF
        set_zero_flag(registers[reg])
        print(f"XOR R{reg}, {imm:#04x} | {old:#04x} ^ {imm:#04x} = {registers[reg]:#04x}")

    elif opcode == 0x29:  # XOR ADDR, REG
        addr = effective_address(fetch_byte())
        reg = fetch_byte() & 0x07
        old = int(memory[addr])
        memory[addr] = (memory[addr] ^ registers[reg]) & 0xFF
        set_zero_flag(memory[addr])
        print(f"XOR MEM[{addr}], R{reg} | {old:#04x} ^ {registers[reg]:#04x} = {memory[addr]:#04x}")

    elif opcode == 0x2A:  # XOR REG, ADDR
        reg = fetch_byte() & 0x07
        addr = effective_address(fetch_byte())
        old = int(registers[reg])
        registers[reg] = (registers[reg] ^ memory[addr]) & 0xFF
        set_zero_flag(registers[reg])
        print(f"XOR R{reg}, MEM[{addr}] | {old:#04x} ^ {memory[addr]:#04x} = {registers[reg]:#04x}")

    elif opcode == 0x2B:  # XOR REG, REG
        reg1 = fetch_byte() & 0x07
        reg2 = fetch_byte() & 0x07
        old = int(registers[reg1])
        registers[reg1] = (registers[reg1] ^ registers[reg2]) & 0xFF
        set_zero_flag(registers[reg1])
        print(f"XOR R{reg1}, R{reg2} | {old:#04x} ^ {registers[reg2]:#04x} = {registers[reg1]:#04x}")

    # NOT
    elif opcode == 0x2C:  # NOT REG
        reg = fetch_byte() & 0x07
        old = int(registers[reg])
        registers[reg] = (~registers[reg]) & 0xFF
        set_zero_flag(registers[reg])
        print(f"NOT R{reg} | ~{old:#04x} = {registers[reg]:#04x}")

    elif opcode == 0x2D:  # NOT ADDR
        addr = effective_address(fetch_byte())
        old = int(memory[addr])
        memory[addr] = (~memory[addr]) & 0xFF
        set_zero_flag(memory[addr])
        print(f"NOT MEM[{addr}] | ~{old:#04x} = {memory[addr]:#04x}")

    # === ARITHMETIC ===
    # ADD
    elif opcode == 0x30:  # ADD REG, IMM
        reg = fetch_byte() & 0x07
        imm = fetch_byte() & 0xFF
        old = int(registers[reg])
        registers[reg] = (registers[reg] + imm) & 0xFF
        set_zero_flag(registers[reg])
        print(f"ADD R{reg}, {imm} | {old} + {imm} = {registers[reg]}")

    elif opcode == 0x31:  # ADD ADDR, REG
        addr = effective_address(fetch_byte())
        reg = fetch_byte() & 0x07
        old = int(memory[addr])
        memory[addr] = (memory[addr] + registers[reg]) & 0xFF
        set_zero_flag(memory[addr])
        print(f"ADD MEM[{addr}], R{reg} | {old} + {registers[reg]} = {memory[addr]}")

    elif opcode == 0x32:  # ADD REG, ADDR
        reg = fetch_byte() & 0x07
        addr = effective_address(fetch_byte())
        old = int(registers[reg])
        registers[reg] = (registers[reg] + memory[addr]) & 0xFF
        set_zero_flag(registers[reg])
        print(f"ADD R{reg}, MEM[{addr}] | {old} + {memory[addr]} = {registers[reg]}")

    elif opcode == 0x33:  # ADD REG, REG
        reg1 = fetch_byte() & 0x07
        reg2 = fetch_byte() & 0x07
        old = int(registers[reg1])
        registers[reg1] = (registers[reg1] + registers[reg2]) & 0xFF
        set_zero_flag(registers[reg1])
        print(f"ADD R{reg1}, R{reg2} | {old} + {registers[reg2]} = {registers[reg1]}")

    # SUB
    elif opcode == 0x34:  # SUB REG, IMM
        reg = fetch_byte() & 0x07
        imm = fetch_byte() & 0xFF
        old = int(registers[reg])
        registers[reg] = (registers[reg] - imm) & 0xFF
        set_zero_flag(registers[reg])
        print(f"SUB R{reg}, {imm} | {old} - {imm} = {registers[reg]}")

    elif opcode == 0x35:  # SUB ADDR, REG
        addr = effective_address(fetch_byte())
        reg = fetch_byte() & 0x07
        old = int(memory[addr])
        memory[addr] = (memory[addr] - registers[reg]) & 0xFF
        set_zero_flag(memory[addr])
        print(f"SUB MEM[{addr}], R{reg} | {old} - {registers[reg]} = {memory[addr]}")

    elif opcode == 0x36:  # SUB REG, ADDR
        reg = fetch_byte() & 0x07
        addr = effective_address(fetch_byte())
        old = int(registers[reg])
        registers[reg] = (registers[reg] - memory[addr]) & 0xFF
        set_zero_flag(registers[reg])
        print(f"SUB R{reg}, MEM[{addr}] | {old} - {memory[addr]} = {registers[reg]}")

    elif opcode == 0x37:  # SUB REG, REG
        reg1 = fetch_byte() & 0x07
        reg2 = fetch_byte() & 0x07
        old = int(registers[reg1])
        registers[reg1] = (registers[reg1] - registers[reg2]) & 0xFF
        set_zero_flag(registers[reg1])
        print(f"SUB R{reg1}, R{reg2} | {old} - {registers[reg2]} = {registers[reg1]}")

    # INC
    elif opcode == 0x38:  # INC REG
        reg = fetch_byte() & 0x07
        old = int(registers[reg])
        registers[reg] = (registers[reg] + 1) & 0xFF
        set_zero_flag(registers[reg])
        print(f"INC R{reg} | {old} + 1 = {registers[reg]}")

    elif opcode == 0x39:  # INC ADDR
        addr = effective_address(fetch_byte())
        old = int(memory[addr])
        memory[addr] = (memory[addr] + 1) & 0xFF
        set_zero_flag(memory[addr])
        print(f"INC MEM[{addr}] | {old} + 1 = {memory[addr]}")

    # DEC
    elif opcode == 0x3A:  # DEC REG
        reg = fetch_byte() & 0x07
        old = int(registers[reg])
        registers[reg] = (registers[reg] - 1) & 0xFF
        set_zero_flag(registers[reg])
        print(f"DEC R{reg} | {old} - 1 = {registers[reg]}")

    elif opcode == 0x3B:  # DEC ADDR
        addr = effective_address(fetch_byte())
        old = int(memory[addr])
        memory[addr] = (memory[addr] - 1) & 0xFF
        set_zero_flag(memory[addr])
        print(f"DEC MEM[{addr}] | {old} - 1 = {memory[addr]}")

    # === JUMPING ===
    elif opcode == 0x40:  # JMP IMM
        addr = effective_address(fetch_byte())
        # Print the addr in hex
        print(f"JMP {addr:#04x} | jumping to {addr}")
        if 0 <= addr < len(memory):
            pc = addr

    elif opcode == 0x41:  # JMP REG
        reg = fetch_byte() & 0x07
        print(f"JMP R{reg} | jumping to {registers[reg]}")
        if 0 <= registers[reg] < len(memory):
            pc = registers[reg]

    elif opcode == 0x42:  # JIF IMM, IMM
        imm1 = fetch_byte()
        imm2 = effective_address(fetch_byte())
        cond = bool(imm1 & 0b00000001)
        taken = cond and get_zero_flag()
        print(f"JIF {imm1}, {imm2:#04x} | cond={cond}, ZF={get_zero_flag()} -> {'taken' if taken else 'not taken'}")
        if taken and 0 <= imm2 < len(memory):
            pc = imm2

    elif opcode == 0x43:  # JIF IMM, REG
        imm = fetch_byte()
        reg = fetch_byte() & 0x07
        cond = bool(imm & 0b00000001)
        taken = cond and get_zero_flag()
        print(f"JIF {imm}, R{reg} | cond={cond}, ZF={get_zero_flag()} -> {'taken' if taken else 'not taken'}")
        if taken and 0 <= registers[reg] < len(memory):
            pc = registers[reg]

    elif opcode == 0x44:  # JNI IMM, IMM
        imm1 = fetch_byte()
        imm2 = effective_address(fetch_byte())
        cond = bool(imm1 & 0b00000001)
        taken = cond and not get_zero_flag()
        print(f"JNI {imm1}, {imm2:#04x} | cond={cond}, ZF={get_zero_flag()} -> {'taken' if taken else 'not taken'}")
        if taken and 0 <= imm2 < len(memory):
            pc = imm2

    elif opcode == 0x45:  # JNI IMM, REG
        imm = fetch_byte()
        reg = fetch_byte() & 0x07
        cond = bool(imm & 0b00000001)
        taken = cond and not get_zero_flag()
        print(f"JNI {imm}, R{reg} | cond={cond}, ZF={get_zero_flag()} -> {'taken' if taken else 'not taken'}")
        if taken and 0 <= registers[reg] < len(memory):
            pc = effective_address(registers[reg])

    # --- Move Indirect Location ---

    elif opcode == 0x50:  # MIL REG, IMM
        reg = fetch_byte() & 0x07
        imm = fetch_byte() & 0xFF
        # Set the point in memory referenced by the register to the immediate value
        addr = effective_address(registers[reg])
        old = int(memory[addr])
        memory[addr] = imm
        set_zero_flag(registers[reg])
        print(f"MIL R{reg}, {imm} | old={old} -> new={registers[reg]}")

    elif opcode == 0x51:  # MIL REG, REG
        reg1 = fetch_byte() & 0x07
        reg2 = fetch_byte() & 0x07
        addr = effective_address(registers[reg1])
        old = int(memory[addr])
        memory[addr] = registers[reg2] & 0xFF
        set_zero_flag(registers[reg1])
        print(f"MIL R{reg1}, R{reg2} | old={old} -> new={registers[reg1]}")

    elif opcode == 0x52:  # MIL REG, ADDR
        reg = fetch_byte() & 0x07
        addr2 = effective_address(fetch_byte())
        addr1 = effective_address(registers[reg])
        old = int(memory[addr1])
        memory[addr1] = memory[addr2] & 0xFF
        set_zero_flag(registers[reg])
        print(f"MIL R{reg}, MEM[{addr2}] | old={old} -> new={registers[reg]}")

    elif opcode == 0x53:  # MIL ADDR, REG
        addr1 = effective_address(fetch_byte())
        reg = fetch_byte() & 0x07
        addr2 = effective_address(memory[addr1])
        old = int(memory[addr2])
        memory[addr2] = registers[reg] & 0xFF
        set_zero_flag(memory[addr2])
        print(f"MIL MEM[{addr1}], R{reg} | old={old} -> new={memory[addr2]}")

    # --- Move From Indirect ---

    elif opcode == 0x54:  # MFI REG, REG
        reg1 = fetch_byte() & 0x07
        reg2 = fetch_byte() & 0x07
        old = int(registers[reg1])
        registers[reg1] = memory[effective_address(registers[reg2])]
        set_zero_flag(registers[reg1])
        print(f"MFI R{reg1}, R{reg2} | old={old} -> new={registers[reg1]}")

    elif opcode == 0x55:  # MFI REG, ADDR
        reg = fetch_byte() & 0x07
        addr2 = effective_address(fetch_byte())
        addr1 = effective_address(memory[addr2])
        old = int(registers[reg])
        registers[reg] = memory[addr1] & 0xFF
        set_zero_flag(registers[reg])
        print(f"MFI R{reg}, MEM[{addr2}] | old={old} -> new={registers[reg]}")

    elif opcode == 0x56:  # MFI ADDR, REG
        addr1 = effective_address(fetch_byte())
        reg = fetch_byte() & 0x07
        addr2 = effective_address(registers[reg])
        old = int(memory[addr1])
        memory[addr1] = memory[addr2] & 0xFF
        set_zero_flag(memory[addr1])
        print(f"MFI MEM[{addr1}], R{reg} | old={old} -> new={memory[addr1]}")

    elif opcode == 0x57:  # MFI ADDR, ADDR
        addr1 = effective_address(fetch_byte())
        addr2 = effective_address(fetch_byte())
        addr3 = effective_address(memory[addr2])
        old = int(memory[addr1])
        memory[addr1] = memory[addr3] & 0xFF
        set_zero_flag(memory[addr1])
        print(f"MFI MEM[{addr1}], MEM[{addr2}] | old={old} -> new={memory[addr1]}")

    # Add more opcodes similarly...

    else:
        print(f"Unknown opcode: 0x{opcode:02X}")



# ============================
# Pygame Setup
# ============================
pygame.init()
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Emulator Display")

clock = pygame.time.Clock()
fps_font = pygame.font.SysFont("Arial", 18)
show_fps = False

BOARD_SIZE = 16
board_pixels = min(WIDTH, HEIGHT)
cell_size = board_pixels // BOARD_SIZE

board_x = (WIDTH - board_pixels) // 2
board_y = (HEIGHT - board_pixels) // 2

# ============================
# Main Loop
# ============================
running = True
while running:
    # --- Handle Events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                show_fps = not show_fps

        # --- Update Controller State ---
    keys = pygame.key.get_pressed()
    controller_byte = 0

    if keys[pygame.K_w]: controller_byte |= (1 << 7)
    if keys[pygame.K_s]: controller_byte |= (1 << 6)
    if keys[pygame.K_a]: controller_byte |= (1 << 5)
    if keys[pygame.K_d]: controller_byte |= (1 << 4)
    if keys[pygame.K_SPACE]: controller_byte |= (1 << 3)
    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]: controller_byte |= (1 << 2)
    if keys[pygame.K_RETURN]: controller_byte |= (1 << 1)
    if keys[pygame.K_BACKSPACE]: controller_byte |= (1 << 0)

    memory[0x80] = controller_byte

    # --- Emulation Step ---
    if pc < len(memory):
        opcode = memory[pc]
        pc += 1
        handle_instruction(opcode)

    # --- Render Display ---
    # screen.fill((0, 0, 0))

    # if show_fps:
    #     fps = clock.get_fps()
    #     fps_text = fps_font.render(f"FPS: {fps:.2f}", True, (255, 255, 255))
    #     screen.blit(fps_text, (10, 10))

    # # Display the display_value in top-right corner:
    # bin_str = f"{display_value:08b}"  # 8-bit binary string
    # hex_str = f"0x{display_value:02X}"

    # # Create text surfaces
    # bin_text = fps_font.render(bin_str, True, (255, 255, 255))
    # hex_text = fps_font.render(hex_str, True, (255, 255, 255))

    # # Position at top right, with some padding
    # padding = 10
    # bin_pos = (WIDTH - bin_text.get_width() - padding, padding)
    # hex_pos = (WIDTH - hex_text.get_width() - padding, padding + bin_text.get_height())

    # screen.blit(bin_text, bin_pos)
    # screen.blit(hex_text, hex_pos)

    # # --- Draw Game Board ---
    # addr = 0x80
    # for y in range(BOARD_SIZE):
    #     for x in range(0, BOARD_SIZE, 2):  # 2 pixels per byte
    #         byte_val = memory[addr]
    #         addr += 1
    #         color1, color2 = byte_to_pixels(byte_val)

    #         # Left pixel
    #         rect1 = pygame.Rect(board_x + x*cell_size, board_y + y*cell_size, cell_size, cell_size)
    #         pygame.draw.rect(screen, color1, rect1)

    #         # Right pixel
    #         rect2 = pygame.Rect(board_x + (x+1)*cell_size, board_y + y*cell_size, cell_size, cell_size)
    #         pygame.draw.rect(screen, color2, rect2)

    # pygame.display.flip()
    clock.tick(1000)

# ============================
# Cleanup
# ============================
pygame.quit()
sys.exit()
