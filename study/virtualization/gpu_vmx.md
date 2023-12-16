# .vmx file

> ref: https://ianmcdowell.net/blog/esxi-nvidia/

```
hypervisor.cpuid.v0 = "FALSE"

# automatically
pciPassthru0.id = "00000:002:00.0"
pciPassthru0.deviceId = "0x1c82"
pciPassthru0.vendorId = "0x10de"
pciPassthru0.systemId = "5aec7ae7-7d90-8511-435a-d094660b7768"
pciPassthru0.present = "TRUE"
pciPassthru1.id = "00000:002:00.1"
pciPassthru1.deviceId = "0x0fb9"
pciPassthru1.vendorId = "0x10de"
pciPassthru1.systemId = "5aec7ae7-7d90-8511-435a-d094660b7768"
pciPassthru1.present = "TRUE"
pciPassthru0.pciSlotNumber = "160"
pciPassthru1.pciSlotNumber = "192"
```
