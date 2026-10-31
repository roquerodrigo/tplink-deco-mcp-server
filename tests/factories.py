"""SDK records with realistic defaults, overridable per test."""

from __future__ import annotations

from dataclasses import replace

from tplink_deco_api import (
    AddressReservation,
    AddressReservationTable,
    BlockedClient,
    ClientDevice,
    Device,
    InternetStatus,
    IotHost,
    IpInfo,
    IpStatus,
    LanDetails,
    LogType,
    MloHost,
    Performance,
    SignalLevel,
    SystemLogEntry,
    SystemLogPage,
    WanDetails,
    WanInfo,
    WlanBackhaul,
    WlanBand,
    WlanConfig,
    WlanGuest,
    WlanHost,
)

_CLIENT = ClientDevice(
    mac="AA:BB:CC:DD:EE:01",
    ip="192.168.68.10",
    name="Living Room TV",
    up_speed=10,
    down_speed=200,
    wire_type="wireless",
    connection_type="band5",
    space_id="1",
    access_host="1",
    interface="main",
    client_type="Television",
    owner_id="",
    remain_time=0,
    online=True,
    client_mesh=True,
    enable_priority=False,
)

_DEVICE = Device(
    mac="0C:EF:15:00:00:01",
    device_ip="192.168.68.1",
    device_model="BE65",
    device_type="HOMEWIFISYSTEM",
    role="master",
    nickname="living_room",
    custom_nickname="Living Room",
    hardware_ver="2.0",
    software_ver="1.3.3 Build 26071612",
    oem_id="",
    hw_id="",
    bssid_2g="",
    bssid_5g="",
    bssid_sta_2g="",
    bssid_sta_5g="",
    inet_status="online",
    inet_error_msg="well",
    group_status="connected",
    signal_level=SignalLevel(band2_4="0", band5="0", band6="0"),
    product_level=0,
    set_gateway_support=True,
    support_plc=False,
    oversized_firmware=False,
    nand_flash=True,
)


def client_device(**overrides: object) -> ClientDevice:
    return replace(_CLIENT, **overrides)


def device(**overrides: object) -> Device:
    return replace(_DEVICE, **overrides)


def blocked_client(mac: str = "AA:BB:CC:DD:EE:09") -> BlockedClient:
    return BlockedClient(mac=mac, name="Tablet", client_type="Mobile")


def reservation_table(*reservations: AddressReservation) -> AddressReservationTable:
    return AddressReservationTable(reservations=reservations, max_count=64)


def log_types() -> list[LogType]:
    return [LogType(name="ALL", value=8), LogType(name="NOTICE", value=5)]


def system_log_page(page: int = 2) -> SystemLogPage:
    entry = SystemLogEntry(
        time="Mon Oct 26 13:57:02 2026",
        facility="daemon",
        level="notice",
        source="pppd[18932]",
        message="len < 0",
    )
    return SystemLogPage(page=page, total_pages=3, entries=(entry,))


def performance() -> Performance:
    return Performance(cpu_usage=0.125, mem_usage=0.4)


def internet_status() -> InternetStatus:
    return InternetStatus(
        ipv4=IpStatus("online", "connected", "pppoe", "pppoe", 0),
        ipv6=IpStatus("offline", "unknown", "unknown", "unknown", 1),
        link_status="plugged",
    )


def wan_info() -> WanInfo:
    return WanInfo(
        wan=WanDetails(
            ip_info=IpInfo(
                "203.0.113.7", "255.255.255.255", "", "203.0.113.1", "1.1.1.1", "8.8.8.8"
            ),
            dial_type="pppoe",
            enable_auto_dns=False,
        ),
        lan=LanDetails(ip_info=IpInfo("192.168.68.1", "255.255.255.0", "", "", "", "")),
    )


def _band(ssid: str, *, enable: bool = True, guest_enable: bool = True) -> WlanBand:
    return WlanBand(
        host=WlanHost(
            ssid=ssid,
            password="main-secret",
            channel=36,
            enable=enable,
            mode="11ax",
            channel_width="HT80",
            enable_hide_ssid=False,
        ),
        guest=WlanGuest(ssid=f"{ssid} Guest", password="guest-secret", enable=guest_enable),
        backhaul=WlanBackhaul(channel=149),
    )


def wlan_config(
    *,
    band6: WlanBand | None = None,
    iot_ssid: str = "Home IoT",
    mlo_ssid: str = "Home",
) -> WlanConfig:
    return WlanConfig(
        band2_4=_band("Home"),
        band5_1=_band("Home"),
        band6=band6 if band6 is not None else _band("Home 6", guest_enable=False),
        iot_host=IotHost(
            ssid=iot_ssid,
            password="iot-secret",
            encryption_mode="wpa2",
            enable=True,
            enable_2g=True,
            enable_5g=False,
        ),
        mlo_host=MloHost(
            ssid=mlo_ssid,
            password="main-secret",
            enable=True,
            band=("band5", "band6"),
            enable_hide_ssid=True,
        ),
    )


def empty_band() -> WlanBand:
    return WlanBand(
        host=WlanHost("", "", 0, enable=False, mode="", channel_width="", enable_hide_ssid=False),
        guest=WlanGuest("", "", enable=False),
        backhaul=WlanBackhaul(channel=0),
    )


def disabled_band(ssid: str) -> WlanBand:
    return _band(ssid, enable=False, guest_enable=False)
