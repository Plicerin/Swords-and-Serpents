#!/usr/bin/env python3
"""Simulate L_6394 viewport clipping with CORRECTED SDBD+CMPI thresholds."""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# CORRECTED thresholds from RAW BYTES (not disassembler's $FF97/$FFCE):
# SDBD CMPI bytes [$00,$97] -> threshold = $0097 = 151
# SDBD CMPI bytes [$00,$CE] -> threshold = $00CE = 206
X_WRAP_THRESHOLD = 0x0097  # 151
Y_WRAP_THRESHOLD = 0x00CE  # 206

BACKTAB_COLS = 20  # 0-19
BACKTAB_ROWS = 12  # 0-11
X_WRAP_MASK = 0x001F  # 32 values (0-31)
Y_WRAP_MASK = 0x000F  # 16 values (0-15)


def signed_16(val):
    return val - 0x10000 if val >= 0x8000 else val

def sim_l6394(x_world, y_world, cam_x, cam_y):
    """Simulate L_6394 with CORRECTED thresholds."""
    path = []
    
    # Step 1: SUB G_0175, R0
    x_screen = (x_world - cam_x) & 0xFFFF
    xs_signed = signed_16(x_screen)
    path.append(f"X_screen = {x_world} - {cam_x} = {xs_signed}")
    
    # Step 2: SDBD ; CMPI #$0097, R0 ; BGE skip_wrap_x
    # BGE branches if signed(R0) >= 151
    if xs_signed >= X_WRAP_THRESHOLD:
        path.append(f"  {xs_signed} >= {X_WRAP_THRESHOLD}: skip wrapping")
    else:
        old_x = x_screen
        x_screen = x_screen & X_WRAP_MASK
        path.append(f"  {xs_signed} < {X_WRAP_THRESHOLD}: ANDI #$001F -> {x_screen}")
        xs_signed = signed_16(x_screen)
    
    # Step 3: TSTR R0 ; BLT skip_object
    if xs_signed < 0:
        path.append(f"  X={xs_signed} < 0 -> SKIP OBJECT")
        return -1, -1, path
    
    # Step 4: CMPI #$0013, R0 ; BGT skip_object
    if x_screen > 0x13:
        path.append(f"  X={x_screen} > 19 -> SKIP OBJECT")
        return -1, -1, path
    
    # Step 5: SUB G_0176, R1
    y_screen = (y_world - cam_y) & 0xFFFF
    ys_signed = signed_16(y_screen)
    path.append(f"Y_screen = {y_world} - {cam_y} = {ys_signed}")
    
    # Step 6: SDBD ; CMPI #$00CE, R1 ; BGE skip_wrap_y
    if ys_signed >= Y_WRAP_THRESHOLD:
        path.append(f"  {ys_signed} >= {Y_WRAP_THRESHOLD}: skip wrapping")
    else:
        old_y = y_screen
        y_screen = y_screen & Y_WRAP_MASK
        path.append(f"  {ys_signed} < {Y_WRAP_THRESHOLD}: ANDI #$000F -> {y_screen}")
        ys_signed = signed_16(y_screen)
    
    # Step 7: TSTR R1 ; BLT skip_object
    if ys_signed < 0:
        path.append(f"  Y={ys_signed} < 0 -> SKIP OBJECT")
        return -1, -1, path
    
    # Step 8: CMPI #$000B, R1 ; BLE proceed
    if y_screen > 0x0B:
        path.append(f"  Y={y_screen} > 11 -> SKIP OBJECT")
        return -1, -1, path
    
    path.append(f"  VALID: X={x_screen} Y={y_screen} -> BACKTAB[{y_screen}][{x_screen}]")
    return x_screen, y_screen, path


# ===================================================================
# PART 1: Room objects with various camera positions
# ===================================================================
print("=" * 70)
print("PART 1: Room data objects at various camera positions (CORRECTED)")
print("=" * 70)

room_objects_s0 = [0x14, 0x6C, 0x4C, 0x3A, 0x5C, 0x0C, 0x26, 0x33, 0x4F, 0x2F, 0x71, 0x06, 0x2B]

cameras = [
    ("Initial (L_55D1)", 2, 26),
    ("Screen 0 ($5A17)", 98, 12),
    ("Screen 1 ($5A1B)", 27, 98),
]

for cam_name, cam_x, cam_y in cameras:
    print(f"\n--- {cam_name}: CamX={cam_x}, CamY={cam_y} ---")
    visible = 0
    wrapped = 0
    skipped = 0
    
    for x_world in room_objects_s0:
        xs, ys, path = sim_l6394(x_world, 0, cam_x, cam_y)
        was_wrapped = any("ANDI" in p for p in path)
        
        if xs >= 0:
            status = "WRAPPED" if was_wrapped else "VISIBLE"
            print(f"  X={x_world:3d} ($%02X): -> col={xs:2d} row={ys:2d} [{status}]" % x_world)
            visible += 1
        else:
            if was_wrapped:
                print(f"  X={x_world:3d} ($%02X): WRAPPED but out of bounds" % x_world)
                wrapped += 1
            else:
                skipped += 1
    
    print(f"  Summary: {visible} visible, {wrapped} wrapped-invalid, {skipped} skipped")


# ===================================================================
# PART 2: Wrapping sweep across X_screen space
# ===================================================================
print("\n" + "=" * 70)
print(f"PART 2: X wrapping sweep (threshold={X_WRAP_THRESHOLD})")
print("=" * 70)

print(f"\nWrapping applied for X_screen < {X_WRAP_THRESHOLD} (signed)")
print("Effect of ANDI #$001F across X_screen values:\n")

print(f"  {'X_screen':>10} {'Wrapped':>10} {'Post CMPI #$0013':>20}")
print(f"  {'-'*10} {'-'*10} {'-'*20}")

for xs in range(-160, 200, 1):
    xs_signed = xs if xs < 128 else xs - 256
    if xs_signed >= X_WRAP_THRESHOLD:
        if 0 <= xs_signed <= 19:
            print(f"  {xs_signed:10d} {'skip':>10} {'VALID (no wrap)':>20}")
    else:
        masked = xs & X_WRAP_MASK
        if masked != xs or xs_signed < 0:
            status = f"VALID col={masked}" if 0 <= masked <= 19 else f"SKIP col={masked}"
            if xs_signed in range(-32, 0) or xs_signed in range(20, 64):
                print(f"  {xs_signed:10d} {'WRAP':>10} {status:>20}")

print()

# ===================================================================
# PART 3: Wrapping effectiveness statistics
# ===================================================================
print("=" * 70)
print("PART 3: Wrapping effectiveness statistics")
print("=" * 70)

# Positive values 0-150 (where wrapping applies)
wv = sum(1 for xs in range(0, 151) if 0 <= (xs & X_WRAP_MASK) <= 19)
wi = sum(1 for xs in range(0, 151) if (xs & X_WRAP_MASK) > 19)
print(f"\nX wrapping for X_screen 0-150:")
print(f"  On-screen (0-19):     20 values unchanged (no-op)")
print(f"  Off-right (20-150):   {wv-20} map to visible cols, {wi} to cols 20-31")
print(f"  Total visible:        {wv}/151 = {100*wv/151:.1f}%")

# Negative values
nv = sum(1 for xs in range(-128, 0) if 0 <= ((xs & 0xFFFF) & X_WRAP_MASK) <= 19)
print(f"\nX wrapping for X_screen -128 to -1:")
print(f"  Visible: {nv}/128 = {100*nv/128:.1f}%")
print(f"  (Negative values wrap by: (-X & $1F) = (32 - (|X| % 32)) % 32)")

# Y wrapping
ywv = sum(1 for ys in range(0, 206) if 0 <= (ys & Y_WRAP_MASK) <= 11)
ywi = sum(1 for ys in range(0, 206) if (ys & Y_WRAP_MASK) > 11)
print(f"\nY wrapping for Y_screen 0-205:")
print(f"  On-screen (0-11):     12 values unchanged (no-op)")
print(f"  Off-bottom (12-205):  {ywv-12} map to visible rows, {ywi} to rows 12-15")
print(f"  Total visible:        {ywv}/205 = {100*ywv/205:.1f}%")

nyv = sum(1 for ys in range(-128, 0) if 0 <= ((ys & 0xFFFF) & Y_WRAP_MASK) <= 11)
print(f"\nY wrapping for Y_screen -128 to -1:")
print(f"  Visible: {nyv}/128 = {100*nyv/128:.1f}%")

# ===================================================================
# PART 4: Conclusion
# ===================================================================
print("\n" + "=" * 70)
print("PART 4: CONCLUSION")
print("=" * 70)

print(f"""
The disassembler incorrectly decoded SDBD+CMPI as comparing against
$FF97 (-105) and $FFCE (-50). The RAW BYTES are [$00,$97] and [$00,$CE],
giving thresholds of {X_WRAP_THRESHOLD} and {Y_WRAP_THRESHOLD}.

With the CORRECTED thresholds:
  - X wrapping (threshold 151): Applied to ALL X_screen < 151
  - Y wrapping (threshold 206): Applied to ALL Y_screen < 206

Since BACKTAB is only 20x12, virtually EVERY object gets wrapped.

This IS intentional — it's a MODULO ADDRESSING scheme:
  ANDI #$001F → X mod 32 → wrap at 32-column intervals
  ANDI #$000F → Y mod 16 → wrap at 16-row intervals

For on-screen objects: ANDI is a no-op (0-19 & $1F = 0-19).
For off-screen objects: ANDI wraps them back into the visible area.
For negative values: Two's complement ANDI maps them to positive 0-31 range.

The CMPI #$0013 (X) and CMPI #$000B (Y) checks AFTER wrapping filter
out columns 20-31 and rows 12-15.

Result: The room behaves as a TOROIDAL space with 32-column wrapping
periodicity, creating natural room-looping as the camera scrolls.
""")
