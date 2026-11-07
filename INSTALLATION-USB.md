<!-- INSTALLATION-USB.md -->

# Create an Omarchy Installation USB

## 1. Download the ISO

Download the latest **x86 ISO** from [omarchy.org](https://omarchy.org/) into `~/Downloads`.

## 2. Flash the USB

Install Caligula if missing:

```bash
omarchy pkg add caligula
```

Connect the USB and unmount any mounted partitions through the file manager. Then run, replacing the filename with the version you downloaded:

```bash
caligula burn ~/Downloads/omarchy-4.5.0-x86.iso
```

Select the correct USB—**its contents will be erased**—and wait for writing and verification to finish.

The USB automatically receives Omarchy's default label: `OMARCHY_YYYYMM`.

## 3. Reboot

Save your work, leave the USB connected, and reboot:

```bash
omarchy system reboot
```

Select the USB from your computer's boot menu.
