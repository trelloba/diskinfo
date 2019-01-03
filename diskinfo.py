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

# /sys/class/scsi_host/host0/device/phy-0:0/sas_phy/phy-0:0/device/port/end_device-0:0/target0:0:0/0:0:0:0/block/sda
# /sys/class/scsi_host/host2/device/target2:0:0/2:0:0:0/block/sdq/
# Hba -> Phy -> Device -> Port -> EndDevice -> Target -> Device -> BlockDevice
# Hba -> Phy -> Port -> Expander -> Phy -> Port -> EndDevice -> Target -> Device -> BlockDevice


class Hba(dict):
    def __init__(self, path, **kwargs):
        self._device_path = os.path.realpath(os.path.abspath(path))
        self._data_path = os.path.join(self.device_path, 'scsi_host/', os.path.split(self.device_path)[-1])
        super(Hba, self).__init__(**kwargs)
        self.phys = []

    @property
    def active_mode(self):
        return get_sysfs_data(self.data_path, 'active_mode')

    @property
    def board_assembly(self):
        return get_sysfs_data(self.data_path, 'board_assembly')

    @property
    def board_name(self):
        return get_sysfs_data(self.data_path, 'board_name')

    @property
    def board_tracer(self):
        return get_sysfs_data(self.data_path, 'board_tracer')

    @property
    def brm_status(self):
        return get_sysfs_data(self.data_path, 'BRM_status')

    @property
    def can_queue(self):
        return get_sysfs_data(self.data_path, 'can_queue')

    @property
    def cmd_per_lun(self):
        return get_sysfs_data(self.data_path, 'cmd_per_lun')

    @property
    def eh_deadline(self):
        return get_sysfs_data(self.data_path, 'eh_deadline')

    @property
    def fw_queue_depth(self):
        return get_sysfs_data(self.data_path, 'fw_queue_depth')

    @property
    def host_busy(self):
        return get_sysfs_data(self.data_path, 'host_busy')

    @property
    def host_sas_address(self):
        return get_sysfs_data(self.data_path, 'host_sas_address')

    @property
    def ioc_reset_count(self):
        return get_sysfs_data(self.data_path, 'ioc_reset_count')

    @property
    def io_delay(self):
        return get_sysfs_data(self.data_path, 'io_delay')

    @property
    def logging_level(self):
        return get_sysfs_data(self.data_path, 'logging_level')

    @property
    def proc_name(self):
        return get_sysfs_data(self.data_path, 'proc_name')

    @property
    def prot_capabilities(self):
        return get_sysfs_data(self.data_path, 'prot_capabilities')

    @property
    def prot_guard_type(self):
        return get_sysfs_data(self.data_path, 'prot_guard_type')

    @property
    def reply_queue_count(self):
        return get_sysfs_data(self.data_path, 'reply_queue_count')

    @property
    def sg_prot_tablesize(self):
        return get_sysfs_data(self.data_path, 'sg_prot_tablesize')

    @property
    def sg_tablesize(self):
        return get_sysfs_data(self.data_path, 'sg_tablesize')

    @property
    def state(self):
        return get_sysfs_data(self.data_path, 'state')

    @property
    def supported_mode(self):
        return get_sysfs_data(self.data_path, 'supported_mode')

    @property
    def unchecked_isa_dma(self):
        return get_sysfs_data(self.data_path, 'unchecked_isa_dma')

    @property
    def unique_id(self):
        return get_sysfs_data(self.data_path, 'unique_id')

    @property
    def use_blk_mq(self):
        return get_sysfs_data(self.data_path, 'use_blk_mq')

    @property
    def version_bios(self):
        return get_sysfs_data(self.data_path, 'version_bios')

    @property
    def version_fw(self):
        return get_sysfs_data(self.data_path, 'version_fw')

    @property
    def version_mpi(self):
        return get_sysfs_data(self.data_path, 'version_mpi')

    @property
    def version_nvdata_default(self):
        return get_sysfs_data(self.data_path, 'version_nvdata_default')

    @property
    def version_nvdata_persistent(self):
        return get_sysfs_data(self.data_path, 'version_nvdata_persistent')

    @property
    def version_product(self):
        return get_sysfs_data(self.data_path, 'version_product')

    @property
    def data_path(self):
        return self._data_path

    @data_path.setter
    def data_path(self, value):
        self._data_path = value

    @property
    def device_path(self):
        return self._device_path

    @device_path.setter
    def device_path(self, value):
        self._device_path = value

    @property
    def is_sas(self):
        try:
            return os.path.exists(os.path.join(self.device_path, 'sas_host'))
        except OSError as e:
            logging.warning('Unable to determine if Host is SAS. %s', e)
            return False

    def to_json(self):
        return json.dumps(
            {'active_mode': self.active_mode,
             'board_assembly': self.board_assembly,
             'board_name': self.board_name,
             'board_tracer': self.board_tracer,
             'brm_status': self.brm_status,
             'can_queue': self.can_queue,
             'cmd_per_lun': self.cmd_per_lun,
             'eh_deadline': self.eh_deadline,
             'fw_queue_depth': self.fw_queue_depth,
             'host_busy': self.host_busy,
             'host_sas_address': self.host_sas_address,
             'ioc_reset_count': self.ioc_reset_count,
             'io_delay': self.io_delay,
             'logging_level': self.logging_level,
             'proc_name': self.proc_name,
             'prot_capabilities': self.prot_capabilities,
             'prot_guard_type': self.prot_guard_type,
             'reply_queue_count': self.reply_queue_count,
             'sg_prot_tablesize': self.sg_prot_tablesize,
             'sg_tablesize': self.sg_tablesize,
             'state': self.state,
             'supported_mode': self.supported_mode,
             'unchecked_isa_dma': self.unchecked_isa_dma,
             'unique_id': self.unique_id,
             'use_blk_mq': self.use_blk_mq,
             'version_bios': self.version_bios,
             'version_fw': self.version_fw,
             'version_mpi': self.version_mpi,
             'version_nvdata_default': self.version_nvdata_default,
             'version_nvdata_persistent': self.version_nvdata_persistent,
             'version_product': self.version_product,
             'phys': [p.to_json() for p in self.phys]})


class Phy(dict):
    def __init__(self, path, **kwargs):
        self._device_path = os.path.realpath(os.path.abspath(path))
        self._data_path = os.path.join(self.device_path, 'sas_phy/', os.path.split(self.device_path)[-1])
        super(Phy, self).__init__(**kwargs)
        self.ports = []

    @property
    def device_type(self):
        return get_sysfs_data(self.data_path, 'device_type')

    @property
    def enable(self):
        return get_sysfs_data(self.data_path, 'enable')

    @property
    def initiator_port_protocols(self):
        return get_sysfs_data(self.data_path, 'initiator_port_protocols')

    @property
    def invalid_dword_count(self):
        return get_sysfs_data(self.data_path, 'invalid_dword_count')

    @property
    def loss_of_dword_sync_count(self):
        return get_sysfs_data(self.data_path, 'loss_of_dword_sync_count')

    @property
    def maximum_linkrate(self):
        return get_sysfs_data(self.data_path, 'maximum_linkrate')

    @property
    def maximum_linkrate_hw(self):
        return get_sysfs_data(self.data_path, 'maximum_linkrate_hw')

    @property
    def minimum_linkrate(self):
        return get_sysfs_data(self.data_path, 'minimum_linkrate')

    @property
    def minimum_linkrate_hw(self):
        return get_sysfs_data(self.data_path, 'minimum_linkrate_hw')

    @property
    def negotiated_linkrate(self):
        return get_sysfs_data(self.data_path, 'negotiated_linkrate')

    @property
    def phy_identifier(self):
        return get_sysfs_data(self.data_path, 'phy_identifier')

    @property
    def phy_reset_problem_count(self):
        return get_sysfs_data(self.data_path, 'phy_reset_problem_count')

    @property
    def running_disparity_error_count(self):
        return get_sysfs_data(self.data_path, 'running_disparity_error_count')

    @property
    def sas_address(self):
        return get_sysfs_data(self.data_path, 'sas_address')

    @property
    def target_port_protocols(self):
        return get_sysfs_data(self.data_path, 'target_port_protocols')

    @property
    def data_path(self):
        return self._data_path

    @data_path.setter
    def data_path(self, value):
        self._data_path = value

    @property
    def device_path(self):
        return self._device_path

    @device_path.setter
    def device_path(self, value):
        self._device_path = value

    @property
    def is_sas(self):
        try:
            return os.path.exists(os.path.join(self.device_path, 'sas_phy'))
        except OSError as e:
            logging.warning('Unable to determine if Phy is SAS. %s', e)
            return False

    def to_json(self):
        return json.dumps(
            {'device_type': self.device_type,
             'enable': self.enable,
             'initiator_port_protocols': self.initiator_port_protocols,
             'invalid_dword_count': self.invalid_dword_count,
             'loss_of_dword_sync_count': self.loss_of_dword_sync_count,
             'maximum_linkrate': self.maximum_linkrate,
             'maximum_linkrate_hw': self.maximum_linkrate_hw,
             'minimum_linkrate': self.minimum_linkrate,
             'minimum_linkrate_hw': self.minimum_linkrate_hw,
             'negotiated_linkrate': self.negotiated_linkrate,
             'phy_identifier': self.phy_identifier,
             'phy_reset_problem_count': self.phy_reset_problem_count,
             'running_disparity_error_count': self.running_disparity_error_count,
             'sas_address': self.sas_address,
             'target_port_protocols': self.target_port_protocols,
             'ports': [p.to_json for p in self.ports]})


class Port(dict):
    def __init__(self, path, **kwargs):
        self._device_path = os.path.realpath(os.path.abspath(path))
        self._data_path = os.path.join(self.device_path, 'sas_port/', os.path.split(self.device_path)[-1])
        super(Port, self).__init__(**kwargs)
        self.end_devices = []

    @property
    def num_phys(self):
        return get_sysfs_data(self.data_path, 'num_phys')

    @property
    def data_path(self):
        return self._data_path

    @data_path.setter
    def data_path(self, value):
        self._data_path = value

    @property
    def device_path(self):
        return self._device_path

    @device_path.setter
    def device_path(self, value):
        self._device_path = value

    @property
    def is_sas(self):
        try:
            return os.path.exists(os.path.join(self.device_path, 'sas_port'))
        except OSError as e:
            logging.warning('Unable to determine if Port is SAS. %s', e)
            return False

    def to_json(self):
        return json.dumps({'num_phys': self.num_phys,
                           'end_devices': self.end_devices})


class EndDevice(dict):
    def __init__(self, path, **kwargs):
        self._device_path = os.path.realpath(os.path.abspath(path))
        self._data_path = os.path.join(self.device_path, 'sas_device/', os.path.split(self.device_path)[-1])
        super(EndDevice, self).__init__(**kwargs)
        self.targets = []

    @property
    def bay_identifier(self):
        return get_sysfs_data(self.data_path, 'bay_identifier')

    @property
    def device_type(self):
        return get_sysfs_data(self.data_path, 'device_type')

    @property
    def enclosure_identifier(self):
        return get_sysfs_data(self.data_path, 'enclosure_identifier')

    @property
    def initiator_port_protocols(self):
        return get_sysfs_data(self.data_path, 'initiator_port_protocols')

    @property
    def phy_identifier(self):
        return get_sysfs_data(self.data_path, 'phy_identifier')

    @property
    def sas_address(self):
        return get_sysfs_data(self.data_path, 'sas_address')

    @property
    def scsi_target_id(self):
        return get_sysfs_data(self.data_path, 'scsi_target_id')

    @property
    def target_port_protocols(self):
        return get_sysfs_data(self.data_path, 'target_port_protocols')

    @property
    def data_path(self):
        return self._data_path

    @data_path.setter
    def data_path(self, value):
        self._data_path = value

    @property
    def device_path(self):
        return self._device_path

    @device_path.setter
    def device_path(self, value):
        self._device_path = value

    @property
    def is_sas(self):
        try:
            return os.path.exists(os.path.join(self.device_path, 'sas_device'))
        except OSError as e:
            logging.warning('Unable to determine if EndDevice is SAS. %s', e)
            return False

    def to_json(self):
        return json.dumps(
            {'bay_identifier': self.bay_identifier,
             'device_type': self.device_type,
             'enclosure_identifier': self.enclosure_identifier,
             'initiator_port_protocols': self.initiator_port_protocols,
             'phy_identifier': self.phy_identifier,
             'sas_address': self.sas_address,
             'scsi_target_id': self.scsi_target_id,
             'target_port_protocols': self.target_port_protocols,
             'targets': self.targets})


class Target(object):
    def __init__(self, path, **kwargs):
        self._device_path = os.path.realpath(os.path.abspath(path))
        super(Target, self).__init__(**kwargs)
        self.devices = []

    @property
    def data_path(self):
        return self._device_path

    @property
    def device_path(self):
        return self._device_path

    @device_path.setter
    def device_path(self, value):
        self._device_path = value

    def to_json(self):
        return json.dumps({'devices': self.devices})


class Device(object):
    def __init__(self, path, **kwargs):
        self._device_path = os.path.realpath(os.path.abspath(path))
        super(Device, self).__init__(**kwargs)
        self.block_devices = []

    @property
    def device_blocked(self):
        return get_sysfs_data(self.data_path, 'device_blocked')

    @property
    def device_busy(self):
        return get_sysfs_data(self.data_path, 'device_busy')

    @property
    def dh_state(self):
        return get_sysfs_data(self.data_path, 'dh_state')

    @property
    def eh_timeout(self):
        return get_sysfs_data(self.data_path, 'eh_timeout')

    @property
    def evt_capacity_change_reported(self):
        return get_sysfs_data(self.data_path, 'evt_capacity_change_reported')

    @property
    def evt_inquiry_change_reported(self):
        return get_sysfs_data(self.data_path, 'evt_inquiry_change_reported')

    @property
    def evt_lun_change_reported(self):
        return get_sysfs_data(self.data_path, 'evt_lun_change_reported')

    @property
    def evt_media_change(self):
        return get_sysfs_data(self.data_path, 'evt_media_change')

    @property
    def evt_mode_parameter_change_reported(self):
        return get_sysfs_data(self.data_path, 'evt_mode_parameter_change_reported')

    @property
    def evt_soft_threshold_reached(self):
        return get_sysfs_data(self.data_path, 'evt_soft_threshold_reached')

    @property
    def inquiry(self):
        return get_sysfs_data(self.data_path, 'inquiry')

    @property
    def iocounterbits(self):
        return get_sysfs_data(self.data_path, 'iocounterbits')

    @property
    def iodone_cnt(self):
        return get_sysfs_data(self.data_path, 'iodone_cnt')

    @property
    def ioerr_cnt(self):
        return get_sysfs_data(self.data_path, 'ioerr_cnt')

    @property
    def iorequest_cnt(self):
        return get_sysfs_data(self.data_path, 'iorequest_cnt')

    @property
    def model(self):
        return get_sysfs_data(self.data_path, 'model')

    @property
    def queue_depth(self):
        return get_sysfs_data(self.data_path, 'queue_depth')

    @property
    def queue_ramp_up_period(self):
        return get_sysfs_data(self.data_path, 'queue_ramp_up_period')

    @property
    def queue_type(self):
        return get_sysfs_data(self.data_path, 'queue_type')

    @property
    def rev(self):
        return get_sysfs_data(self.data_path, 'rev')

    @property
    def sas_address(self):
        return get_sysfs_data(self.data_path, 'sas_address')

    @property
    def sas_device_handle(self):
        return get_sysfs_data(self.data_path, 'sas_device_handle')

    @property
    def scsi_level(self):
        return get_sysfs_data(self.data_path, 'scsi_level')

    @property
    def state(self):
        return get_sysfs_data(self.data_path, 'state')

    @property
    def timeout(self):
        return get_sysfs_data(self.data_path, 'timeout')

    @property
    def type(self):
        return get_sysfs_data(self.data_path, 'type')

    @property
    def vendor(self):
        return get_sysfs_data(self.data_path, 'vendor')

    @property
    def vpd_pg80(self):
        return get_sysfs_data(self.data_path, 'vpd_pg80')

    @property
    def vpd_pg83(self):
        return get_sysfs_data(self.data_path, 'vpd_pg83')

    @property
    def wwid(self):
        return get_sysfs_data(self.data_path, 'wwid')

    @property
    def data_path(self):
        return self._device_path

    @property
    def device_path(self):
        return self._device_path

    @device_path.setter
    def device_path(self, value):
        self._device_path = value

    @property
    def is_sas(self):
        try:
            return os.path.exists(os.path.join(self.device_path, 'sas_address'))
        except OSError as e:
            logging.warning('Unable to determine if Device is SAS. %s', e)
            return False

    def to_json(self):
        return json.dumps(
            {'device_blocked': self.device_blocked,
             'device_busy': self.device_busy,
             'dh_state': self.dh_state,
             'eh_timeout': self.eh_timeout,
             'evt_capacity_change_reported': self.evt_capacity_change_reported,
             'evt_inquiry_change_reported': self.evt_inquiry_change_reported,
             'evt_lun_change_reported': self.evt_lun_change_reported,
             'evt_media_change': self.evt_media_change,
             'evt_mode_parameter_change_reported': self.evt_mode_parameter_change_reported,
             'evt_soft_threshold_reached': self.evt_soft_threshold_reached,
             'inquiry': self.inquiry,
             'iocounterbits': self.iocounterbits,
             'iodone_cnt': self.iodone_cnt,
             'ioerr_cnt': self.ioerr_cnt,
             'iorequest_cnt': self.iorequest_cnt,
             'model': self.model,
             'queue_depth': self.queue_depth,
             'queue_ramp_up_period': self.queue_ramp_up_period,
             'queue_type': self.queue_type,
             'rev': self.rev,
             'sas_address': self.sas_address,
             'sas_device_handle': self.sas_device_handle,
             'scsi_level': self.scsi_level,
             'state': self.state,
             'timeout': self.timeout,
             'type': self.type,
             'vendor': self.vendor,
             'vpd_pg80': self.vpd_pg80,
             'vpd_pg83': self.vpd_pg83,
             'wwid': self.wwid,
             'block_devices': self.block_devices})


class BlockDevice(object):
    def __init__(self, path, **kwargs):
        self._device_path = os.path.realpath(os.path.abspath(path))
        super(BlockDevice, self).__init__(**kwargs)

    @property
    def alignment_offset(self):
        return get_sysfs_data(self.data_path, 'alignment_offset')

    @property
    def badblocks(self):
        return get_sysfs_data(self.data_path, 'badblocks')

    @property
    def capability(self):
        return get_sysfs_data(self.data_path, 'capability')

    @property
    def dev(self):
        return get_sysfs_data(self.data_path, 'dev')

    @property
    def discard_alignment(self):
        return get_sysfs_data(self.data_path, 'discard_alignment')

    @property
    def ext_range(self):
        return get_sysfs_data(self.data_path, 'ext_range')

    @property
    def range(self):
        return get_sysfs_data(self.data_path, 'range')

    @property
    def removable(self):
        return get_sysfs_data(self.data_path, 'removable')

    @property
    def ro(self):
        return get_sysfs_data(self.data_path, 'ro')

    @property
    def size(self):
        return get_sysfs_data(self.data_path, 'size')

    @property
    def stat(self):
        return get_sysfs_data(self.data_path, 'stat')

    @property
    def data_path(self):
        return self._device_path

    @property
    def device_path(self):
        return self._device_path

    @device_path.setter
    def device_path(self, value):
        self._device_path = value

    @property
    def is_sas(self):
        try:
            # TODO: Research what SAS-specific content is created for SAS block
            #  devices. Currently this fails intentionally.
            return os.path.exists(os.path.join(self.device_path, 'does_not_exist'))
        except OSError as e:
            logging.warning('Unable to determine if BlockDevice is SAS. %s', e)
            return False

    def to_json(self):
        return json.dumps(
            {'alignment_offset': self.alignment_offset,
             'badblocks': self.badblocks,
             'capability': self.capability,
             'dev': self.dev,
             'discard_alignment': self.discard_alignment,
             'ext_range': self.ext_range,
             'range': self.range,
             'removable': self.removable,
             'ro': self.ro,
             'size': self.size,
             'stat': self.stat})


class Host(dict):
    def __init__(self, *args, **kwargs):
        self._device_path = os.path.realpath(os.path.abspath('/sys/devices/virtual/dmi'))
        self._data_path = os.path.join(self.device_path, 'id/')
        super(Host, self).__init__(*args, **kwargs)
        self.targets = []

    @property
    def hostname(self):
        """ Return the system's hostname. If the hostname is an empty string
        return None instead so the JSON output is consistent. """
        return platform.node() or None

    @property
    def bios_date(self):
        return get_sysfs_data(self.data_path, 'bios_date')

    @property
    def bios_vendor(self):
        return get_sysfs_data(self.data_path, 'bios_vendor')

    @property
    def bios_version(self):
        return get_sysfs_data(self.data_path, 'bios_version')

    @property
    def board_asset_tag(self):
        return get_sysfs_data(self.data_path, 'board_asset_tag')

    @property
    def board_name(self):
        return get_sysfs_data(self.data_path, 'board_name')

    @property
    def board_serial(self):
        return get_sysfs_data(self.data_path, 'board_serial')

    @property
    def board_vendor(self):
        return get_sysfs_data(self.data_path, 'board_vendor')

    @property
    def board_version(self):
        return get_sysfs_data(self.data_path, 'board_version')

    @property
    def chassis_asset_tag(self):
        return get_sysfs_data(self.data_path, 'chassis_asset_tag')

    @property
    def chassis_serial(self):
        return get_sysfs_data(self.data_path, 'chassis_serial')

    @property
    def chassis_type(self):
        return get_sysfs_data(self.data_path, 'chassis_type')

    @property
    def chassis_vendor(self):
        return get_sysfs_data(self.data_path, 'chassis_vendor')

    @property
    def chassis_version(self):
        return get_sysfs_data(self.data_path, 'chassis_version')

    @property
    def product_family(self):
        return get_sysfs_data(self.data_path, 'product_family')

    @property
    def product_name(self):
        return get_sysfs_data(self.data_path, 'product_name')

    @property
    def product_serial(self):
        return get_sysfs_data(self.data_path, 'product_serial')

    @property
    def product_sku(self):
        return get_sysfs_data(self.data_path, 'product_sku')

    @property
    def product_uuid(self):
        return get_sysfs_data(self.data_path, 'product_uuid')

    @property
    def product_version(self):
        return get_sysfs_data(self.data_path, 'product_version')

    @property
    def sys_vendor(self):
        return get_sysfs_data(self.data_path, 'sys_vendor')

    @property
    def data_path(self):
        return self._data_path

    @data_path.setter
    def data_path(self, value):
        self._data_path = value

    @property
    def device_path(self):
        return self._device_path

    @device_path.setter
    def device_path(self, value):
        self._device_path = value


def get_canonical_path(path):
    return os.path.realpath(os.path.abspath(path))
    

def get_sysfs_data(devicepath, item):
    itempath = os.path.join(devicepath, item)
    logging.debug('Reading %s', itempath)
    try:
        itemfile = open(file=itempath, mode='r')
        iremdata = itemfile.read()
        itemfile.close()
        return iremdata.strip()
    except Exception as e:
        logging.warning('Unable to read %s from %s. %s', item, devicepath, e)
        return None


#
# Collect Classes
#
def collect_scsi_hbas():
    hbas = []
    for scsi_hba in glob.glob('/sys/bus/scsi/devices/host*'):
        hba = Hba(path=scsi_hba)
        hbas.append(hba)

    return hbas


def collect_scsi_host_phys(hba):
    phys = []
    for host_phy in glob.glob(os.path.join(hba.device_path, 'phy-*')):
        phy = Phy(path=host_phy)
        phys.append(phy)

    return phys


def collect_scsi_phy_ports(phy):
    ports = []
    for phy_port in glob.glob(os.path.join(phy.device_path, 'port')):
        port = Port(path=phy_port)
        ports.append(port)

    return ports


def collect_scsi_port_end_devices(port):
    end_devices = []
    for port_end_device in glob.glob(os.path.join(port.device_path, 'end_device-*')):
        end_device = EndDevice(path=port_end_device)
        end_devices.append(end_device)

    return end_devices


def collect_scsi_end_device_targets(end_device):
    targets = []
    for end_device_target in glob.glob(os.path.join(end_device.device_path, 'target[0-9]')):
        target = Target(path=end_device_target)
        targets.append(target)

    return targets


def collect_scsi_target_devices(target):
    devices = []
    for target_device in glob.glob(os.path.join(target.device_path, '[0-9]*')):
        device = Device(path=target_device)
        devices.append(device)

    return devices


def collect_scsi_block_devices(device):
    block_devices = []
    for scsi_block_device in glob.glob(os.path.join(device.device_path, 'block/sd*')):
        device = BlockDevice(path=scsi_block_device)
        block_devices.append(device)

    return block_devices


def collect_host_data():
    host = Host()
    return host


#
# Old methods
#
def get_system_identifiers():
    data = {}

    boardname = get_sysfs_data('/sys/devices/virtual/dmi/id', 'board_name')
    if boardname:
        data.update({'board_name': boardname})

    boardserial = get_sysfs_data('/sys/devices/virtual/dmi/id', 'board_serial')
    if boardserial:
        data.update({'board_serial': boardserial})

    boardvendor = get_sysfs_data('/sys/devices/virtual/dmi/id', 'board_vendor')
    if boardvendor:
        data.update({'board_vendor': boardvendor})

    chassisserial = get_sysfs_data('/sys/devices/virtual/dmi/id', 'chassis_serial')
    if chassisserial:
        data.update({'chassis_serial': chassisserial})

    chassisserial = get_sysfs_data('/sys/devices/virtual/dmi/id', 'chassis_serial')
    if chassisserial:
        data.update({'chassis_serial': chassisserial})

    chassisvendor = get_sysfs_data('/sys/devices/virtual/dmi/id', 'chassis_vendor')
    if chassisvendor:
        data.update({'chassis_vendor': chassisvendor})

    hostname = platform.node().split('.')[0]
    if hostname:
        data.update({'hostname': hostname})

    productname = get_sysfs_data('/sys/devices/virtual/dmi/id', 'product_name')
    if productname:
        data.update({'product_name': productname})

    productserial = get_sysfs_data('/sys/devices/virtual/dmi/id', 'product_serial')
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
    boardname = get_sysfs_data(glob.glob(os.path.join(hostpath, 'scsi_host/host[0-9]*'))[0], 'board_name')
    return boardname


def get_host_sasaddress(hostpath):
    address = get_sysfs_data(glob.glob(os.path.join(hostpath, 'scsi_host/host[0-9]*'))[0], 'host_sas_address')
    return address


def get_host_state(hostpath):
    state = get_sysfs_data(glob.glob(os.path.join(hostpath, 'scsi_host/host[0-9]*'))[0], 'state')
    return state


def get_host_uniqueid(hostpath):
    uniqueid = get_sysfs_data(glob.glob(os.path.join(hostpath, 'scsi_host/host[0-9]*'))[0], 'unique_id')
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
    devtype = get_sysfs_data(glob.glob(os.path.join(phypath, 'sas_phy/phy-*'))[0], 'device_type')
    return devtype


def get_phy_enable(phypath):
    enable = get_sysfs_data(glob.glob(os.path.join(phypath, 'sas_phy/phy-*'))[0], 'enable')
    return enable


def get_phy_negotiatedlinkrate(phypath):
    linkrate = get_sysfs_data(glob.glob(os.path.join(phypath, 'sas_phy/phy-*'))[0], 'negotiated_linkrate')
    return linkrate


def get_phy_phyid(phypath):
    phyid = get_sysfs_data(glob.glob(os.path.join(phypath, 'sas_phy/phy-*'))[0], 'phy_identifier')
    return phyid


def get_phy_sasaddress(phypath):
    address = get_sysfs_data(glob.glob(os.path.join(phypath, 'sas_phy/phy-*'))[0], 'sas_address')
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
    bayid = get_sysfs_data(
        glob.glob(os.path.join(devicepath, 'sas_device/end_device*'))[0],
        'bay_identifier'
    )
    return bayid


def get_enddevice_sasdevice_enclosureid(devicepath):
    enclosureid = get_sysfs_data(
        glob.glob(os.path.join(devicepath, 'sas_device/end_device*'))[0],
        'enclosure_identifier'
    )
    return enclosureid


def get_enddevice_sasdevice_phyid(devicepath):
    phyid = get_sysfs_data(
        glob.glob(os.path.join(devicepath, 'sas_device/end_device*'))[0],
        'phy_identifier'
    )
    return phyid


def get_enddevice_sasdevice_sasaddress(devicepath):
    address = get_sysfs_data(
        glob.glob(os.path.join(devicepath, 'sas_device/end_device*'))[0],
        'sas_address'
    )
    return address


def get_enddevice_sasdevice_targetid(devicepath):
    targetid = get_sysfs_data(
        glob.glob(os.path.join(devicepath, 'sas_device/end_device*'))[0],
        'scsi_target_id'
    )
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
    model = get_sysfs_data(devicepath, 'model')
    return model


def get_lun_sasaddress(devicepath):
    address = get_sysfs_data(devicepath, 'sas_address')
    return address


def get_lun_scsilevel(devicepath):
    scsilevel = get_sysfs_data(devicepath, 'scsi_level')
    return scsilevel


def get_lun_serial(devicepath):
    serial = filter(str.isalnum, get_sysfs_data(devicepath, 'vpd_pg80'))
    return serial
    

def get_lun_state(devicepath):
    state = get_sysfs_data(devicepath, 'state')
    return state


def get_lun_vendor(devicepath):
    vendor = get_sysfs_data(devicepath, 'vendor')
    return vendor


def get_lun_wwid(devicepath):
    wwid = get_sysfs_data(devicepath, 'wwid')
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
    badblocks = get_sysfs_data(devpath, 'badblocks')
    return badblocks


def get_blockdev_stat(devpath):
    stat = get_sysfs_data(devpath, 'stat')
    return stat


#
# Main function walks sysfs, fetching data about the SCSI bus
#
def main():
    logging.basicConfig(
        format='%(levelname)s: %(message)s',
        level=logging.ERROR
    )
    logging.info('Collecting device information')

    # Use new functions to iterate through classes instead of the kludge of
    # previous functions.

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

    hba_devices = glob.glob('/sys/bus/scsi/devices/host[0-9]*')
    if hba_devices:
        hba_devices.sort()
        tree['hostcount'] = hba_devices.count()

    for hba_device in hba_devices:
        hba = Hba(hba_device)
        hba_name = os.path.basename(hba.device_path)
        tree['hosts'][hba_name] = hba.to_json()

        phy_devices = glob.glob(os.path.join(hba.device_path, 'phy-[0-9]*'))
        if phy_devices:
            phy_devices.sort()
            tree['phycount'] += phy_devices.count()

        for phy_device in phy_devices:
            phy = Phy(phy_device)
            phy_name = os.path.basename(phy.device_path)
            tree['hosts'][hba_name][phy_name] = phy.to_json()

            hba_ports = glob.glob(os.path.join(phy.device_path, 'port'))
            if hba_ports:
                hba_ports.sort()
                tree['portcount'] += hba_ports.count()

            for hba_port in hba_ports:
                # TODO: Check for expanders here, which will also have Phy and Port children.
                port = Port(hba_port)
                port_name = os.path.basename(port.device_path)
                tree['hosts'][hba_name][phy_name][port_name] = port.to_json()

                port_end_devices = glob.glob(os.path.join(port.device_path, 'end_device-[0-9]*'))
                if port_end_devices:
                    port_end_devices.sort()
                    target['devicecount'] += port_end_devices.count()

                for port_end_device in port_end_devices:
                    end_device = EndDevice(port_end_device)
                    end_device_name = os.path.basename(end_device.device_path)
                    tree['hosts'][hba_name][phy_name][port_name][end_device_name] = end_device.to_json()

                    port_targets = glob.glob(os.path.join(end_device.device_path, 'target[0-9]*'))
                    if port_targets:
                        port_targets.sort()
                        target['targetcount'] += port_targets.count()

                    for port_target in port_targets:
                        target = Target(port_target)
                        target_name = os.path.basename(target.device_path)
                        tree['hosts'][hba_name][phy_name][port_name][end_device_name][target_name] = target.to_json()

                        target_luns = glob.glob(os.path.join(end_device.device_path, '[0-9]*'))
                        if target_luns:
                            target_luns.sort()
                            target['luncount'] += target_luns.count()

                        for target_lun in target_luns:
                            lun = Lun(target_lun)
                            target_name = os.path.basename(target.device_path)
                            tree['hosts'][hba_name][phy_name][port_name][end_device_name][target_name] = target.to_json()

                        #
                        # # Hba -> Phy -> Port -> Expander -> Phy -> Port -> EndDevice -> Target -> Device -> BlockDevice
                        #
                        luns = get_target_luns(target)
                        if luns:
                            luns.sort()
                        for lun in luns:
                            tree['luncount'] += 1
                            lun_name = os.path.basename(
                                get_canonical_path(lun)
                            )
                            tree['hosts'][host_name][phy_name][port_name][enddev_name][target_name][lun_name] = \
                                get_lun_data(lun)

                            blockdevs = get_lun_blockdevs(lun)
                            if blockdevs:
                                blockdevs.sort()
                            for blockdev in blockdevs:
                                tree['blockdevcount'] += 1
                                blockdev_name = os.path.basename(
                                    get_canonical_path(blockdev)
                                )
                                tree['hosts'][host_name][phy_name][port_name][enddev_name][target_name][lun_name][blockdev_name] = \
                                    get_blockdev_data(blockdev)

    logging.info('Finished collecting device information')
    print('##########')
    print(json.dumps(tree, indent=2, sort_keys=True))
    print('##########')


if __name__ == "__main__":
    main()
