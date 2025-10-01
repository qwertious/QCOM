import sys
import re

# Operand type constants
REG = "REG"
ADDR = "ADDR"
IMM = "IMM"
LABEL = "LABEL"

# Instruction modes - updated to accept LABEL where relevant
INSTRUCTION_MODES = {
    ("DIS", (IMM,)): 0x01,
    ("DIS", (REG,)): 0x02,
    ("DIS", (ADDR,)): 0x03,
    ("IN", (REG,)): 0x04,
    ("OUT", (IMM, IMM)): 0x05,
    ("OUT", (IMM, REG)): 0x06,
    ("OUT", (IMM, ADDR)): 0x07,
    ("BRK", ()): 0x0F,
    ("MOV", (REG, IMM)): 0x10,
    ("MOV", (ADDR, REG)): 0x11,
    ("MOV", (REG, ADDR)): 0x12,
    ("MOV", (REG, REG)): 0x13,
    ("SHW", ()): 0x14,
    ("CLS", (IMM,)): 0x15,
    ("SBL", (REG,)): 0x18,
    ("SBL", (ADDR,)): 0x19,
    ("SBR", (REG,)): 0x1A,
    ("SBR", (ADDR,)): 0x1B,
    ("RBL", (REG,)): 0x1C,
    ("RBL", (ADDR,)): 0x1D,
    ("RBR", (REG,)): 0x1E,
    ("RBR", (ADDR,)): 0x1F,
    ("AND", (REG, IMM)): 0x20,
    ("AND", (ADDR, REG)): 0x21,
    ("AND", (REG, ADDR)): 0x22,
    ("AND", (REG, REG)): 0x23,
    ("OR", (REG, IMM)): 0x24,
    ("OR", (ADDR, REG)): 0x25,
    ("OR", (REG, ADDR)): 0x26,
    ("OR", (REG, REG)): 0x27,
    ("XOR", (REG, IMM)): 0x28,
    ("XOR", (ADDR, REG)): 0x29,
    ("XOR", (REG, ADDR)): 0x2A,
    ("XOR", (REG, REG)): 0x2B,
    ("NOT", (REG,)): 0x2C,
    ("NOT", (ADDR,)): 0x2D,
    ("NOT", (REG, IMM)): 0x2E,
    ("NOT", (ADDR, REG)): 0x2F,
    ("ADD", (REG, IMM)): 0x30,
    ("ADD", (ADDR, REG)): 0x31,
    ("ADD", (REG, ADDR)): 0x32,
    ("ADD", (REG, REG)): 0x33,
    ("SUB", (REG, IMM)): 0x34,
    ("SUB", (IMM, REG)): 0x35,
    ("SUB", (REG, ADDR)): 0x36,
    ("SUB", (REG, REG)): 0x37,
    ("INC", (REG,)): 0x38,
    ("INC", (ADDR,)): 0x39,
    ("INC", (REG, ADDR)): 0x3A,
    ("INC", (ADDR, REG)): 0x3B,
    ("DEC", (REG,)): 0x3C,
    ("DEC", (ADDR,)): 0x3D,
    ("DEC", (REG, ADDR)): 0x3E,
    ("DEC", (ADDR, REG)): 0x3F,
    ("JMP", (IMM,)): 0x40,
    ("JMP", (REG,)): 0x41,
    ("JIF", (IMM, IMM)): 0x42,
    ("JIF", (IMM, REG)): 0x43,
    ("JNI", (IMM, IMM)): 0x44,
    ("JNI", (IMM, REG)): 0x45,
    ("PSH", (IMM,)): 0x46,
    ("PSH", (REG,)): 0x47,
    ("POP", ()): 0x48,
    ("PIF", (IMM, IMM)): 0x49,
    ("PIF", (IMM, REG)): 0x4A,
    ("PNI", (IMM, IMM)): 0x4B,
    ("PNI", (IMM, REG)): 0x4C,
    ("MIL", (REG, IMM)): 0x50,
    ("MIL", (REG, REG)): 0x51,
    ("MIL", (REG, ADDR)): 0x52,
    ("MIL", (ADDR, REG)): 0x53,
    ("MFI", (REG, REG)): 0x54,
    ("MFI", (REG, ADDR)): 0x55,
    ("MFI", (ADDR, REG)): 0x56,
    ("MFI", (ADDR, ADDR)): 0x57,
}


def adjust_modes_for_labels():
    new_modes = {}
    for (instr, operands), opcode in INSTRUCTION_MODES.items():
        if instr in ("JMP", "JIF", "JNI", "PSH", "PIF", "PNI"):
            operands_with_labels = tuple(LABEL if op == IMM else op for op in operands)
            new_modes[(instr, operands_with_labels)] = opcode
        new_modes[(instr, operands)] = opcode
    return new_modes


INSTRUCTION_MODES = adjust_modes_for_labels()


def detect_operand_type(operand):
    if re.fullmatch(r"R[0-7]", operand):
        return REG
    elif operand.startswith("#") and re.fullmatch(r"#\w+", operand):
        return LABEL
    elif operand.startswith("$"):
        return IMM
    elif re.fullmatch(r"0x[0-9A-Fa-f]+", operand):
        return ADDR
    elif re.fullmatch(r"0b[01]+", operand):
        return ADDR
    elif operand.isdigit():
        return ADDR
    else:
        return None


def parse_operand(operand, operand_type, labels=None, line_num=None, resolve_labels=True):
    """Convert operand string to a numeric byte value."""
    try:
        # ===== Handle label reference =====
        if operand.startswith("#"):
            print(f"Parsing operand '{operand}' on line {line_num}")
            if not resolve_labels:
                # First pass: return dummy value for label operands
                return 0
            if labels is None:
                raise ValueError(f"Line {line_num}: Label resolution failed — no label table provided.")
            if operand not in labels:
                raise ValueError(f"Line {line_num}: Undefined label reference: {operand}")
            return labels[operand]

        # ===== Regular operand handling =====
        if operand_type == REG:
            return int(operand[1])  # e.g., "R2" -> 2

        elif operand_type == IMM:
            if operand.startswith("$"):
                value = operand[1:]  # Remove leading $
                if value.startswith("0x"):
                    return int(value, 16)
                elif value.startswith("0b"):
                    return int(value, 2)
                else:
                    return int(value)  # Decimal
            else:
                return int(operand)  # Decimal fallback

        elif operand_type == ADDR:
            if operand.startswith("0x"):
                return int(operand, 16)
            elif operand.startswith("0b"):
                return int(operand, 2)
            else:
                return int(operand)  # Decimal

        else:
            raise ValueError(f"Unknown operand type: {operand_type}")

    except ValueError:
        raise ValueError(f"Line {line_num}: Invalid number format: {operand}")

def strip_comments(line: str) -> str:
    # Remove everything after the first "/"
    return line.split("/", 1)[0].strip()

def compile_line(line, line_num, labels=None, current_offset=None, resolve_labels=True):
    parts = line.strip().split()
    if len(parts) < 1:
        raise ValueError(f"Line {line_num}: Empty or invalid instruction.")

    instr = parts[0].upper()
    operands = parts[1:]

    detected_types = [detect_operand_type(op) for op in operands]
    if None in detected_types:
        raise ValueError(f"Line {line_num}: Invalid operand(s): {operands}")

    # Treat LABEL as IMM for matching
    match_types = tuple(IMM if t == LABEL else t for t in detected_types)

    matched_key = None
    for (key_instr, key_operand_types), opcode in INSTRUCTION_MODES.items():
        if key_instr != instr:
            continue
        if len(key_operand_types) != len(operands):
            continue
        if key_operand_types == match_types:
            matched_key = (key_instr, key_operand_types)
            break

    if not matched_key:
        raise ValueError(f"Line {line_num}: Unsupported instruction or operand types for '{instr}'")

    opcode = INSTRUCTION_MODES[matched_key]
    compiled_bytes = [opcode]

    injected = bytearray()

    for op, typ in zip(operands, detected_types):
        if typ == LABEL:
            if not resolve_labels:
                # First pass: fake page setup (placeholder page 0)
                injected.extend([
                    INSTRUCTION_MODES[("AND", (REG, IMM))], 7, 0x0F,
                    INSTRUCTION_MODES[("OR",  (REG, IMM))], 7, 0x00
                ])
                val = 0x00
            else:
                # Second pass: resolve label -> split into page and offset
                full_addr = parse_operand(op, typ, labels, line_num, resolve_labels=True)
                page = (full_addr >> 8) & 0x0F
                offset = full_addr & 0xFF

                injected.extend([
                    INSTRUCTION_MODES[("AND", (REG, IMM))], 7, 0x0F,
                    INSTRUCTION_MODES[("OR",  (REG, IMM))], 7, page << 4
                ])
                val = offset
        else:
            val = parse_operand(op, typ, labels, line_num, resolve_labels=resolve_labels)

        if not (0 <= val <= 0xFF):
            raise ValueError(f"Line {line_num}: Operand value out of 8-bit range: {val}")
        compiled_bytes.append(val)

    return bytes(injected), bytes(compiled_bytes)

def main():
    if len(sys.argv) != 3:
        print("Usage: python compiler.py input_file.txt output_file.qcom")
        return

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if not output_file.endswith(".qcom"):
        print("Error: Output file must end with .qcom")
        return

    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return

    # ---------- First pass (fixed) ----------
    # ---------- First pass (precise layout simulation) ----------
    # This simulates the final emission order (same rules as second pass)
    # and records both injection-block and compiled-block start offsets so
    # labels can be bound to the earliest byte that belongs to the following instruction.
    base = 0x90

    # collect events and instruction size info (length-only, labels unresolved)
    events = []   # ('label', label_name) or ('comment',None) or ('instr', instr_idx)
    instrs = []   # list of {line_num, instr_name, injected_len, compiled_len}
    for line_num, line in enumerate(lines, 1):
        stripped = strip_comments(line)
        if not stripped:
            continue

        # numbered label (keep your isalpha rule)
        if stripped.startswith("#") and len(stripped) > 1 and not stripped[1].isalpha():
            events.append(("label", stripped))
            continue
        if stripped.startswith("#"):
            events.append(("comment", None))
            continue

        injected, compiled = compile_line(stripped, line_num, labels=None, resolve_labels=False)
        info = {
            "line_num": line_num,
            "instr_name": stripped.split()[0].upper(),
            "injected_len": len(injected),
            "compiled_len": len(compiled),
        }
        instr_idx = len(instrs)
        instrs.append(info)
        events.append(("instr", instr_idx))

    # simulate final emission exactly (recording injection and compiled starts)
    compiled_size = 0
    pending_prev = None            # instr_idx of buffered previous instruction
    instr_positions = {}          # instr_idx -> {'inj_start': x or None, 'compiled_start': y or None}

    for ev in events:
        if ev[0] != "instr":
            continue
        idx = ev[1]
        info = instrs[idx]
        inj = info["injected_len"]
        comp = info["compiled_len"]
        name = info["instr_name"]

        if pending_prev is None:
            # first instruction: injection (if any and not JIF/JNI) emits immediately
            if inj > 0 and name not in ("JIF", "JNI"):
                instr_positions[idx] = {'inj_start': compiled_size, 'compiled_start': None}
                compiled_size += inj
            else:
                instr_positions[idx] = {'inj_start': None, 'compiled_start': None}
            pending_prev = idx
        else:
            prev_idx = pending_prev
            prev_comp = instrs[prev_idx]['compiled_len']

            if inj > 0:
                if name in ("JIF", "JNI"):
                    # injection for this JIF/JNI emits now, then previous compiled emits
                    instr_positions.setdefault(idx, {'inj_start': None, 'compiled_start': None})['inj_start'] = compiled_size
                    compiled_size += inj
                    instr_positions.setdefault(prev_idx, {})['compiled_start'] = compiled_size
                    compiled_size += prev_comp
                    pending_prev = idx
                else:
                    # append previous compiled now, then emit this instruction's injection
                    instr_positions.setdefault(prev_idx, {})['compiled_start'] = compiled_size
                    compiled_size += prev_comp
                    instr_positions[idx] = {'inj_start': compiled_size, 'compiled_start': None}
                    compiled_size += inj
                    pending_prev = idx
            else:
                # no injection: append previous compiled now
                instr_positions.setdefault(prev_idx, {})['compiled_start'] = compiled_size
                compiled_size += prev_comp
                instr_positions[idx] = {'inj_start': None, 'compiled_start': None}
                pending_prev = idx

    # append final pending compiled block
    if pending_prev is not None:
        instr_positions.setdefault(pending_prev, {})['compiled_start'] = compiled_size
        compiled_size += instrs[pending_prev]['compiled_len']

    # compute earliest-emitted byte for each instruction
    first_emit = {}
    for idx, pos in instr_positions.items():
        inj_s = pos.get('inj_start')
        comp_s = pos.get('compiled_start')
        if inj_s is None:
            first_emit[idx] = comp_s
        elif comp_s is None:
            first_emit[idx] = inj_s
        else:
            first_emit[idx] = min(inj_s, comp_s)

    # finally map numbered labels to the earliest byte of the following instruction
    labels = {}
    for i, ev in enumerate(events):
        if ev[0] != "label":
            continue
        label_name = ev[1]
        next_first = None
        for j in range(i + 1, len(events)):
            if events[j][0] == "instr":
                next_idx = events[j][1]
                next_first = first_emit[next_idx]
                break
        if next_first is None:
            # dangling label at end -> point at end of program
            next_first = compiled_size
        labels[label_name] = base + next_first

    # ---------- Second pass: compile with labels resolved ----------
    compiled_binary = bytearray(b"\x00" * 0x90)
    prev_compiled_bytes = None
    prev_instr = None

    for line_num, line in enumerate(lines, 1):
        stripped = strip_comments(line)
        if not stripped:
            continue
        if stripped.startswith("#") and len(stripped) > 1 and not stripped[1].isalpha():
            continue
        if stripped.startswith("#"):
            continue

        try:
            injected, compiled = compile_line(stripped, line_num, labels=labels, resolve_labels=True)
            instr = stripped.split()[0].upper()

            if prev_compiled_bytes is None:
                # First instruction
                if len(injected) > 0 and instr not in ("JIF", "JNI"):
                    compiled_binary.extend(injected)
                prev_compiled_bytes = compiled
                prev_instr = instr
            else:
                if len(injected) > 0:
                    if instr in ("JIF", "JNI"):
                        # For JIF/JNI: inject before previous instruction
                        compiled_binary.extend(injected)
                        compiled_binary.extend(prev_compiled_bytes)
                        prev_compiled_bytes = compiled
                    else:
                        # For all others: inject before *this* instruction
                        compiled_binary.extend(prev_compiled_bytes)
                        compiled_binary.extend(injected)
                        prev_compiled_bytes = compiled
                else:
                    compiled_binary.extend(prev_compiled_bytes)
                    prev_compiled_bytes = compiled
                prev_instr = instr

        except ValueError as e:
            print(f"Second pass error at line {line_num}: {e}")
            print(f"Faulty line: '{stripped}'")
            return

    # emit the last buffered instruction
    if prev_compiled_bytes is not None:
        compiled_binary.extend(prev_compiled_bytes)
    
        # Attempt to write the compiled ROM to disk
    try:
        with open(output_file, "wb") as out_f:
            out_f.write(compiled_binary)
    except OSError as e:
        print(f"Error writing output file '{output_file}': {e}")
        return
    
    print(f"\nCompilation complete. Output written to '{output_file}'")

if __name__ == "__main__":
    main()
