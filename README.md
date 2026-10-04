# Elgani Kernel — POCO F4 (munch)

Kernel build project for **POCO F4 / Redmi K40S (munch)**.

## Kernel base

- Source: AstideLabs/android_kernel_xiaomi_sm8250
- Branch: `android17-aptusitu`
- Target: `munch_defconfig`
- Stock-compatible config: `munch_stock-defconfig`

The upstream kernel already contains the POCO F4/munch kernel configuration and device support, so this project does not duplicate the very large kernel tree.

## Device tree reference

- Repository: xiaomi-sm8250-devs/android_device_xiaomi_munch
- Branch: `lineage-23.2`

The device tree is checked out during CI for validation/reference. Kernel compilation uses the DTS/DTSI sources included in the AstideLabs kernel tree.

## GitHub Actions

The workflow builds the kernel automatically on pushes to `main`.

Manual builds are available from **Actions → Build Elgani Kernel - POCO F4 → Run workflow**.

Options:
- AOSP
- MIUI
- Both
- ReSukiSU + SuSFS

The first baseline build intentionally makes no custom charging, thermal, CPU, GPU, or battery modifications. Hardware/thermal changes should be added only after a clean baseline kernel is confirmed.

## Safety

This project is for development/testing. A successful kernel compilation does not guarantee that a particular ROM/firmware combination will boot. Keep a known-good boot image/kernel available for recovery.
