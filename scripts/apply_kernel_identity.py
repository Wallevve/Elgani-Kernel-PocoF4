#!/usr/bin/env python3
from pathlib import Path

KERNEL_RELEASE = "5.10.257"
KSU_VERSION = "32603"

root = Path("kernel")

# Spoof only the runtime UTS release/banner. Do NOT change
# VERSION/PATCHLEVEL/SUBLEVEL in the kernel Makefile: the actual
# kernel tree remains 4.19 internally.
version_c = root / "init/version.c"
s = version_c.read_text()

old_release = "        .release = UTS_RELEASE,"
new_release = f'        .release = "{KERNEL_RELEASE}",'
if s.count(old_release) != 1:
    raise SystemExit(f"UTS release target mismatch: found {s.count(old_release)}")
s = s.replace(old_release, new_release, 1)

old_banner = '"Linux version " UTS_RELEASE " ("'
new_banner = f'"Linux version {KERNEL_RELEASE} ("'
if s.count(old_banner) != 1:
    raise SystemExit(f"Linux banner target mismatch: found {s.count(old_banner)}")
s = s.replace(old_banner, new_banner, 1)

version_c.write_text(s)

# KernelSU setup.sh places the driver source at KernelSU/kernel.
ksu_kbuild = root / "KernelSU/kernel/Kbuild"
if not ksu_kbuild.exists():
    raise SystemExit(f"KernelSU Kbuild not found: {ksu_kbuild}")

k = ksu_kbuild.read_text()
marker = "ccflags-y += -DKSU_VERSION="
lines = k.splitlines()
replaced = False
out = []
for line in lines:
    if line.strip().startswith(marker):
        indent = line[:len(line) - len(line.lstrip())]
        out.append(f"{indent}ccflags-y += -DKSU_VERSION={KSU_VERSION}")
        replaced = True
    else:
        out.append(line)

if not replaced:
    raise SystemExit("KernelSU Kbuild version definition was not found")

ksu_kbuild.write_text("\n".join(out) + "\n")

print(f"[+] Kernel release spoof: {KERNEL_RELEASE}")
print(f"[+] KernelSU driver version: {KSU_VERSION}")
