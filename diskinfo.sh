#!/usr/bin/env bash

echo -e "\n"

# TODO: Output host shortname, serial, disk serial number, total # visible disks (online/offline)
system_hostname=$(cat /etc/hostname)
system_vendor=$(cat /sys/devices/virtual/dmi/id/board_vendor)
system_board_model=system_serial=$(cat /sys/devices/virtual/dmi/id/board_name)
system_serial=$(cat /sys/devices/virtual/dmi/id/board_serial)

# Output SCSI subsystem view of host/chan/id/lun
echo "SCSI Device Status"
cat /proc/scsi/sg/devices
echo -e "\n"

# Output SAS PHY topology
echo "PHY Link Status"
for sas_phy in /sys/class/sas_phy/phy-*; do
    linkrate=$(cat ${sas_phy}/negotiated_linkrate)
    phyname=$(basename ${sas_phy})
    attached_dev_path=${sas_phy}/device/port/end_device-*/target*/*/block/*
    attached_dev=$(basename ${attached_dev_path})
    dev_addr_path=$(find /dev/disk/by-path -lname */${attached_dev})
    dev_addr=$(basename "${dev_addr_path}")
    if [[ ${attached_dev} == "*" ]]; then
        # No disk device detected on this SAS port.
        attached_dev="N/A"
        dev_addr="N/A"
    fi
    echo "${phyname} - ${attached_dev} - ${dev_addr} - ${linkrate}"
done
echo -e "\n"

# Iterate through devices, find offline units, and output dev/bus info
echo "Block Device Status"
for dev in /dev/sd?; do
    devname=${dev#/dev/}
    bypath_path=$(find /dev/disk/by-path -lname */${devname})
    bypath_name=${bypath_path#/dev/disk/by-path/}
    sysdev=/sys/block/${devname}
    sas_end_dev=$(readlink -fn ${sysdev}/device/../../..)
    sas_end_dev_phy=$(readlink -fn ${sas_end_dev}/phy-*)
    if [[ ! -e ${sas_end_dev_phy} ]]; then
        # Device is not actually connected to SAS HBA. Ignore it.
        continue
    fi
    phy_name=$(basename ${sas_end_dev_phy})
    phy_path=/sys/class/sas_phy/${phy_name}
    linkrate=$(cat ${phy_path}/negotiated_linkrate)

    if ! grep "running" ${sysdev}/device/state > /dev/null; then
        echo -n "OFFLINE "
    fi
    echo "${devname} - ${bypath_name} - ${sas_end_dev} - ${phy_name} - ${linkrate}"
done
echo -e "\n"
