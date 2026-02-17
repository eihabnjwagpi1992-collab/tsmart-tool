#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: 2025 Shomy
# SPDX-License-Identifier: AGPL-3.0-or-later
#
import struct
from typing import Final

MAGIC: Final[bytes] = b"PENUMBRAV6P" + bytes([0] * 5)
ARM_MAGIC: Final[bytes] = b"ARM7" + bytes([0] * 4)
ARM64_MAGIC: Final[bytes] = b"ARM64" + bytes([0] * 3)


def pack_v6_payload(arm7_file: str, arm64_file: str, output_file: str) -> None:
    header_format = "<16s4I"  # Magic (16 bytes) + ARM7 offset (4 bytes) + ARM7 length (4 bytes) + ARM64 offset (4 bytes) + ARM64 length (4 bytes)

    # Every payload must start with its own magic of the respective architecture
    with open(arm7_file, "rb") as f:
        arm7_payload = f.read()

    with open(arm64_file, "rb") as f:
        arm64_payload = f.read()

    arm7_payload = ARM_MAGIC + arm7_payload
    arm64_payload = ARM64_MAGIC + arm64_payload

    header_len = struct.calcsize(header_format)
    arm7_offset = header_len
    arm7_length = len(arm7_payload)
    arm64_offset = arm7_offset + arm7_length
    arm64_length = len(arm64_payload)

    with open(output_file, "wb") as f:
        f.write(
            struct.pack(
                header_format,
                MAGIC,
                arm7_offset,
                arm7_length,
                arm64_offset,
                arm64_length,
            )
        )
        f.write(arm7_payload)
        f.write(arm64_payload)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        print(
            "Usage: python3 pack_v6_payload.py <arm7_payload.bin> <arm64_payload.bin> <output_payload.bin>"
        )
        sys.exit(1)

    arm7_payload_file = sys.argv[1]
    arm64_payload_file = sys.argv[2]

    pack_v6_payload(arm7_payload_file, arm64_payload_file, sys.argv[3])
    print(f"Packed v6 payload written to {sys.argv[3]}")
