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
import re
# import sys

# Hba -> Phy -> Port -> Expander -> Phy -> Port -> EndDevice -> Target -> Device -> BlockDevice
# /sys/class/scsi_host/host0/device/phy-0:0/sas_phy/phy-0:0/device/port/end_device-0:0/target0:0:0/0:0:0:0/block/sda


class Hba(dict):
    def __init__(self, path, **kwargs):
        self._device_path = get_canonical_path(path)
        self._data_path = os.path.join(self.device_path, 'scsi_host/', os.path.basename(self.device_path))
        super(Hba, self).__init__(**kwargs)

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
    def name(self):
        return os.path.basename(self.device_path)

    @property
    def is_sas(self):
        try:
            return os.path.exists(os.path.join(self.device_path, 'sas_host'))
        except OSError as e:
            logging.warning('Unable to determine if Host is SAS. %s', e)
            return False

    def dump(self):
        return {'active_mode': self.active_mode,
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
             'version_product': self.version_product}


class Phy(dict):
    def __init__(self, path, **kwargs):
        self._device_path = get_canonical_path(path)
        self._data_path = os.path.join(self.device_path, 'sas_phy/', os.path.basename(self.device_path))
        super(Phy, self).__init__(**kwargs)

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
    def name(self):
        return os.path.basename(self.device_path)

    @property
    def is_sas(self):
        try:
            return os.path.exists(os.path.join(self.device_path, 'sas_phy'))
        except OSError as e:
            logging.warning('Unable to determine if Phy is SAS. %s', e)
            return False

    def dump(self):
        return {'device_type': self.device_type,
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
             'target_port_protocols': self.target_port_protocols}


class Port(dict):
    def __init__(self, path, **kwargs):
        self._device_path = get_canonical_path(path)
        self._data_path = os.path.join(self.device_path, 'sas_port/', os.path.basename(self.device_path))
        super(Port, self).__init__(**kwargs)

    @property
    def expanders(self):
        return sorted(glob.glob(os.path.join(self.device_path, 'expander-*')))

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
    def has_expander(self):
        if self.expanders:
            return True
        return False

    @property
    def name(self):
        return os.path.basename(self.device_path)

    @property
    def is_sas(self):
        try:
            return os.path.exists(os.path.join(self.device_path, 'sas_port'))
        except OSError as e:
            logging.warning('Unable to determine if Port is SAS. %s', e)
            return False

    def dump(self):
        return {'num_phys': self.num_phys}


class EndDevice(dict):
    def __init__(self, path, **kwargs):
        self._device_path = get_canonical_path(path)
        self._data_path = os.path.join(self.device_path, 'sas_device/', os.path.basename(self.device_path))
        self._sas_data_path = os.path.join(self.device_path, 'sas_end_device/', os.path.basename(self.device_path))
        super(EndDevice, self).__init__(**kwargs)

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
    def i_t_nexus_loss_timeout(self):
        return get_sysfs_data(self.sas_data_path, 'i_t_nexus_loss_timeout')

    @property
    def initiator_port_protocols(self):
        return get_sysfs_data(self.data_path, 'initiator_port_protocols')

    @property
    def initiator_response_timeout(self):
        return get_sysfs_data(self.sas_data_path, 'initiator_response_timeout')

    @property
    def phy_identifier(self):
        return get_sysfs_data(self.data_path, 'phy_identifier')

    @property
    def ready_led_meaning(self):
        return get_sysfs_data(self.sas_data_path, 'ready_led_meaning')

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
    def tlr_enabled(self):
        return get_sysfs_data(self.sas_data_path, 'tlr_enabled')

    @property
    def tlr_supported(self):
        return get_sysfs_data(self.sas_data_path, 'tlr_supported')

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
    def name(self):
        return os.path.basename(self.device_path)

    @property
    def sas_data_path(self):
        return self._sas_data_path

    @property
    def is_sas(self):
        try:
            return os.path.exists(os.path.join(self.device_path, 'sas_device'))
        except OSError as e:
            logging.warning('Unable to determine if EndDevice is SAS. %s', e)
            return False

    def dump(self):
        return {'bay_identifier': self.bay_identifier,
             'device_type': self.device_type,
             'enclosure_identifier': self.enclosure_identifier,
             'i_t_nexus_loss_timeout': self.i_t_nexus_loss_timeout,
             'initiator_port_protocols': self.initiator_port_protocols,
             'initiator_response_timeout': self.initiator_response_timeout,
             'phy_identifier': self.phy_identifier,
             'ready_led_meaning': self.ready_led_meaning,
             'sas_address': self.sas_address,
             'scsi_target_id': self.scsi_target_id,
             'target_port_protocols': self.target_port_protocols,
             'tlr_enabled': self.tlr_enabled,
             'tlr_supported': self.tlr_supported}


class Target(object):
    def __init__(self, path, **kwargs):
        self._device_path = get_canonical_path(path)
        super(Target, self).__init__(**kwargs)

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
    def name(self):
        return os.path.basename(self.device_path)

    def dump(self):
        return {}


class Device(object):
    def __init__(self, path, **kwargs):
        self._device_path = get_canonical_path(path)
        super(Device, self).__init__(**kwargs)

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
    def name(self):
        return os.path.basename(self.device_path)

    @property
    def is_sas(self):
        try:
            return os.path.exists(os.path.join(self.device_path, 'sas_address'))
        except OSError as e:
            logging.warning('Unable to determine if Device is SAS. %s', e)
            return False

    def dump(self):
        return {'device_blocked': self.device_blocked,
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
                'wwid': self.wwid}


class BlockDevice(object):
    def __init__(self, path, **kwargs):
        self._device_path = get_canonical_path(path)
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
    def name(self):
        return os.path.basename(self.device_path)

    @property
    def is_sas(self):
        # TODO: Research what SAS-specific content is created for SAS block
        #  devices. Currently this fails intentionally.
        return False

    def dump(self):
        return {'alignment_offset': self.alignment_offset,
             'badblocks': self.badblocks,
             'capability': self.capability,
             'dev': self.dev,
             'discard_alignment': self.discard_alignment,
             'ext_range': self.ext_range,
             'range': self.range,
             'removable': self.removable,
             'ro': self.ro,
             'size': self.size,
             'stat': self.stat}


class Host(dict):
    def __init__(self, *args, **kwargs):
        self._device_path = get_canonical_path('/sys/devices/virtual/dmi')
        self._data_path = os.path.join(self.device_path, 'id/')
        super(Host, self).__init__(*args, **kwargs)
        self.targets = []

    def __repr__(self):
        return '<{} hostname={}, '\
               'bios_date={}, '\
               'bios_vendor={}, '\
               'bios_version={}, ' \
               'board_asset_tag={}, ' \
               'board_name={}, ' \
               'board_serial={}, ' \
               'board_vendor={}, ' \
               'board_version={}, ' \
               'chassis_asset_tag={}, ' \
               'chassis_serial={}, ' \
               'chassis_type={}, ' \
               'chassis_vendor={}, ' \
               'chassis_version={}, ' \
               'product_family={}, ' \
               'product_name={}, ' \
               'product_serial={}, ' \
               'product_sku={}, ' \
               'product_uuid={}, ' \
               'product_version={}, ' \
               'sys_vendor={}>'.format(
                    self.__class__.__name__,
                    self.hostname,
                    self.bios_date,
                    self.bios_vendor,
                    self.bios_version,
                    self.board_asset_tag,
                    self.board_name,
                    self.board_serial,
                    self.board_vendor,
                    self.board_version,
                    self.chassis_asset_tag,
                    self.chassis_serial,
                    self.chassis_type,
                    self.chassis_vendor,
                    self.chassis_version,
                    self.product_family,
                    self.product_name,
                    self.product_serial,
                    self.product_sku,
                    self.product_uuid,
                    self.product_version,
                    self.sys_vendor
                )

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

    def dump(self):
        return {'bios_date': self.bios_date,
             'bios_vendor': self.bios_vendor,
             'bios_version': self.bios_version,
             'board_asset_tag': self.board_asset_tag,
             'board_name': self.board_name,
             'board_serial': self.board_serial,
             'board_vendor': self.board_vendor,
             'board_version': self.board_version,
             'chassis_asset_tag': self.chassis_asset_tag,
             'chassis_serial': self.chassis_serial,
             'chassis_type': self.chassis_type,
             'chassis_vendor': self.chassis_vendor,
             'chassis_version': self.chassis_version,
             'product_family': self.product_family,
             'product_name': self.product_name,
             'product_serial': self.product_serial,
             'product_sku': self.product_sku,
             'product_uuid': self.product_uuid,
             'product_version': self.product_version,
             'sys_vendor': self.sys_vendor}


#
# Helper functions
#
def get_canonical_path(path):
    return os.path.realpath(os.path.abspath(path))
    

def get_sysfs_data(devicepath, item):
    itempath = os.path.join(devicepath, item)
    logging.debug('Reading %s', itempath)
    try:
        itemfile = open(itempath, mode='r')
        itemdata = itemfile.read()
        itemfile.close()
        itemdata = re.sub(r'[^\w\s]+','', itemdata)
        itemdata = re.sub(r'\s{2,}',' ', itemdata).strip()
        return itemdata
    except Exception as e:
        logging.warning('Unable to read %s from %s. %s', item, devicepath, e)
        return None


#
# Collect Classes
#
def collect_hbas():
    """
    Return a list of HBA devices found by this host
    :rtype: list
    """
    hbas = []
    for hba_path in sorted(glob.glob('/sys/bus/scsi/devices/host*')):
        hba = Hba(path=hba_path)
        hbas.append(hba)

    return hbas


def collect_phys(hba):
    """
    Return a list of Phys controlled by hba

    :param hba: An Hba class representing a SAS/SATA HBA
    :type hba: Hba
    :rtype: list
    """
    phys = []
    for phy_path in sorted(glob.glob(os.path.join(hba.device_path, 'phy-*'))):
        phy = Phy(path=phy_path)
        phys.append(phy)

    return phys


def collect_ports(phy):
    """
    Return a list of Ports utilizing phy

    :param phy: A Phy class representing a SAS/SATA Phy layer
    :type phy: Phy
    :rtype: list
    """
    ports = []
    for port_path in sorted(glob.glob(os.path.join(phy.device_path, 'port'))):
        port = Port(path=port_path)
        ports.append(port)

    return ports


def collect_end_devices(port):
    """
    Return a list of SAS/SATA end devices connected to port

    :param port: A Port class representing a SAS/SATA port
    :type port: Port
    :rtype: list
    """
    end_devices = []
    for end_device_path in sorted(glob.glob(os.path.join(port.device_path, 'end_device-*'))):
        end_device = EndDevice(path=end_device_path)
        end_devices.append(end_device)

    return end_devices


def collect_targets(end_device):
    """
    Return a list of targets exposed by end_device

    :param end_device: An EndDevice class representing a SAS/SATA port's end device
    :type end_device: EndDevice
    :rtype: list
    """
    targets = []
    for target_path in sorted(glob.glob(os.path.join(end_device.device_path, 'target[0-9]*'))):
        target = Target(path=target_path)
        targets.append(target)

    return targets


def collect_target_devices(target):
    """
    Return a list of devices connected through a target

    :param target: A Target class representing a SAS/SATA port's target
    :type target: Target
    :rtype: list
    """
    devices = []
    for target_device_path in sorted(glob.glob(os.path.join(target.device_path, '[0-9]*'))):
        device = Device(path=target_device_path)
        devices.append(device)

    return devices


def collect_block_devices(device):
    """
    Return a list of SCSI block devices behind device

    :param device: A Device class representing a SAS/SATA port's end device
    :type device: Device
    :rtype: list
    """
    block_devices = []
    for block_device_path in sorted(glob.glob(os.path.join(device.device_path, 'block/sd*'))):
        device = BlockDevice(path=block_device_path)
        block_devices.append(device)

    return block_devices


def collect_host_data():
    host = Host()
    return host


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

    #
    # Hba x -> Phy x -> Port x -> [Expander -> Phy -> Port ->] EndDevice x -> Target x -> Device x -> BlockDevice
    #
    tree = {
        'blockdevcount': 0,
        'devicecount': 0,
        'hostcount': 0,
        'hosts': {},
        'luncount': 0,
        'phycount': 0,
        'portcount': 0,
        'system': None,
        'targetcount': 0
    }
    host = collect_host_data()
    tree['system'] = host.dump()

    # Collect Hbas
    hba_devices = collect_hbas()
    if hba_devices:
        tree['hostcount'] = len(hba_devices)
    for hba in hba_devices:
        tree['hosts'][hba.name] = hba.dump()
        # Note: If there are no PHYs, this is a SATA HBA, slip to Targets

        # Collect Phys
        phys = collect_phys(hba)
        if phys:
            tree['phycount'] += len(phys)
            for phy in phys:
                tree['hosts'][hba.name][phy.name] = phy.dump()

                # Collect Ports
                ports = collect_ports(phy)
                if ports:
                    tree['portcount'] += len(ports)
                for port in ports:
                    tree['hosts'][hba.name][phy.name][port.name] = port.dump()

                    # Collect EndDevices
                    # TODO: Check for expanders here, which will also have Phy and Port children.
                    end_devices = collect_end_devices(port)
                    if end_devices:
                        tree['devicecount'] += len(end_devices)
                    for end_device in end_devices:
                        tree['hosts'][hba.name][phy.name][port.name][end_device.name] = end_device.dump()

                        # Collect Targets
                        targets = collect_targets(end_device)
                        if targets:
                            tree['targetcount'] += len(targets)
                        for target in targets:
                            tree['hosts'][hba.name][phy.name][port.name][end_device.name][target.name] = target.dump()

                            # Collect Devices
                            devices = collect_target_devices(target)
                            if devices:
                                tree['luncount'] += len(devices)
                            for device in devices:
                                tree['hosts'][hba.name][phy.name][port.name][end_device.name][target.name][device.name] = device.dump()

                                # Collect BlockDevices
                                block_devices = collect_block_devices(device)
                                if block_devices:
                                    tree['blockdevcount'] += len(block_devices)
                                for block_device in block_devices:
                                    tree['hosts'][hba.name][phy.name][port.name][end_device.name][target.name][device.name][block_device.name] = block_device.dump()

        else:
            # Collect Targets
            targets = collect_targets(hba)
            if targets:
                tree['targetcount'] += len(targets)
            for target in targets:
                tree['hosts'][hba.name][target.name] = target.dump()

                # Collect Devices
                devices = collect_target_devices(target)
                if devices:
                    tree['luncount'] += len(devices)
                for device in devices:
                    tree['hosts'][hba.name][target.name][device.name] = device.dump()

                    # Collect BlockDevices
                    block_devices = collect_block_devices(device)
                    if block_devices:
                        tree['blockdevcount'] += len(block_devices)
                    for block_device in block_devices:
                        tree['hosts'][hba.name][target.name][device.name][block_device.name] = block_device.dump()

    logging.info('Finished collecting device information')
    print('##########')
    print(json.dumps(tree, indent=2, sort_keys=True))
    print('##########')


if __name__ == "__main__":
    main()
