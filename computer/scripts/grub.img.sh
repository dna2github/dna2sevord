grub-mkrescue —modules=“multiboot sh fat scsi ext2 elf pxe echo ntfs chain cat blacklist memdisk ls linux boot reboot biosdisk acpi loopback tar usb iso9660 search search_fs_uuid”\
              —output=grub2.img <source_file_to_put>

# source_file_to_put: other resources, e.g. ks.cfg, hello.exe, ...

# example grub.cfg
cat <<EOF
#!/bin/sh
# grub.cfg

default=0
timeout=10

menuentry "install centos" {
   insmod ata
   set root=(ata0)
   linux /isolinux/vmlinuz ks=hd:fd0:/ks.cfg
   initrd /isolinux/initrd.img
   boot
}
EOF
