"""
TCP开关实体实现
"""
from __future__ import annotations
import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import DeviceInfo
from .client import TCPClient
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """设置开关实体"""
    host = config_entry.data["host"]
    port = config_entry.data["port"]
    
    client = TCPClient(host, port)
    if not await client.connect():
        return False
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = client
    
    # 创建设备
    device_info = DeviceInfo(
        identifiers={(DOMAIN, f"tcp_switch_{host}_{port}")},
        manufacturer="Custom TCP",
        name=f"TCP Switch {host}:{port}",
    )
    
    # 创建8个通道开关
    entities = [
        TCPSwitch(client, f"channel_{i+1}", device_info)
        for i in range(8)
    ]
    async_add_entities(entities)

class TCPSwitch(SwitchEntity):
    """TCP开关实体"""
    
    def __init__(self, client, channel, device_info):
        self._client = client
        self._channel = channel
        self._attr_unique_id = f"{client.host}_{client.port}_{channel}"
        self._attr_device_info = device_info
        self._attr_is_on = False

    async def async_turn_on(self, **kwargs):
        """打开开关"""
        if await self._client.send_command(f"ON {self._channel}"):
            self._attr_is_on = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """关闭开关"""
        if await self._client.send_command(f"OFF {self._channel}"):
            self._attr_is_on = False
            self.async_write_ha_state()