<!-- NVIDIA-DRIVER-REPAIR.md -->

# NVIDIA Driver Repair on Omarchy 4.0.6

On **2026-11-11**, the RTX 5060 Ti in the desktop described in
[README.md](README.md#target-system) received a targeted NVIDIA driver change
from **615.78.08-1** to **620.70.06-1**. Omarchy stayed at **4.0.6-1**. The new
driver passed the initial checks after a reset, but crashes later recurred.
See [Recurring Crashes and LTS Kernel Trial](#recurring-crashes-and-lts-kernel-trial)
for the subsequent investigation and current test.

This was separately requested maintenance. `setup.py` retains its existing
protection against GPU package changes; running setup does not repeat this repair.

## Symptoms and Diagnosis

The desktop froze or went black during active use and required a manual reset.
Initial checks found matching NVIDIA kernel and user-space versions, installed
DKMS modules, and intact driver package files. The earlier boot ended abruptly
without an application core dump.

During live checks, NVIDIA's GPU System Processor (GSP) firmware stopped
responding to driver requests. The kernel recorded:

```text
Xid 119: Timeout after 6s of waiting for RPC response from GPU0 GSP
GSP heartbeat timeout
GPU marked for reset
Xid 154: GPU recovery action changed from None to PF FLR
```

`nvidia-smi` reported `[GPU requires reset]` instead of temperature, power,
and PCIe telemetry. This established a GPU firmware timeout and reset-required
state; it did not by itself distinguish a driver bug from a hardware fault.

## Package Versions

Only these three packages changed in the repair transaction:

| Package | Before | After | Download source |
| --- | --- | --- | --- |
| `nvidia-open-dkms` | `615.78.08-1` | `620.70.06-1` | Arch `extra-testing` |
| `nvidia-utils` | `615.78.08-1` | `620.70.06-1` | Arch `extra-testing` |
| `lib32-nvidia-utils` | `615.78.08-1` | `620.70.06-1` | Arch `multilib-testing` |

These installed versions stayed unchanged:

| Component | Version |
| --- | --- |
| `omarchy` and `omarchy-settings` | `4.0.6-1` |
| `linux-omarchy` and `linux-omarchy-headers` | `7.2.8-9` |
| Running kernel | `7.2.8-9-omarchy` |
| Hyprland | `0.56.2-4` |

The replacement packages came from Arch's testing repositories at the time of
repair. Matching package archives and detached signatures were downloaded
directly, without enabling testing repositories in Pacman's configuration.
The complete installed-package lists before and after the transaction matched
except for the three NVIDIA packages.

## Repair Procedure Used

1. Saved the kernel logs and installed-package versions, and copied all three
   original `615.78.08-1` package archives from the Pacman cache for rollback.
2. Verified the three replacement packages against Arch's signing keyring.
   Their signatures were valid signatures from Peter Jung.
3. Built the new open kernel modules in a staging directory against the
   existing `7.2.8-9-omarchy` headers. This build succeeded before installation.
4. Previewed the Pacman transaction and required it to contain exactly the
   three packages listed above, all at `620.70.06-1`.
5. Created **Snapper root snapshot 1** and backed up `/boot`, the driver
   configuration, and the initramfs and Limine configuration.
6. Installed the three downloaded archives with `pacman --upgrade`. The normal
   hooks built and installed the DKMS modules and rebuilt the unified kernel
   image at `/boot/EFI/Linux/omarchy_linux-omarchy.efi`.
7. Verified DKMS installation and the `620.70.06` versions of `nvidia`,
   `nvidia_modeset`, `nvidia_uvm`, and `nvidia_drm`, then extracted the boot
   image's initramfs and checked its NVIDIA module version and bundled
   `620.70.06` firmware.
8. Restarted to activate the new driver. The requested reboot needed a manual
   reset; the old `615.78.08` kernel module was still loaded and reporting
   reset-required errors during that shutdown. The checks below were performed
   in the subsequent boot with `620.70.06` loaded.

The RTX 5060 Ti is a Blackwell GPU and requires the open kernel-module flavor,
as documented in [NVIDIA's 620.70.06 driver manual](https://download.nvidia.com/XFree86/Linux-x86_64/620.70.06/README/kernel_open.html).
Keep the kernel module and both user-space packages at matching driver versions
when reviewing a future repair.

## Validation After Reset

The live checks on 2026-11-11 confirmed:

- `/proc/driver/nvidia/version` reported the open `620.70.06` kernel module.
- DKMS reported `nvidia/620.70.06` installed for `7.2.8-9-omarchy`.
- `nvidia-smi` returned normal telemetry, including about **37°C** and **7 W**
  at idle. The extended power and PCIe query that had encountered the earlier
  fault also succeeded.
- The current boot had no NVIDIA Xid errors or GSP timeouts, and no application
  core dumps were found.
- Hyprland reported no configuration errors and supported explicit sync on
  the Samsung display.

These checks cover startup and light desktop operation. Continued normal use
is needed to establish whether the intermittent freezes have stopped; a short
clean boot does not establish long-term stability.

Repeat the basic checks without changing configuration:

```bash
omarchy version
pacman -Q omarchy omarchy-settings linux-omarchy linux-omarchy-headers hyprland \
  nvidia-open-dkms nvidia-utils lib32-nvidia-utils
cat /proc/driver/nvidia/version
dkms status
timeout 15s nvidia-smi \
  --query-gpu=name,driver_version,temperature.gpu,pstate --format=csv
journalctl -b 0 -k --no-pager --grep='NVRM:.*(Xid|GSP|Reset required)'
hyprctl configerrors
```

The filtered journal should have no fault entries, and `hyprctl configerrors`
should be empty. If the problem returns, save the affected boot's kernel log
before another reset when possible; after a reset, inspect `journalctl -b -1 -k`.

## Recurring Crashes and LTS Kernel Trial

Later on 2026-11-11, black screens recurred on `620.70.06`, with square artifacts
appearing shortly before the failure after the desktop loaded. One boot logged
an Xwayland **Xid 13, Graphics FECS Exception: UCODE Fatal Error**, followed by
Xid 154, repeated Xid 109 context-switch timeouts, and Xid 8. A subsequent boot
logged Xid 119 GSP timeouts. The driver change alone did not resolve the problem.

Read-only hardware checks found SSD SMART health passing, zero media/data
integrity errors, and zero Btrfs device error counters. The SSD's recorded
NVMe error-log entries were invalid-field responses on the admin queue rather
than media errors. The two 8 GiB DDR4 modules were configured at 2666 MT/s and
1.2 V. A memory test was not performed; these results do not rule out a GPU,
VRAM, power, or system-memory fault.

A controlled kernel comparison added `linux-lts` and `linux-lts-headers`, both
**6.18.57-2**, alongside the existing kernel. NVIDIA stayed at **620.70.06-1**,
Omarchy and its settings stayed at **4.0.6-1**, and existing package versions
were unchanged. The NVIDIA modules built against the LTS headers before
installation; DKMS and the installed LTS boot image were then validated.
**Snapper snapshot 2** and a separate boot backup were created.

The first LTS boot reported `6.18.57-2-lts`, matching NVIDIA modules, normal
GPU telemetry near 35°C, and no initial NVIDIA or Hyprland configuration
errors. The user resumed the Dota download and slide-compilation workload.
**Stability testing is ongoing; the LTS kernel is not yet a confirmed fix.**

The trial orders `linux-lts` first in Limine through
`/etc/limine-entry-tool.d/zz-pc-crash-kernel-trial.conf`. The original
`linux-omarchy` entry remains selectable. Trial packages, logs, the installer,
and the boot backup are local to this PC under:

```text
~/Projects/pc-crash-investigation-20261111-153637/kernel-trial/
```

The parent investigation folder holds the hardware-check results and a passive
kernel-error log for the LTS boot. The error logger runs for 30 minutes during
this test and flushes matching errors to disk without polling or stressing the GPU.

To restore the original kernel preference while keeping both kernels installed:

```bash
trial="$HOME/Projects/pc-crash-investigation-20261111-153637/kernel-trial"
sudo bash "$trial/restore-original-kernel.sh"
```

That helper disables the trial's ordering override and refreshes the original
kernel entry. It has not been exercised during this trial. The original kernel
also exhibited freezes. The driver rollback helper and boot backup below
predate the LTS addition; review both kernel images and the current boot order
before using that older recovery procedure.

## Recovery Files and Rollback

The repair artifacts are local to this PC under:

```text
~/Projects/gpu-driver-repair-20261111-150413/
```

| Path inside the repair folder | Purpose |
| --- | --- |
| `install.log`, `kernel-current.txt`, `kernel-previous.txt` | Installation log and kernel evidence saved before repair |
| `packages/` | Replacement packages, detached signatures, and source metadata |
| `rollback/` | The three original `615.78.08-1` package archives |
| `system-backup/boot-before.tar` | Original boot files, including the boot image |
| `system-backup/driver-config-before.tar` | Driver, initramfs, and Limine configuration backup |
| `system-backup/snapshot-number.txt` | Recovery snapshot number, `1` for this repair |
| `install.sh`, `rollback.sh`, `verify-after-reboot.py` | The prepared installer, recovery helper, and read-only validation helper |

The package archives, logs, helpers, boot backups, and Snapper snapshot are not
stored in this Git repository. Preserve them separately before reinstalling
the PC. A clone on another machine provides this record, not those local artifacts.

To repeat the validation on this installation:

```bash
repair="$HOME/Projects/gpu-driver-repair-20261111-150413"
python3 "$repair/verify-after-reboot.py"
```

If this specific driver change needs to be reversed, the prepared recovery
helper restores all three original packages together, checks the original DKMS
modules, and restores the saved boot files:

```bash
repair="$HOME/Projects/gpu-driver-repair-20261111-150413"
sudo bash "$repair/rollback.sh"
```

That helper is specific to this PC's saved repair folder and kernel. It was
prepared for recovery but was not exercised during the successful installation.
It restores the former driver version that exhibited the fault, so rollback
is a recovery option rather than a claim that `615.78.08` is stable. Review its
output before restarting; if recovery reports failure, repair the modules and
boot image before rebooting.
