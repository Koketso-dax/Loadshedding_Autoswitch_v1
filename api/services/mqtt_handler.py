"""MQTT Client Module for handling device metrics

This module manages MQTT connections and message handling for IoT devices,
including metric validation, storage, and error handling.
"""
from __future__ import annotations
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
import paho.mqtt.client as mqtt
from flask import Flask, current_app
from sqlalchemy.exc import SQLAlchemyError
from models.device import Device
from models.metric import Metric, MetricType


logger = logging.getLogger(__name__)


class MQTTHandler:
    """Handler for MQTT client connections and message processing"""

    def __init__(self, app: Flask):
        self.app = app
        self.clients: List[mqtt.Client] = []
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure logging for MQTT operations"""
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(handler)
        logger.setLevel(self.app.config.get('MQTT_LOG_LEVEL', logging.INFO))

    def on_connect(self, client: mqtt.Client, userdata: Any,
                   flags: Dict, rc: int) -> None:
        """Handle client connection events"""
        device_id = userdata.get('device_id')
        if rc == 0:
            logger.info(f"Device {device_id} connected successfully")
            # Subscribe to device-specific topics
            client.subscribe(f"devices/{device_id}/metrics/#")
            client.subscribe(f"devices/{device_id}/status")
        else:
            logger.error(f"Device {device_id}\
                         connection failed with code {rc}")

    def on_message(self, client: mqtt.Client, userdata: Any,
                   msg: mqtt.MQTTMessage) -> None:
        """Process incoming MQTT messages"""
        try:
            # Parse topic to get device_id and metric_type
            topics = msg.topic.split('/')
            if len(topics) < 4:
                logger.error(f"Invalid topic format: {msg.topic}")
                return

            device_id = int(topics[1])
            metric_type_name = topics[3]

            # Parse message payload
            try:
                payload = json.loads(msg.payload.decode('utf-8'))
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON payload from device {device_id}")
                return

            with self.app.app_context():
                self._process_metric(device_id, metric_type_name, payload)

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")

    def _process_metric(self, device_id: int, metric_type_name: str,
                        payload: Dict[str, Any]) -> None:
        """Process and store metric data"""
        try:
            # Validate device and metric type
            device = Device.query.get(device_id)
            metric_type = MetricType.query.filter_by(
                name=metric_type_name).first()

            if not device or not metric_type:
                logger.error(f"Invalid device {device_id}\
                             or metric type {metric_type_name}")
                return

            # Extract and validate metric data
            timestamp = datetime.fromisoformat(payload.get('timestamp',
                                               datetime.now().isoformat()))
            value = float(payload.get('value'))
            quality = float(payload.get('quality', 1.0))
            metadata = payload.get('metadata', {})

            # Create and validate metric
            metric = Metric(
                device_id=device_id,
                metric_type_id=metric_type.id,
                timestamp=timestamp,
                value=value,
                quality=quality,
                metadata=metadata
            )

            # Batch insert if multiple metrics are queued
            if hasattr(current_app, 'metric_queue'):
                current_app.metric_queue.append(metric.to_dict())
                if len(current_app.metric_queue) >= \
                   current_app.config.get('MQTT_BATCH_SIZE', 100):
                    Metric.batch_insert(current_app.metric_queue)
                    current_app.metric_queue.clear()
            else:
                metric.save()

        except ValueError as e:
            logger.error(f"Validation error for device {device_id}: {str(e)}")
        except SQLAlchemyError as e:
            logger.error(f"Database error for device {device_id}: {str(e)}")

    def init_clients(self) -> List[mqtt.Client]:
        """Initialize MQTT clients for all devices"""
        try:
            devices = Device.query.all()
            for device in devices:
                client = mqtt.Client(userdata={'device_id': device.id})
                client.username_pw_set(device.device_key,
                                       device.user.password_hash)
                client.on_connect = self.on_connect
                client.on_message = self.on_message

                # Configure TLS if enabled
                if self.app.config.get('MQTT_USE_TLS', False):
                    client.tls_set(
                        ca_certs=self.app.config.get('MQTT_CA_CERTS'),
                        certfile=self.app.config.get('MQTT_CERTFILE'),
                        keyfile=self.app.config.get('MQTT_KEYFILE')
                    )

                # Configure connection parameters
                client.connect(
                    host=self.app.config['MQTT_BROKER'],
                    port=self.app.config['MQTT_PORT'],
                    keepalive=self.app.config.get('MQTT_KEEPALIVE', 60)
                )

                client.loop_start()
                self.clients.append(client)

            logger.info(f"Initialized {len(self.clients)} MQTT clients")
            self.app.mqtt_handler = self
            return self.clients

        except Exception as e:
            logger.error(f"Error initializing MQTT clients: {str(e)}")
            return []

    def cleanup(self) -> None:
        """Clean up MQTT clients and connections"""
        for client in self.clients:
            try:
                client.loop_stop()
                client.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting client: {str(e)}")
        self.clients.clear()


def init_mqtt_handler(app: Flask) -> MQTTHandler:
    """Initialize the MQTT handler with the Flask app"""
    handler = MQTTHandler(app)
    handler.init_clients()
    return handler
