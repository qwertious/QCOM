// Minimal QCOM Interpreter for Arduino Mega
// Supports MOV (REG, IMM), ADD (REG, REG), OUT (IMM, REG), BRK ()

#define NUM_REGS 8

// assigning arduino digital pins for the various led display pins
int pinA = 24;
int pinB = 25;
int pinC = 26;
int pinD = 27;
int pinE = 28;
int pinF = 29;
int pinG = 30;
int D1 = 22;
int D2 = 23;

byte display = 0x00;

// Registers
uint8_t R[NUM_REGS];

// Example program:
// MOV R0, 5
// MOV R1, 10
// ADD R0, R1
// OUT 0, R0
// BRK
uint8_t program[] = {
    0x30, 0x00, 0x01, // ADD R0, 1
    0x02, 0x00,       // DIS R0
    0x14,             // SHW
    0x40, 0x00,       // JMP 0
    0x0F              // BRK
};

uint16_t pc = 0; // program counter

void setup()
{
    Serial.begin(9600);
    // initialise the digital pins as outputs.
    pinMode(pinA, OUTPUT);
    pinMode(pinB, OUTPUT);
    pinMode(pinC, OUTPUT);
    pinMode(pinD, OUTPUT);
    pinMode(pinE, OUTPUT);
    pinMode(pinF, OUTPUT);
    pinMode(pinG, OUTPUT);
    pinMode(D1, OUTPUT);
    pinMode(D2, OUTPUT);

    write_D1();
    print_F();

    runProgram();
}

void write_D1()
{
    digitalWrite(D1, HIGH);
    digitalWrite(D2, LOW);
}

void write_D2()
{
    digitalWrite(D1, LOW);
    digitalWrite(D2, HIGH);
}

void print_0() // writing 0
{
    digitalWrite(pinA, LOW);
    digitalWrite(pinB, LOW);
    digitalWrite(pinC, LOW);
    digitalWrite(pinD, LOW);
    digitalWrite(pinE, LOW);
    digitalWrite(pinF, LOW);
    digitalWrite(pinG, HIGH);
}

void print_1() // writing 1
{
    digitalWrite(pinA, HIGH);
    digitalWrite(pinB, LOW);
    digitalWrite(pinC, LOW);
    digitalWrite(pinD, HIGH);
    digitalWrite(pinE, HIGH);
    digitalWrite(pinF, HIGH);
    digitalWrite(pinG, HIGH);
}

void print_2() // writing 2
{
    digitalWrite(pinA, LOW);
    digitalWrite(pinB, LOW);
    digitalWrite(pinC, HIGH);
    digitalWrite(pinD, LOW);
    digitalWrite(pinE, LOW);
    digitalWrite(pinF, HIGH);
    digitalWrite(pinG, LOW);
}

void print_3() // writing 3
{
    digitalWrite(pinA, LOW);
    digitalWrite(pinB, LOW);
    digitalWrite(pinC, LOW);
    digitalWrite(pinD, LOW);
    digitalWrite(pinE, HIGH);
    digitalWrite(pinF, HIGH);
    digitalWrite(pinG, LOW);
}

void print_4() // writing 4
{
    digitalWrite(pinA, HIGH);
    digitalWrite(pinB, LOW);
    digitalWrite(pinC, LOW);
    digitalWrite(pinD, HIGH);
    digitalWrite(pinE, HIGH);
    digitalWrite(pinF, LOW);
    digitalWrite(pinG, LOW);
}

void print_5() // writing 5
{
    digitalWrite(pinA, LOW);
    digitalWrite(pinB, HIGH);
    digitalWrite(pinC, LOW);
    digitalWrite(pinD, LOW);
    digitalWrite(pinE, HIGH);
    digitalWrite(pinF, LOW);
    digitalWrite(pinG, LOW);
}

void print_6() // writing 6
{
    digitalWrite(pinA, LOW);
    digitalWrite(pinB, HIGH);
    digitalWrite(pinC, LOW);
    digitalWrite(pinD, LOW);
    digitalWrite(pinE, LOW);
    digitalWrite(pinF, LOW);
    digitalWrite(pinG, LOW);
}

void print_7() // writing 7
{
    digitalWrite(pinA, LOW);
    digitalWrite(pinB, LOW);
    digitalWrite(pinC, LOW);
    digitalWrite(pinD, HIGH);
    digitalWrite(pinE, HIGH);
    digitalWrite(pinF, HIGH);
    digitalWrite(pinG, HIGH);
}

void print_8() // writing 8
{
    digitalWrite(pinA, LOW);
    digitalWrite(pinB, LOW);
    digitalWrite(pinC, LOW);
    digitalWrite(pinD, LOW);
    digitalWrite(pinE, LOW);
    digitalWrite(pinF, LOW);
    digitalWrite(pinG, LOW);
}

void print_9() // writing 9
{
    digitalWrite(pinA, LOW);
    digitalWrite(pinB, LOW);
    digitalWrite(pinC, LOW);
    digitalWrite(pinD, LOW);
    digitalWrite(pinE, HIGH);
    digitalWrite(pinF, LOW);
    digitalWrite(pinG, LOW);
}

void print_A() // writing A
{
    digitalWrite(pinA, LOW);
    digitalWrite(pinB, LOW);
    digitalWrite(pinC, LOW);
    digitalWrite(pinD, HIGH);
    digitalWrite(pinE, LOW);
    digitalWrite(pinF, LOW);
    digitalWrite(pinG, LOW);
}

void print_B() // writing b
{
    digitalWrite(pinA, HIGH);
    digitalWrite(pinB, HIGH);
    digitalWrite(pinC, LOW);
    digitalWrite(pinD, LOW);
    digitalWrite(pinE, LOW);
    digitalWrite(pinF, LOW);
    digitalWrite(pinG, LOW);
}

void print_C() // writing C
{
    digitalWrite(pinA, LOW);
    digitalWrite(pinB, HIGH);
    digitalWrite(pinC, HIGH);
    digitalWrite(pinD, LOW);
    digitalWrite(pinE, LOW);
    digitalWrite(pinF, LOW);
    digitalWrite(pinG, HIGH);
}

void print_D() // writing d
{
    digitalWrite(pinA, HIGH);
    digitalWrite(pinB, LOW);
    digitalWrite(pinC, LOW);
    digitalWrite(pinD, LOW);
    digitalWrite(pinE, LOW);
    digitalWrite(pinF, HIGH);
    digitalWrite(pinG, LOW);
}

void print_E() // writing E
{
    digitalWrite(pinA, LOW);
    digitalWrite(pinB, HIGH);
    digitalWrite(pinC, HIGH);
    digitalWrite(pinD, LOW);
    digitalWrite(pinE, LOW);
    digitalWrite(pinF, LOW);
    digitalWrite(pinG, LOW);
}

void print_F() // writing F
{
    digitalWrite(pinA, LOW);
    digitalWrite(pinB, HIGH);
    digitalWrite(pinC, HIGH);
    digitalWrite(pinD, HIGH);
    digitalWrite(pinE, LOW);
    digitalWrite(pinF, LOW);
    digitalWrite(pinG, LOW);
}

void loop()
{
}

// === Zero flag helper ===
// Zero flag is stored in the least significant bit of R7
void set_zero_flag(uint8_t value)
{
    if (value == 0)
    {
        R[7] |= 0x01; // set bit 0
    }
    else
    {
        R[7] &= 0xFE; // clear bit 0
    }
}

bool get_zero_flag()
{
    return (R[7] & 0x01);
}

void runProgram()
{
    bool running = true;
    Serial.println("Starting...");
    while (running)
    {
        uint8_t opcode = program[pc++];
        switch (opcode)
        {
        case 0x01:
        { // DIS IMM
            uint8_t imm = program[pc++];
            Serial.print("DIS IMM ");
            display = imm;
            Serial.println(imm);
            set_zero_flag(imm);
            break;
        }
        case 0x02:
        { // DIS REG
            uint8_t reg = program[pc++] & 0x07;
            display = R[reg];
            Serial.print("DIS R");
            Serial.print(reg);
            Serial.print(" = ");
            Serial.println(R[reg]);
            set_zero_flag(R[reg]);
            break;
        }
        case 0x03:
        { // DIS ADDR
            uint8_t addr = program[pc++];
            display = program[addr];
            Serial.print("DIS MEM[");
            Serial.print(addr);
            Serial.print("] = ");
            Serial.println(program[addr]);
            set_zero_flag(program[addr]);
            break;
        }
        case 0x04:
        { // IN REG
            uint8_t reg = program[pc++] & 0x07;
            // For now: fake input from a memory-mapped address 0x80
            // Replace with digitalRead() or Serial.read() later
            uint8_t val = program[0x80] & 0xFF;
            R[reg] = val;
            Serial.print("IN R");
            Serial.print(reg);
            Serial.print(" <- MEM[0x80] (");
            Serial.print(val, BIN);
            Serial.println(")");
            set_zero_flag(R[reg]);
            break;
        }
        case 0x05:
        { // OUT IMM, IMM
            uint8_t port = program[pc++];
            uint8_t val = program[pc++];
            Serial.print("OUT port ");
            Serial.print(port);
            Serial.print(", value ");
            Serial.println(val);
            break;
        }
        case 0x06:
        { // OUT IMM, REG
            uint8_t port = program[pc++];
            uint8_t reg = program[pc++] & 0x07;
            Serial.print("OUT port ");
            Serial.print(port);
            Serial.print(", R");
            Serial.print(reg);
            Serial.print(" = ");
            Serial.println(R[reg]);
            break;
        }
        case 0x07:
        { // OUT IMM, ADDR
            uint8_t port = program[pc++];
            uint8_t addr = program[pc++];
            Serial.print("OUT port ");
            Serial.print(port);
            Serial.print(", MEM[");
            Serial.print(addr);
            Serial.print("] = ");
            Serial.println(program[addr]); // later replace with memory[]
            break;
        }
        case 0x0F:
        { // BRK
            Serial.println("BRK - Break / Halt");
            running = false;
            break;
        }
        // ==== MOV ====
        case 0x10:
        { // MOV REG, IMM
            uint8_t reg = program[pc++] & 0x07;
            uint8_t imm = program[pc++];
            uint8_t old = R[reg];
            R[reg] = imm;
            Serial.print("MOV R");
            Serial.print(reg);
            Serial.print(", ");
            Serial.print(imm);
            Serial.print(" | old=");
            Serial.print(old);
            Serial.print(" -> new=");
            Serial.println(R[reg]);
            set_zero_flag(R[reg]);
            break;
        }
        case 0x11:
        { // MOV ADDR, REG
            uint8_t addr = program[pc++];
            uint8_t reg = program[pc++] & 0x07;
            uint8_t old = program[addr];
            program[addr] = R[reg];
            Serial.print("MOV MEM[");
            Serial.print(addr);
            Serial.print("], R");
            Serial.print(reg);
            Serial.print(" | old=");
            Serial.print(old);
            Serial.print(" -> new=");
            Serial.println(program[addr]);
            set_zero_flag(program[addr]);
            break;
        }
        case 0x12:
        { // MOV REG, ADDR
            uint8_t reg = program[pc++] & 0x07;
            uint8_t addr = program[pc++];
            uint8_t old = R[reg];
            R[reg] = program[addr];
            Serial.print("MOV R");
            Serial.print(reg);
            Serial.print(", MEM[");
            Serial.print(addr);
            Serial.print("]");
            Serial.print(" | old=");
            Serial.print(old);
            Serial.print(" -> new=");
            Serial.println(R[reg]);
            set_zero_flag(R[reg]);
            break;
        }
        case 0x13:
        { // MOV REG, REG
            uint8_t reg1 = program[pc++] & 0x07;
            uint8_t reg2 = program[pc++] & 0x07;
            uint8_t old = R[reg1];
            R[reg1] = R[reg2];
            Serial.print("MOV R");
            Serial.print(reg1);
            Serial.print(", R");
            Serial.print(reg2);
            Serial.print(" | old=");
            Serial.print(old);
            Serial.print(" -> new=");
            Serial.println(R[reg1]);
            set_zero_flag(R[reg1]);
            break;
        }

        // ==== SHW ====
        case 0x14:
        { // SHW
            Serial.println("SHW - Show memory 0x00–0x7F:");
            // for (uint16_t i = 0; i < 0x80; i++) {
            // if (i % 16 == 0) {
            // Serial.println();
            // Serial.print("0x");
            // if (i < 0x10) Serial.print("0");
            // Serial.print(i, HEX);
            // Serial.print(": ");
            // }
            // if (program[i] < 0x10) Serial.print("0");
            // Serial.print(program[i], HEX);
            // Serial.print(" ");
            // }
            // Serial.println();
            break;
        }

        // ==== CLS ====
        case 0x15:
        { // CLS
            uint8_t color = program[pc++];
            Serial.print("CLS - Clear screen to color ");
            Serial.println(color);
            break;
        }

        // ==== Shifts & Rotates ====
        case 0x18:
        { // SBL REG
            uint8_t reg = program[pc++] & 0x07;
            R[reg] = (R[reg] << 1) & 0xFF;
            Serial.print("SBL R");
            Serial.print(reg);
            Serial.print(" -> ");
            Serial.println(R[reg], HEX);
            set_zero_flag(R[reg]);
            break;
        }
        case 0x19:
        { // SBL ADDR
            uint8_t addr = program[pc++];
            program[addr] = (program[addr] << 1) & 0xFF;
            Serial.print("SBL MEM[");
            Serial.print(addr);
            Serial.print("] -> ");
            Serial.println(program[addr], HEX);
            set_zero_flag(program[addr]);
            break;
        }
        case 0x1A:
        { // SBR REG
            uint8_t reg = program[pc++] & 0x07;
            R[reg] = (R[reg] >> 1) & 0xFF;
            Serial.print("SBR R");
            Serial.print(reg);
            Serial.print(" -> ");
            Serial.println(R[reg], HEX);
            set_zero_flag(R[reg]);
            break;
        }
        case 0x1B:
        { // SBR ADDR
            uint8_t addr = program[pc++];
            program[addr] = (program[addr] >> 1) & 0xFF;
            Serial.print("SBR MEM[");
            Serial.print(addr);
            Serial.print("] -> ");
            Serial.println(program[addr], HEX);
            set_zero_flag(program[addr]);
            break;
        }
        case 0x1C:
        { // RBL REG
            uint8_t reg = program[pc++] & 0x07;
            uint8_t val = R[reg];
            R[reg] = ((val << 1) & 0xFF) | ((val >> 7) & 0x01);
            Serial.print("RBL R");
            Serial.print(reg);
            Serial.print(" -> ");
            Serial.println(R[reg], HEX);
            set_zero_flag(R[reg]);
            break;
        }
        case 0x1D:
        { // RBL ADDR
            uint8_t addr = program[pc++];
            uint8_t val = program[addr];
            program[addr] = ((val << 1) & 0xFF) | ((val >> 7) & 0x01);
            Serial.print("RBL MEM[");
            Serial.print(addr);
            Serial.print("] -> ");
            Serial.println(program[addr], HEX);
            set_zero_flag(program[addr]);
            break;
        }
        case 0x1E:
        { // RBR REG
            uint8_t reg = program[pc++] & 0x07;
            uint8_t val = R[reg];
            R[reg] = ((val >> 1) & 0xFF) | ((val & 0x01) << 7);
            Serial.print("RBR R");
            Serial.print(reg);
            Serial.print(" -> ");
            Serial.println(R[reg], HEX);
            set_zero_flag(R[reg]);
            break;
        }
        case 0x1F:
        { // RBR ADDR
            uint8_t addr = program[pc++];
            uint8_t val = program[addr];
            program[addr] = ((val >> 1) & 0xFF) | ((val & 0x01) << 7);
            Serial.print("RBR MEM[");
            Serial.print(addr);
            Serial.print("] -> ");
            Serial.println(program[addr], HEX);
            set_zero_flag(program[addr]);
            break;
        }
        // === AND ===
        case 0x20:
        { // AND REG, IMM
            uint8_t reg = program[pc++] & 0x07;
            uint8_t imm = program[pc++];
            uint8_t old = R[reg];
            R[reg] = (R[reg] & imm) & 0xFF;
            set_zero_flag(R[reg]);
            Serial.print("AND R");
            Serial.print(reg);
            Serial.print(", 0x");
            Serial.print(imm, HEX);
            Serial.print(" | 0x");
            Serial.print(old, HEX);
            Serial.print(" & 0x");
            Serial.print(imm, HEX);
            Serial.print(" = 0x");
            Serial.println(R[reg], HEX);
            break;
        }
        case 0x21:
        { // AND ADDR, REG
            uint8_t addr = program[pc++];
            uint8_t reg = program[pc++] & 0x07;
            uint8_t old = program[addr];
            program[addr] = (program[addr] & R[reg]) & 0xFF;
            set_zero_flag(program[addr]);
            Serial.print("AND MEM[");
            Serial.print(addr);
            Serial.print("], R");
            Serial.print(reg);
            Serial.print(" | 0x");
            Serial.print(old, HEX);
            Serial.print(" & 0x");
            Serial.print(R[reg], HEX);
            Serial.print(" = 0x");
            Serial.println(program[addr], HEX);
            break;
        }
        case 0x22:
        { // AND REG, ADDR
            uint8_t reg = program[pc++] & 0x07;
            uint8_t addr = program[pc++];
            uint8_t old = R[reg];
            R[reg] = (R[reg] & program[addr]) & 0xFF;
            set_zero_flag(R[reg]);
            Serial.print("AND R");
            Serial.print(reg);
            Serial.print(", MEM[");
            Serial.print(addr);
            Serial.print("]");
            Serial.print(" | 0x");
            Serial.print(old, HEX);
            Serial.print(" & 0x");
            Serial.print(program[addr], HEX);
            Serial.print(" = 0x");
            Serial.println(R[reg], HEX);
            break;
        }
        case 0x23:
        { // AND REG, REG
            uint8_t reg1 = program[pc++] & 0x07;
            uint8_t reg2 = program[pc++] & 0x07;
            uint8_t old = R[reg1];
            R[reg1] = (R[reg1] & R[reg2]) & 0xFF;
            set_zero_flag(R[reg1]);
            Serial.print("AND R");
            Serial.print(reg1);
            Serial.print(", R");
            Serial.print(reg2);
            Serial.print(" | 0x");
            Serial.print(old, HEX);
            Serial.print(" & 0x");
            Serial.print(R[reg2], HEX);
            Serial.print(" = 0x");
            Serial.println(R[reg1], HEX);
            break;
        }

        // === OR ===
        case 0x24:
        { // OR REG, IMM
            uint8_t reg = program[pc++] & 0x07;
            uint8_t imm = program[pc++];
            uint8_t old = R[reg];
            R[reg] = (R[reg] | imm) & 0xFF;
            set_zero_flag(R[reg]);
            Serial.print("OR R");
            Serial.print(reg);
            Serial.print(", 0x");
            Serial.print(imm, HEX);
            Serial.print(" | 0x");
            Serial.print(old, HEX);
            Serial.print(" | 0x");
            Serial.print(imm, HEX);
            Serial.print(" = 0x");
            Serial.println(R[reg], HEX);
            break;
        }
        case 0x25:
        { // OR ADDR, REG
            uint8_t addr = program[pc++];
            uint8_t reg = program[pc++] & 0x07;
            uint8_t old = program[addr];
            program[addr] = (program[addr] | R[reg]) & 0xFF;
            set_zero_flag(program[addr]);
            Serial.print("OR MEM[");
            Serial.print(addr);
            Serial.print("], R");
            Serial.print(reg);
            Serial.print(" | 0x");
            Serial.print(old, HEX);
            Serial.print(" | 0x");
            Serial.print(R[reg], HEX);
            Serial.print(" = 0x");
            Serial.println(program[addr], HEX);
            break;
        }
        case 0x26:
        { // OR REG, ADDR
            uint8_t reg = program[pc++] & 0x07;
            uint8_t addr = program[pc++];
            uint8_t old = R[reg];
            R[reg] = (R[reg] | program[addr]) & 0xFF;
            set_zero_flag(R[reg]);
            Serial.print("OR R");
            Serial.print(reg);
            Serial.print(", MEM[");
            Serial.print(addr);
            Serial.print("]");
            Serial.print(" | 0x");
            Serial.print(old, HEX);
            Serial.print(" | 0x");
            Serial.print(program[addr], HEX);
            Serial.print(" = 0x");
            Serial.println(R[reg], HEX);
            break;
        }
        case 0x27:
        { // OR REG, REG
            uint8_t reg1 = program[pc++] & 0x07;
            uint8_t reg2 = program[pc++] & 0x07;
            uint8_t old = R[reg1];
            R[reg1] = (R[reg1] | R[reg2]) & 0xFF;
            set_zero_flag(R[reg1]);
            Serial.print("OR R");
            Serial.print(reg1);
            Serial.print(", R");
            Serial.print(reg2);
            Serial.print(" | 0x");
            Serial.print(old, HEX);
            Serial.print(" | 0x");
            Serial.print(R[reg2], HEX);
            Serial.print(" = 0x");
            Serial.println(R[reg1], HEX);
            break;
        }

        // === XOR ===
        case 0x28:
        { // XOR REG, IMM
            uint8_t reg = program[pc++] & 0x07;
            uint8_t imm = program[pc++];
            uint8_t old = R[reg];
            R[reg] = (R[reg] ^ imm) & 0xFF;
            set_zero_flag(R[reg]);
            Serial.print("XOR R");
            Serial.print(reg);
            Serial.print(", 0x");
            Serial.print(imm, HEX);
            Serial.print(" | 0x");
            Serial.print(old, HEX);
            Serial.print(" ^ 0x");
            Serial.print(imm, HEX);
            Serial.print(" = 0x");
            Serial.println(R[reg], HEX);
            break;
        }
        case 0x29:
        { // XOR ADDR, REG
            uint8_t addr = program[pc++];
            uint8_t reg = program[pc++] & 0x07;
            uint8_t old = program[addr];
            program[addr] = (program[addr] ^ R[reg]) & 0xFF;
            set_zero_flag(program[addr]);
            Serial.print("XOR MEM[");
            Serial.print(addr);
            Serial.print("], R");
            Serial.print(reg);
            Serial.print(" | 0x");
            Serial.print(old, HEX);
            Serial.print(" ^ 0x");
            Serial.print(R[reg], HEX);
            Serial.print(" = 0x");
            Serial.println(program[addr], HEX);
            break;
        }
        case 0x2A:
        { // XOR REG, ADDR
            uint8_t reg = program[pc++] & 0x07;
            uint8_t addr = program[pc++];
            uint8_t old = R[reg];
            R[reg] = (R[reg] ^ program[addr]) & 0xFF;
            set_zero_flag(R[reg]);
            Serial.print("XOR R");
            Serial.print(reg);
            Serial.print(", MEM[");
            Serial.print(addr);
            Serial.print("]");
            Serial.print(" | 0x");
            Serial.print(old, HEX);
            Serial.print(" ^ 0x");
            Serial.print(program[addr], HEX);
            Serial.print(" = 0x");
            Serial.println(R[reg], HEX);
            break;
        }
        case 0x2B:
        { // XOR REG, REG
            uint8_t reg1 = program[pc++] & 0x07;
            uint8_t reg2 = program[pc++] & 0x07;
            uint8_t old = R[reg1];
            R[reg1] = (R[reg1] ^ R[reg2]) & 0xFF;
            set_zero_flag(R[reg1]);
            Serial.print("XOR R");
            Serial.print(reg1);
            Serial.print(", R");
            Serial.print(reg2);
            Serial.print(" | 0x");
            Serial.print(old, HEX);
            Serial.print(" ^ 0x");
            Serial.print(R[reg2], HEX);
            Serial.print(" = 0x");
            Serial.println(R[reg1], HEX);
            break;
        }

        // === NOT ===
        case 0x2C:
        { // NOT REG
            uint8_t reg = program[pc++] & 0x07;
            uint8_t old = R[reg];
            R[reg] = (~R[reg]) & 0xFF;
            set_zero_flag(R[reg]);
            Serial.print("NOT R");
            Serial.print(reg);
            Serial.print(" | ~0x");
            Serial.print(old, HEX);
            Serial.print(" = 0x");
            Serial.println(R[reg], HEX);
            break;
        }
        case 0x2D:
        { // NOT ADDR
            uint8_t addr = program[pc++];
            uint8_t old = program[addr];
            program[addr] = (~program[addr]) & 0xFF;
            set_zero_flag(program[addr]);
            Serial.print("NOT MEM[");
            Serial.print(addr);
            Serial.print("]");
            Serial.print(" | ~0x");
            Serial.print(old, HEX);
            Serial.print(" = 0x");
            Serial.println(program[addr], HEX);
            break;
        }
        // === ADD ===
        case 0x30:
        { // ADD REG, IMM
            uint8_t reg = program[pc++] & 0x07;
            uint8_t imm = program[pc++];
            uint8_t old = R[reg];
            R[reg] = (R[reg] + imm) & 0xFF;
            set_zero_flag(R[reg]);
            Serial.print("ADD R");
            Serial.print(reg);
            Serial.print(", ");
            Serial.print(imm);
            Serial.print(" | ");
            Serial.print(old);
            Serial.print(" + ");
            Serial.print(imm);
            Serial.print(" = ");
            Serial.println(R[reg]);
            break;
        }
        case 0x31:
        { // ADD ADDR, REG
            uint8_t addr = program[pc++];
            uint8_t reg = program[pc++] & 0x07;
            uint8_t old = program[addr];
            program[addr] = (program[addr] + R[reg]) & 0xFF;
            set_zero_flag(program[addr]);
            Serial.print("ADD MEM[");
            Serial.print(addr);
            Serial.print("], R");
            Serial.print(reg);
            Serial.print(" | ");
            Serial.print(old);
            Serial.print(" + ");
            Serial.print(R[reg]);
            Serial.print(" = ");
            Serial.println(program[addr]);
            break;
        }
        case 0x32:
        { // ADD REG, ADDR
            uint8_t reg = program[pc++] & 0x07;
            uint8_t addr = program[pc++];
            uint8_t old = R[reg];
            R[reg] = (R[reg] + program[addr]) & 0xFF;
            set_zero_flag(R[reg]);
            Serial.print("ADD R");
            Serial.print(reg);
            Serial.print(", MEM[");
            Serial.print(addr);
            Serial.print("]");
            Serial.print(" | ");
            Serial.print(old);
            Serial.print(" + ");
            Serial.print(program[addr]);
            Serial.print(" = ");
            Serial.println(R[reg]);
            break;
        }
        case 0x33:
        { // ADD REG, REG
            uint8_t reg1 = program[pc++] & 0x07;
            uint8_t reg2 = program[pc++] & 0x07;
            uint8_t old = R[reg1];
            R[reg1] = (R[reg1] + R[reg2]) & 0xFF;
            set_zero_flag(R[reg1]);
            Serial.print("ADD R");
            Serial.print(reg1);
            Serial.print(", R");
            Serial.print(reg2);
            Serial.print(" | ");
            Serial.print(old);
            Serial.print(" + ");
            Serial.print(R[reg2]);
            Serial.print(" = ");
            Serial.println(R[reg1]);
            break;
        }

        // === SUB ===
        case 0x34:
        { // SUB REG, IMM
            uint8_t reg = program[pc++] & 0x07;
            uint8_t imm = program[pc++];
            uint8_t old = R[reg];
            R[reg] = (R[reg] - imm) & 0xFF;
            set_zero_flag(R[reg]);
            Serial.print("SUB R");
            Serial.print(reg);
            Serial.print(", ");
            Serial.print(imm);
            Serial.print(" | ");
            Serial.print(old);
            Serial.print(" - ");
            Serial.print(imm);
            Serial.print(" = ");
            Serial.println(R[reg]);
            break;
        }
        case 0x35:
        { // SUB ADDR, REG
            uint8_t addr = program[pc++];
            uint8_t reg = program[pc++] & 0x07;
            uint8_t old = program[addr];
            program[addr] = (program[addr] - R[reg]) & 0xFF;
            set_zero_flag(program[addr]);
            Serial.print("SUB MEM[");
            Serial.print(addr);
            Serial.print("], R");
            Serial.print(reg);
            Serial.print(" | ");
            Serial.print(old);
            Serial.print(" - ");
            Serial.print(R[reg]);
            Serial.print(" = ");
            Serial.println(program[addr]);
            break;
        }
        case 0x36:
        { // SUB REG, ADDR
            uint8_t reg = program[pc++] & 0x07;
            uint8_t addr = program[pc++];
            uint8_t old = R[reg];
            R[reg] = (R[reg] - program[addr]) & 0xFF;
            set_zero_flag(R[reg]);
            Serial.print("SUB R");
            Serial.print(reg);
            Serial.print(", MEM[");
            Serial.print(addr);
            Serial.print("]");
            Serial.print(" | ");
            Serial.print(old);
            Serial.print(" - ");
            Serial.print(program[addr]);
            Serial.print(" = ");
            Serial.println(R[reg]);
            break;
        }
        case 0x37:
        { // SUB REG, REG
            uint8_t reg1 = program[pc++] & 0x07;
            uint8_t reg2 = program[pc++] & 0x07;
            uint8_t old = R[reg1];
            R[reg1] = (R[reg1] - R[reg2]) & 0xFF;
            set_zero_flag(R[reg1]);
            Serial.print("SUB R");
            Serial.print(reg1);
            Serial.print(", R");
            Serial.print(reg2);
            Serial.print(" | ");
            Serial.print(old);
            Serial.print(" - ");
            Serial.print(R[reg2]);
            Serial.print(" = ");
            Serial.println(R[reg1]);
            break;
        }

        // === INC ===
        case 0x38:
        { // INC REG
            uint8_t reg = program[pc++] & 0x07;
            uint8_t old = R[reg];
            R[reg] = (R[reg] + 1) & 0xFF;
            set_zero_flag(R[reg]);
            Serial.print("INC R");
            Serial.print(reg);
            Serial.print(" | ");
            Serial.print(old);
            Serial.print(" + 1 = ");
            Serial.println(R[reg]);
            break;
        }
        case 0x39:
        { // INC ADDR
            uint8_t addr = program[pc++];
            uint8_t old = program[addr];
            program[addr] = (program[addr] + 1) & 0xFF;
            set_zero_flag(program[addr]);
            Serial.print("INC MEM[");
            Serial.print(addr);
            Serial.print("] | ");
            Serial.print(old);
            Serial.print(" + 1 = ");
            Serial.println(program[addr]);
            break;
        }

        // === DEC ===
        case 0x3A:
        { // DEC REG
            uint8_t reg = program[pc++] & 0x07;
            uint8_t old = R[reg];
            R[reg] = (R[reg] - 1) & 0xFF;
            set_zero_flag(R[reg]);
            Serial.print("DEC R");
            Serial.print(reg);
            Serial.print(" | ");
            Serial.print(old);
            Serial.print(" - 1 = ");
            Serial.println(R[reg]);
            break;
        }
        case 0x3B:
        { // DEC ADDR
            uint8_t addr = program[pc++];
            uint8_t old = program[addr];
            program[addr] = (program[addr] - 1) & 0xFF;
            set_zero_flag(program[addr]);
            Serial.print("DEC MEM[");
            Serial.print(addr);
            Serial.print("] | ");
            Serial.print(old);
            Serial.print(" - 1 = ");
            Serial.println(program[addr]);
            break;
        }
        // === JUMPING ===
        case 0x40:
        { // JMP IMM
            uint8_t addr = program[pc++];
            Serial.print("JMP 0x");
            Serial.print(addr, HEX);
            Serial.print(" | jumping to ");
            Serial.println(addr);
            if (addr < sizeof(program))
            {
                pc = addr;
            }
            break;
        }
        case 0x41:
        { // JMP REG
            uint8_t reg = program[pc++] & 0x07;
            Serial.print("JMP R");
            Serial.print(reg);
            Serial.print(" | jumping to ");
            Serial.println(R[reg]);
            if (R[reg] < sizeof(program))
            {
                pc = R[reg];
            }
            break;
        }
        case 0x42:
        { // JIF IMM, IMM
            uint8_t imm1 = program[pc++];
            uint8_t addr = program[pc++];
            bool cond = imm1 & 0x01;
            bool taken = cond && get_zero_flag();
            Serial.print("JIF ");
            Serial.print(imm1);
            Serial.print(", 0x");
            Serial.print(addr, HEX);
            Serial.print(" | cond=");
            Serial.print(cond);
            Serial.print(", ZF=");
            Serial.print(get_zero_flag());
            Serial.print(" -> ");
            Serial.println(taken ? "taken" : "not taken");
            if (taken && addr < sizeof(program))
            {
                pc = addr;
            }
            break;
        }
        case 0x43:
        { // JIF IMM, REG
            uint8_t imm = program[pc++];
            uint8_t reg = program[pc++] & 0x07;
            bool cond = imm & 0x01;
            bool taken = cond && get_zero_flag();
            Serial.print("JIF ");
            Serial.print(imm);
            Serial.print(", R");
            Serial.print(reg);
            Serial.print(" | cond=");
            Serial.print(cond);
            Serial.print(", ZF=");
            Serial.print(get_zero_flag());
            Serial.print(" -> ");
            Serial.println(taken ? "taken" : "not taken");
            if (taken && R[reg] < sizeof(program))
            {
                pc = R[reg];
            }
            break;
        }
        case 0x44:
        { // JNI IMM, IMM
            uint8_t imm1 = program[pc++];
            uint8_t addr = program[pc++];
            bool cond = imm1 & 0x01;
            bool taken = cond && !get_zero_flag();
            Serial.print("JNI ");
            Serial.print(imm1);
            Serial.print(", 0x");
            Serial.print(addr, HEX);
            Serial.print(" | cond=");
            Serial.print(cond);
            Serial.print(", ZF=");
            Serial.print(get_zero_flag());
            Serial.print(" -> ");
            Serial.println(taken ? "taken" : "not taken");
            if (taken && addr < sizeof(program))
            {
                pc = addr;
            }
            break;
        }
        case 0x45:
        { // JNI IMM, REG
            uint8_t imm = program[pc++];
            uint8_t reg = program[pc++] & 0x07;
            bool cond = imm & 0x01;
            bool taken = cond && !get_zero_flag();
            Serial.print("JNI ");
            Serial.print(imm);
            Serial.print(", R");
            Serial.print(reg);
            Serial.print(" | cond=");
            Serial.print(cond);
            Serial.print(", ZF=");
            Serial.print(get_zero_flag());
            Serial.print(" -> ");
            Serial.println(taken ? "taken" : "not taken");
            if (taken && R[reg] < sizeof(program))
            {
                pc = R[reg];
            }
            break;
        }

        // === Move Indirect Location (MIL) ===
        case 0x50:
        { // MIL REG, IMM
            uint8_t reg = program[pc++] & 0x07;
            uint8_t imm = program[pc++];
            uint8_t addr = R[reg];
            uint8_t old = program[addr];
            program[addr] = imm;
            set_zero_flag(R[reg]);
            Serial.print("MIL R");
            Serial.print(reg);
            Serial.print(", ");
            Serial.print(imm);
            Serial.print(" | old=");
            Serial.print(old);
            Serial.print(" -> new=");
            Serial.println(program[addr]);
            break;
        }
        case 0x51:
        { // MIL REG, REG
            uint8_t reg1 = program[pc++] & 0x07;
            uint8_t reg2 = program[pc++] & 0x07;
            uint8_t addr = R[reg1];
            uint8_t old = program[addr];
            program[addr] = R[reg2];
            set_zero_flag(R[reg1]);
            Serial.print("MIL R");
            Serial.print(reg1);
            Serial.print(", R");
            Serial.print(reg2);
            Serial.print(" | old=");
            Serial.print(old);
            Serial.print(" -> new=");
            Serial.println(program[addr]);
            break;
        }
        case 0x52:
        { // MIL REG, ADDR
            uint8_t reg = program[pc++] & 0x07;
            uint8_t addr2 = program[pc++];
            uint8_t addr1 = R[reg];
            uint8_t old = program[addr1];
            program[addr1] = program[addr2];
            set_zero_flag(R[reg]);
            Serial.print("MIL R");
            Serial.print(reg);
            Serial.print(", MEM[");
            Serial.print(addr2);
            Serial.print("]");
            Serial.print(" | old=");
            Serial.print(old);
            Serial.print(" -> new=");
            Serial.println(program[addr1]);
            break;
        }
        case 0x53:
        { // MIL ADDR, REG
            uint8_t addr1 = program[pc++];
            uint8_t reg = program[pc++] & 0x07;
            uint8_t addr2 = program[addr1];
            uint8_t old = program[addr2];
            program[addr2] = R[reg];
            set_zero_flag(program[addr2]);
            Serial.print("MIL MEM[");
            Serial.print(addr1);
            Serial.print("], R");
            Serial.print(reg);
            Serial.print(" | old=");
            Serial.print(old);
            Serial.print(" -> new=");
            Serial.println(program[addr2]);
            break;
        }

        // === Move From Indirect (MFI) ===
        case 0x54:
        { // MFI REG, REG
            uint8_t reg1 = program[pc++] & 0x07;
            uint8_t reg2 = program[pc++] & 0x07;
            uint8_t old = R[reg1];
            R[reg1] = program[R[reg2]];
            set_zero_flag(R[reg1]);
            Serial.print("MFI R");
            Serial.print(reg1);
            Serial.print(", R");
            Serial.print(reg2);
            Serial.print(" | old=");
            Serial.print(old);
            Serial.print(" -> new=");
            Serial.println(R[reg1]);
            break;
        }
        case 0x55:
        { // MFI REG, ADDR
            uint8_t reg = program[pc++] & 0x07;
            uint8_t addr2 = program[pc++];
            uint8_t addr1 = program[addr2];
            uint8_t old = R[reg];
            R[reg] = program[addr1];
            set_zero_flag(R[reg]);
            Serial.print("MFI R");
            Serial.print(reg);
            Serial.print(", MEM[");
            Serial.print(addr2);
            Serial.print("] | old=");
            Serial.print(old);
            Serial.print(" -> new=");
            Serial.println(R[reg]);
            break;
        }
        case 0x56:
        { // MFI ADDR, REG
            uint8_t addr1 = program[pc++];
            uint8_t reg = program[pc++] & 0x07;
            uint8_t addr2 = R[reg];
            uint8_t old = program[addr1];
            program[addr1] = program[addr2];
            set_zero_flag(program[addr1]);
            Serial.print("MFI MEM[");
            Serial.print(addr1);
            Serial.print("], R");
            Serial.print(reg);
            Serial.print(" | old=");
            Serial.print(old);
            Serial.print(" -> new=");
            Serial.println(program[addr1]);
            break;
        }
        case 0x57:
        { // MFI ADDR, ADDR
            uint8_t addr1 = program[pc++];
            uint8_t addr2 = program[pc++];
            uint8_t addr3 = program[addr2];
            uint8_t old = program[addr1];
            program[addr1] = program[addr3];
            set_zero_flag(program[addr1]);
            Serial.print("MFI MEM[");
            Serial.print(addr1);
            Serial.print("], MEM[");
            Serial.print(addr2);
            Serial.print("] | old=");
            Serial.print(old);
            Serial.print(" -> new=");
            Serial.println(program[addr1]);
            break;
        }
        default:
            Serial.print("Unknown opcode: ");
            Serial.println(opcode, HEX);
            running = false;
            break;
        }

        // Static flag to keep track of which display to write to
        static bool writeToD1 = true; // starts with D1

        // Extract nibble from 'display'
        byte nibble = writeToD1 ? (display >> 4) : (display & 0x0F);

        // Write to the correct display
        if (writeToD1)
        {
            write_D1();
        }
        else
        {
            write_D2();
        }

        // Call the appropriate print function based on nibble
        switch (nibble)
        {
        case 0x0:
            print_0();
            break;
        case 0x1:
            print_1();
            break;
        case 0x2:
            print_2();
            break;
        case 0x3:
            print_3();
            break;
        case 0x4:
            print_4();
            break;
        case 0x5:
            print_5();
            break;
        case 0x6:
            print_6();
            break;
        case 0x7:
            print_7();
            break;
        case 0x8:
            print_8();
            break;
        case 0x9:
            print_9();
            break;
        case 0xA:
            print_A();
            break;
        case 0xB:
            print_B();
            break;
        case 0xC:
            print_C();
            break;
        case 0xD:
            print_D();
            break;
        case 0xE:
            print_E();
            break;
        case 0xF:
            print_F();
            break;
        }

        // Flip for next frame
        writeToD1 = !writeToD1;
    }
}
