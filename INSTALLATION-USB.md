<!-- INSTALLATION-USB.md -->

# Create an Omarchy 4.0.6 Installation USB

This guide is manual. Repository setup does not flash USB drives, install or
downgrade Omarchy, update the system, or reboot the PC.

## 1. Download the ISO

Download the **4.0.6 ISO** from the [official 4.0.6 release](https://github.com/omacom/omarchy/releases/tag/v4.0.6)
into `~/Downloads` as `omarchy-4.0.6.iso`. Use the versioned release download;
the homepage's latest ISO can install a newer version.

Verify the downloaded file against the SHA256 published in that release:

```bash
cd ~/Downloads
echo 'b542db5fecc37395d9af6654a8146ebed225f275ae4d5a6fcf432e40afe7bb88  omarchy-4.0.6.iso' | sha256sum --check
```

Continue only when verification reports `OK`.

## 2. Flash the USB

Install Caligula if missing:

```bash
omarchy pkg add caligula
```

Connect the USB and unmount any mounted partitions through the file manager. Then run:

```bash
caligula burn ~/Downloads/omarchy-4.0.6.iso
```

Select the correct USB—**its contents will be erased**—and wait for writing and verification to finish.

The USB automatically receives Omarchy's default label: `OMARCHY_YYYYMM`.

## 3. Reboot

Save your work, leave the USB connected, and reboot:

```bash
omarchy system reboot
```

Select the USB from your computer's boot menu.
