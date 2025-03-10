"""
TCP传感器实体实现
"""
from __future__ import annotations
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import DeviceInfo
from . import DOMAIN
from .client import TCPClient

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """设置传感器实体"""
    host = config_entry.data["host"]
    port = config_entry.data["port"]
    
    client = TCPClient(host, port)
    if not await client.connect():
        return False
    
    # 创建设备信息（与switch共用）
    device_info = DeviceInfo(
        identifiers={(DOMAIN, f"tcp_switch_{host}_{port}")},
        manufacturer="Custom TCP",
        name=f"TCP Switch {host}:{port}"
    )
    
    # 创建电压/电流传感器
    entities = [
        TCPSensor(client, "voltage", "V", device_info),
        TCPSensor(client, "current", "A", device_info)
    ]
    async_add_entities(entities)

class TCPSensor(SensorEntity):
    """TCP传感器实体"""
    
    def __init__(self, client, sensor_type, unit, device_info):
        self._client = client
        self._type = sensor_type
        self._attr_name = f"TCP {sensor_type.capitalize()}"
        self._attr_native_unit_of_measurement = unit
        self._attr_unique_id = f"{client.host}_{client.port}_{sensor_type}"
        self._attr_device_info = device_info

    async def async_update(self):
        """更新传感器数据"""
        try:
            # 发送查询指令并解析响应
            self._client.writer.write(f"GET_{self._type.upper()}".encode())
            await self._client.writer.drain()
            response = await self._client.reader.readuntil(separator=b'\n')
            value = float(response.decode().strip())
            self._attr_native_value = round(value, 2)
        except Exception as e:
            _LOGGER.error("传感器更新失败: %s", e)