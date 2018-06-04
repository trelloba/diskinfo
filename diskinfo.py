#!/usr/bin/env python2

"""
This script walks the /sys/bus/scsi directory tree to search for ports and devices connected to those ports.
If a device is found to be connected to a port its serial number, device name, and aliases will be collected.
"""
import glob
import json
import logging
import os
import platform
import sys


def get_canonical_path(path):
    return os.path.realpath(os.path.abspath(path))
    

def get_device_data(devicepath, item):
    itempath = os.path.join(devicepath, item)
    logging.debug('Reading %s', itempath)
    try:
        itemfile = open(name=itempath, mode='r')
        iremdata = itemfile.read()
        itemfile.close()
        return iremdata.strip()
    except Exception as e:
        logging.warn('Unable to read %s from %s. %s', item, devicepath, e)
        return None


#
# System Data
#
def get_system_identifiers():
    data = {}

    boardname = get_device_data('/sys/devices/virtual/dmi/id', 'board_name')
    if boardname:
        data.update({'board_name': boardname})

    boardserial = get_device_data('/sys/devices/virtual/dmi/id', 'board_serial')
    if boardserial:
        data.update({'board_serial': boardserial})

    boardvendor = get_device_data('/sys/devices/virtual/dmi/id', 'board_vendor')
    if boardvendor:
        data.update({'board_vendor': boardvendor})

    chassisserial = get_device_data('/sys/devices/virtual/dmi/id', 'chassis_serial')
    if chassisserial:
        data.update({'chassis_serial': chassisserial})

    chassisserial = get_device_data('/sys/devices/virtual/dmi/id', 'chassis_serial')
    if chassisserial:
        data.update({'chassis_serial': chassisserial})

    chassisvendor = get_device_data('/sys/devices/virtual/dmi/id', 'chassis_vendor')
    if chassisvendor:
        data.update({'chassis_vendor': chassisvendor})

    hostname = platform.node().split('.')[0]
    if hostname:
        data.update({'hostname': hostname})

    productname = get_device_data('/sys/devices/virtual/dmi/id', 'product_name')
    if productname:
        data.update({'product_name': productname})

    productserial = get_device_data('/sys/devices/virtual/dmi/id', 'product_serial')
    if productserial:
        data.update({'product_serial': productserial})

    return data

def get_scsi_devices():
    return glob.glob('/sys/bus/scsi/devices/*')


def get_scsi_bus_luns():
    # Items beginning with a 'X:X...' are a target's LUN(s)
    return glob.glob('/sys/bus/scsi/devices/[0-9]*')


def get_scsi_bus_targets():
    # Items beginning with 'targetX:X...' are a host's target
    return glob.glob('/sys/bus/scsi/devices/target[0-9]*')


#
# Host Data
#
def get_scsi_bus_hosts():
    # Items beginning with 'hostX' are a SCSI host
    return glob.glob('/sys/bus/scsi/devices/host[0-9]*')


def get_host_data(hostpath):
    data = {}

    boardname = get_host_boardname(hostpath)
    if boardname:
        data.update({'boardname': boardname})

    sasaddress = get_host_sasaddress(hostpath)
    if sasaddress:
        data.update({'sas_address': sasaddress})

    state = get_host_state(hostpath)
    if state:
        data.update({'state': state})

    uniqueid = get_host_uniqueid(hostpath)
    if uniqueid:
        data.update({'unique_id': uniqueid})

    return data


def get_host_boardname(hostpath):
    boardname = get_device_data(glob.glob(os.path.join(hostpath, 'scsi_host/host[0-9]*'))[0], 'board_name')
    return boardname


def get_host_sasaddress(hostpath):
    address = get_device_data(glob.glob(os.path.join(hostpath, 'scsi_host/host[0-9]*'))[0], 'host_sas_address')
    return address


def get_host_state(hostpath):
    state = get_device_data(glob.glob(os.path.join(hostpath, 'scsi_host/host[0-9]*'))[0], 'state')
    return state


def get_host_uniqueid(hostpath):
    uniqueid = get_device_data(glob.glob(os.path.join(hostpath, 'scsi_host/host[0-9]*'))[0], 'unique_id')
    return uniqueid


#
# PHY Data
#
def get_host_phys(hostpath):
    return glob.glob(os.path.join(hostpath, 'phy-[0-9]*'))


def get_phy_data(phypath):
    data = {}

    device_type = get_phy_devtype(phypath)
    if device_type:
        data.update({'device_type': get_phy_devtype(phypath)})
    
    enable = get_phy_enable(phypath)
    if enable:
        data.update({'enable': enable})

    linkrate = get_phy_negotiatedlinkrate(phypath)
    if linkrate:
        data.update({'negotiated_linkrate': linkrate})

    phyid = get_phy_phyid(phypath)
    if phyid:
        data.update({'phy_identifier': phyid})

    sasaddress = get_phy_sasaddress(phypath)
    if sasaddress:
        data.update({'sas_address': sasaddress})

    return data


def get_phy_devtype(phypath):
    devtype = get_device_data(glob.glob(os.path.join(phypath, 'sas_phy/phy-*'))[0], 'device_type')
    return devtype


def get_phy_enable(phypath):
    enable = get_device_data(glob.glob(os.path.join(phypath, 'sas_phy/phy-*'))[0], 'enable')
    return enable


def get_phy_negotiatedlinkrate(phypath):
    linkrate = get_device_data(glob.glob(os.path.join(phypath, 'sas_phy/phy-*'))[0], 'negotiated_linkrate')
    return linkrate


def get_phy_phyid(phypath):
    phyid = get_device_data(glob.glob(os.path.join(phypath, 'sas_phy/phy-*'))[0], 'phy_identifier')
    return phyid


def get_phy_sasaddress(phypath):
    address = get_device_data(glob.glob(os.path.join(phypath, 'sas_phy/phy-*'))[0], 'sas_address')
    return address


#
# Port Data
#
def get_phy_port(phypath):
    return glob.glob(os.path.join(phypath, 'port'))


#
# EndDevice Data
#
def get_port_enddevices(portpath):
    return glob.glob(os.path.join(portpath, 'end_device-[0-9]*'))


def get_enddevice_data(devicepath):
    data = {}

    bayid = get_enddevice_sasdevice_bayid(devicepath)
    if bayid:
        data.update({'bay_identifier': bayid})

    enclosureid = get_enddevice_sasdevice_enclosureid(devicepath)
    if enclosureid:
        data.update({'enclosure_identifier': enclosureid})

    phyid = get_enddevice_sasdevice_phyid(devicepath)
    if phyid:
        data.update({'phy_identifier': phyid})

    sasaddress = get_enddevice_sasdevice_sasaddress(devicepath)
    if sasaddress:
        data.update({'sas_address': sasaddress})

    targetid = get_enddevice_sasdevice_targetid(devicepath)
    if targetid:
        data.update({'scsi_target_id': targetid})

    return data


def get_enddevice_sasdevice_bayid(devicepath):
    bayid = get_device_data(glob.glob(os.path.join(devicepath, 'sas_device/end_device*'))[0], 'bay_identifier')
    return bayid


def get_enddevice_sasdevice_enclosureid(devicepath):
    enclosureid = get_device_data(glob.glob(os.path.join(devicepath, 'sas_device/end_device*'))[0], 'enclosure_identifier')
    return enclosureid


def get_enddevice_sasdevice_phyid(devicepath):
    phyid = get_device_data(glob.glob(os.path.join(devicepath, 'sas_device/end_device*'))[0], 'phy_identifier')
    return phyid


def get_enddevice_sasdevice_sasaddress(devicepath):
    address = get_device_data(glob.glob(os.path.join(devicepath, 'sas_device/end_device*'))[0], 'sas_address')
    return address


def get_enddevice_sasdevice_targetid(devicepath):
    targetid = get_device_data(glob.glob(os.path.join(devicepath, 'sas_device/end_device*'))[0], 'scsi_target_id')
    return targetid


#
# Target Data
#
def get_enddevice_targets(devicepath):
    return glob.glob(os.path.join(devicepath, 'target[0-9]*'))


# 
# LUN Device Data
# 
def get_target_luns(targetpath):
    return glob.glob(os.path.join(targetpath, '[0-9]*'))


def get_lun_data(devicepath):
    data = {}

    model = get_lun_model(devicepath)
    if model:
        data.update({'model': model})

    sasaddress = get_lun_sasaddress(devicepath)
    if sasaddress:
        data.update({'sas_address': sasaddress})

    scsilevel = get_lun_scsilevel(devicepath)
    if scsilevel:
        data.update({'scsi_level': scsilevel})

    serial = get_lun_serial(devicepath)
    if serial:
        data.update({'serial': serial})

    state = get_lun_state(devicepath)
    if state:
        data.update({'state': state})

    vendor = get_lun_vendor(devicepath)
    if vendor:
        data.update({'vendor': vendor})

    wwid = get_lun_wwid(devicepath)
    if wwid:
        data.update({'wwid': wwid})

    return data


def get_lun_model(devicepath):
    model = get_device_data(devicepath, 'model')
    return model


def get_lun_sasaddress(devicepath):
    address = get_device_data(devicepath, 'sas_address')
    return address


def get_lun_scsilevel(devicepath):
    scsilevel = get_device_data(devicepath, 'scsi_level')
    return scsilevel


def get_lun_serial(devicepath):
    serial = filter(str.isalnum, get_device_data(devicepath, 'vpd_pg80'))
    return serial
    
def get_lun_state(devicepath):
    state = get_device_data(devicepath, 'state')
    return state


def get_lun_vendor(devicepath):
    vendor = get_device_data(devicepath, 'vendor')
    return vendor


def get_lun_wwid(devicepath):
    wwid = get_device_data(devicepath, 'wwid')
    return wwid


#
# Blockdev Data
#
def get_lun_blockdevs(lunpath):
    return glob.glob(os.path.join(lunpath, 'block/*'))


def get_blockdev_data(devpath):
    data = {}

    badblocks = get_blockdev_badblocks(devpath)
    if badblocks:
        data.update({'badblocks': badblocks})

    stat = get_blockdev_stat(devpath)
    if stat:
        data.update({'stat': stat})

    return data


def get_blockdev_badblocks(devpath):
    badblocks = get_device_data(devpath, 'badblocks')
    return badblocks


def get_blockdev_stat(devpath):
    stat = get_device_data(devpath, 'stat')
    return stat


#
# Main function walks sysfs, fetching data about the SCSI bus
#
def main():
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.ERROR)
    logging.info('Collecting device information')

    tree = {
        'blockdevcount': 0,
        'devicecount': 0,
        'hostcount': 0,
        'hosts': {},
        'luncount': 0,
        'phycount': 0,
        'portcount': 0,
        'system': get_system_identifiers(),
        'targetcount': 0
    }

    hosts = get_scsi_bus_hosts()
    if hosts:
        hosts.sort()
    for host in hosts:
        tree['hostcount'] += 1
        host_name = os.path.basename(get_canonical_path(host))
        tree['hosts'][host_name] = get_host_data(host)

        phys = get_host_phys(host)
        if phys:
            phys.sort()
        for phy in phys:
            tree['phycount'] += 1
            phy_name = os.path.basename(get_canonical_path(phy))
            tree['hosts'][host_name][phy_name] = get_phy_data(phy)

            ports = get_phy_port(phy)
            if ports:
                ports.sort()
            for port in ports:
                tree['portcount'] += 1
                port_name = os.path.basename(get_canonical_path(port))
                tree['hosts'][host_name][phy_name][port_name] = {}

                enddevs = get_port_enddevices(port)
                if enddevs:
                    enddevs.sort()
                for enddev in enddevs:
                    tree['devicecount'] += 1
                    enddev_name = os.path.basename(get_canonical_path(enddev))
                    tree['hosts'][host_name][phy_name][port_name][enddev_name] = get_enddevice_data(enddev)

                    targets = get_enddevice_targets(enddev)
                    if targets:
                        targets.sort()
                    for target in targets:
                        tree['targetcount'] += 1
                        target_name = os.path.basename(get_canonical_path(target))
                        tree['hosts'][host_name][phy_name][port_name][enddev_name][target_name] = {}

                        luns = get_target_luns(target)
                        if luns:
                            luns.sort()
                        for lun in luns:
                            tree['luncount'] += 1
                            lun_name = os.path.basename(get_canonical_path(lun))
                            tree['hosts'][host_name][phy_name][port_name][enddev_name][target_name][lun_name] = get_lun_data(lun)

                            blockdevs = get_lun_blockdevs(lun)
                            if blockdevs:
                                blockdevs.sort()
                            for blockdev in blockdevs:
                                tree['blockdevcount'] += 1
                                blockdev_name = os.path.basename(get_canonical_path(blockdev))
                                tree['hosts'][host_name][phy_name][port_name][enddev_name][target_name][lun_name][blockdev_name] = get_blockdev_data(blockdev)

    logging.info('Finished collecting device information')
    print(json.dumps(tree, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
