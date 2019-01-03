# diskinfo

NOTE: Shell script is deprecated. Don't use it.

This Python script outputs topology and status information for SAS-attached
disks, as well as physical host identifiers (serial numbers, model, hostname).
This can help physically locate disks in a host, and can allow the user to infer
the presence of missing, misbehaving, or otherwise dead disks.

Disk devices that appear to still be physically present, will have serial number
SAS link speed, and disk status exported as part of the device tree. A disk with
status that is not "running" should be considered offline, or otherwise not
available.

The output of this script is a JSON structure that "walks" all SAS HBAs, their
PHY links, ports attached to those links, devices attached to ports, LUNs
attached to ports, and finally devices present at a LUN.

## Sys Tree
/sys/class/scsi_host/host0/device/phy-0:0/sas_phy/phy-0:0/device/port/end_device-0:0/target0:0:0/0:0:0:0/block/sda/

is_sas => /sys/class/scsi_host/host0/device/sas_host

/sys/class/scsi_host/host2/device/target2\:0\:0/2\:0\:0\:0/block/sdq/

## Example structure

```json
{
    "blockdevcount": 16,
    "devicecount": 16,
    "luncount": 16,
    "hosts": {
        "host1": {
            "phy-1:6": {
                "enable": "1",
                "port-1:4": {
                    "end_device-1:4": {
                        "scsi_target_id": "4",
                        "target1:0:4": {
                            "1:0:4:0": {
                                "state": "running",
                                "vendor": "ATA",
                                "sdj": {
                                    "stat": "48856646        0 406574178  2125460   938541     6305 1008954040  5380628        0  3184232  7499056"
                                },
                                "model": "SSDCO 99999",
                                "wwid": "naa.11ab1c111de11f11",
                                "sas_address": "0x4433221106000000",
                                "serial": "SOMESERIALVALUE",
                                "scsi_level": "7"
                            }
                        },
                        "sas_address": "0x4433221106000000",
                        "bay_identifier": "5",
                        "enclosure_identifier": "0x500605b008ec6d40",
                        "phy_identifier": "6"
                    }
                },
                "negotiated_linkrate": "6.0 Gbit",
                "sas_address": "0x500605b008ec6d44",
                "phy_identifier": "6",
                "device_type": "end device"
            },
            "sas_address": "0x500605b008ec6d44",
            "state": "running",
            "boardname": "SAS9207-8i",
            "unique_id": "1"
        },
        "host9": {
            "phy-9:2": {
                "phy_identifier": "2",
                "negotiated_linkrate": "Unknown",
                "enable": "1",
                "sas_address": "0x5fcfffff00000001",
                "device_type": "none"
            }
        }
    },
    "portcount": 16,
    "hostcount": 10,
    "targetcount": 16,
    "system": {
        "board_name": "F101",
        "chassis_vendor": "Serverco",
        "board_vendor": "Board Co.",
        "hostname": "somehost",
        "product_name": "SuperFast Server"
    },
    "phycount": 28
}
```

## How to use this tool

Run this script with root privileges so it is able to retrieve all available SAS
bus information.

`sudo diskinfo.py`
