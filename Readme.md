# verify-squash-root
## Build signed efi binaries which mount a dm-verity verified squashfs image as rootfs on boot.

### [Install](#install) - [Configuration](#configuration) - [Usage](#usage) - [Development](#development)

This repository provides an easy way to create signed efi binaries which mount a
verified squashfs (dm-verity) image as rootfs on boot (in the initramfs/initrd).
Also it creates A/B-style image and efi files. The current booted image will not
be overriden, so you can boot an old known-working image if there are problems.
The A/B images are stored on the configured root-partition, so they will still
be encrypted, if encryption of the root image is configured.

#### What happens on boot?

 - The initramfs mounts the root-partition as before.
   This is why encryption of the root-partition still works.
   Cmdline parameters to decrypt still need to be configured in the config file
   as `CMDLINE`.
 - Depending on the kernel cmdline, either the A or B image will be verified
   via dm-verity and used. (The build command will set these automatically.)
   If you boot a tmpfs image, a tmpfs will be used as overlay image for
   volatile changes.
   If you boot a non-tmpfs image, the folder overlay on the root-partition
   will be used as overlayfs upper directory to save persistent changes.

## Install

Make yourself familiar with the process of creating, installing and using
custom Secure Boot keys. See:
 - https://wiki.archlinux.org/index.php/Secure_Boot
 - https://www.rodsbooks.com/efi-bootloaders/controlling-sb.html

After you have generated your custom keys:
 - Install [verify-squash-root](https://aur.archlinux.org/packages/verify-squash-root/) from AUR
 - Install `age` and encrypt your secure boot keys
```bash
cd to/your/keys/direcory
tar cf keys.tar db.key db.crt
age -p -e -o keys.tar.age keys.tar
mv keys.tar.age /etc/verify_squash_root/
rm keys.tar
```
 - Remove your plaintext keys
 - Create directories `/boot/efi` and `/mnt/root`
 - Make sure your EFI parition is big enough (500 MB recommended)
 - Mount your EFI partition to `/boot/efi` and configure it in fstab file
 - Mount your root-partition to `/mnt/root` and configure it in fstab file
 - Configure your current kernel cmdline in the config file (`CMDLINE`)
 - Exclude every directory not wanted in the squashfs in the config file (`EXCLUDE_DIRS`)
 - Configure a bind-mount for every excluded directory from `/mnt/root/...`
 - Configure distribution specific options (see [Configuration](#configuration))
 - Install systemd-boot, configure it and build the first image:
```
verify-squash-root --ignore-warnings setup systemd
verify-squash-root --ignore-warnings build
```
 - Now reboot into the squashfs

### Updates

 - Boot into a tmpfs image.
 - Update your distribution
 - Create new squashfs image with signed efis:
```
verify-squash-root build
```

## Configuration

The config file is located at `/etc/verify_squash_root/config.ini`.
These config options are available:

- `CMDLINE`: configures additional kernel cmdline.
- `EFI_STUB`: path to efi stub, default is the one provided by systemd.
- `DECRYPT_SECURE_BOOT_KEYS_CMD`: Command to decrypt your secure-boot keys
tarfile, {} will be replaced with the output tar file. `db.key` and `db.crt`
in the tarfile are used to sign the efi binaries.
- `EXCLUDE_DIRS`: These directories are not included in the squashfs image.
`EFI_PARTITION` and `ROOT_MOUNT` are excluded automatically.
- `EFI_PARTITION`: Path to your efi partition. Efi binaries and systemd-boot
configuration files are stored there.
- `ROOT_MOUNT`: Path to your "original" root partition.
- `IGNORE_KERNEL_EFIS`: Which efi binaries are not built. You can use the
`list` parameter to show which can exist and which are excluded already.

### Arch Linux

Only mkinitcpio wih systemd-hooks is supported under Arch Linux.
Add the hook `verify-squash-root` to `/etc/mkinitcpio.conf`.

## Considerations / Recommendations

 - Directly before updating, reboot into a tmpfs overlay, so modifications by
an attacker are removed and you have your trusted environment from the last
update.
 - If you enable automatic decryption of your secure-boot keys, an
attacker who got access can also sign efi binaries.
 - To be sure to only enter the password for your secure-boot keys
on your machine, you can verify your machine with OTP keys on boot.
 - Encrypt your root partition! If your encryption was handled by the
initramfs before installation, it will work with the squashfs root
image as well.

## Usage

To list all efi images, which will be created or ignored via
`IGNORE_KERNEL_EFIS`:
```
verify-squash-root list
```

To install systemd-boot and create a UEFI Boot Manger entry for it:
```
verify-squash-root setup systemd
```

To add efi files to the UEFI Boot Manager with /dev/sda1 as EFI partition:
```
verify-squash-root setup uefi /dev/sda 1
```

To build a new squashfs image and efi files:
```
verify-squash-root build
```

If you are not yet booted in a verified image, you need `--ignore-warnings`,
since there will be a warning if the root image is not fully verified.

## Files

The following files will be used on your root-partition:

Images with verity info:

- `image_a.squashfs`, `image_a.squashfs.verity`,
- `image_b.squashfs` `image_b.squashfs.verity`

Overlayfs directories:

- `overlay` `workdir`

## Development

### Dependencies

```
age (only when used for decryption of secure-boot keys)
binutils
python
sbsigntools
squashfs-tools
tar
```

#### Development

```
python-pyflakes
python-pycodestyle
```

### Setup

Setup a python3 virtual environment:

```shell
git clone git@github.com:brandsimon/verify-squash-root.git
python3 -m venv .venv
.venv/bin/pip install -e . --no-deps
```

Run unit tests:

```shell
.venv/bin/python -m unittest tests/unit/tests.py
```
