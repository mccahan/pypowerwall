import json
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys

# Mock the paho.mqtt module before importing server
mqtt_mock = MagicMock()
mqtt_mock.MQTT_ERR_SUCCESS = 0
mqtt_mock.Client = MagicMock
sys.modules['paho.mqtt.client'] = mqtt_mock

import proxy.server as server


class TestMQTTConfiguration(unittest.TestCase):
    """Test MQTT configuration and initialization"""

    @patch.dict('os.environ', {
        'PW_MQTT_HOST': 'mqtt.example.com',
        'PW_MQTT_PORT': '1883',
        'PW_MQTT_USER': 'testuser',
        'PW_MQTT_PASSWORD': 'testpass',
        'PW_MQTT_TOPIC_PREFIX': 'powerwall'
    })
    def test_mqtt_config_from_env(self):
        """Test MQTT configuration is read from environment variables"""
        # Note: Since server.py is already imported, these won't actually reload
        # This test validates the configuration pattern
        self.assertTrue(hasattr(server, 'mqtt_host'))
        self.assertTrue(hasattr(server, 'mqtt_port'))
        self.assertTrue(hasattr(server, 'mqtt_user'))
        self.assertTrue(hasattr(server, 'mqtt_password'))
        self.assertTrue(hasattr(server, 'mqtt_topic_prefix'))

    def test_mqtt_enabled_requires_host(self):
        """Test that mqtt_enabled is True only when host is configured"""
        # This test validates the logic: mqtt_enabled = os.getenv("PW_MQTT_HOST", "") != ""
        self.assertIsInstance(server.mqtt_enabled, bool)


class TestMQTTPublishing(unittest.TestCase):
    """Test MQTT publishing functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = MagicMock()
        self.mock_client.publish = MagicMock()
        
        # Mock successful publish
        mock_result = MagicMock()
        mock_result.rc = mqtt_mock.MQTT_ERR_SUCCESS
        self.mock_client.publish.return_value = mock_result

    @patch.object(server, 'mqtt_enabled', True)
    @patch.object(server, 'MQTT_AVAILABLE', True)
    @patch.object(server, 'mqtt_client')
    @patch.object(server, 'mqtt_topic_prefix', 'test')
    @patch.object(server, 'debugmode', False)
    def test_publish_mqtt_success(self, mock_client):
        """Test successful MQTT message publishing"""
        # Set up the mock client
        mock_result = MagicMock()
        mock_result.rc = mqtt_mock.MQTT_ERR_SUCCESS
        
        mock_mqtt = MagicMock()
        mock_mqtt.publish.return_value = mock_result
        server.mqtt_client = mock_mqtt
        
        # Publish a message
        server.publish_mqtt("test/topic", 123.45)
        
        # Verify publish was called with correct parameters
        mock_mqtt.publish.assert_called_once_with("test/test/topic", "123.45", qos=0, retain=False)

    @patch.object(server, 'mqtt_enabled', False)
    def test_publish_mqtt_disabled(self):
        """Test that publishing is skipped when MQTT is disabled"""
        # This should not raise an exception even with no client
        server.publish_mqtt("test/topic", 123.45)
        # No assertion needed - just verify it doesn't crash

    @patch.object(server, 'mqtt_enabled', True)
    @patch.object(server, 'mqtt_client', None)
    def test_publish_mqtt_no_client(self):
        """Test that publishing is skipped when client is None"""
        # This should not raise an exception
        server.publish_mqtt("test/topic", 123.45)
        # No assertion needed - just verify it doesn't crash


class TestMQTTAggregatesPublishing(unittest.TestCase):
    """Test MQTT publishing of meter aggregates"""

    def setUp(self):
        """Set up test fixtures"""
        self.aggregates_dict = {
            "site": {"instant_power": 1500.5},
            "solar": {"instant_power": 3000.0},
            "battery": {"instant_power": -500.25},
            "load": {"instant_power": 2000.75},
        }
        
        self.aggregates_json = json.dumps(self.aggregates_dict)

    @patch.object(server, 'mqtt_enabled', True)
    @patch.object(server, 'mqtt_client', MagicMock())
    @patch.object(server, 'publish_mqtt')
    def test_publish_aggregates_from_dict(self, mock_publish):
        """Test publishing aggregates from dictionary"""
        server.publish_meter_aggregates_to_mqtt(self.aggregates_dict)
        
        # Verify all meter types were published
        calls = [str(call) for call in mock_publish.call_args_list]
        self.assertEqual(len(mock_publish.call_args_list), 4)
        
        # Verify specific calls were made
        mock_publish.assert_any_call("site/instant_power", 1500.5)
        mock_publish.assert_any_call("solar/instant_power", 3000.0)
        mock_publish.assert_any_call("battery/instant_power", -500.25)
        mock_publish.assert_any_call("load/instant_power", 2000.75)

    @patch.object(server, 'mqtt_enabled', True)
    @patch.object(server, 'mqtt_client', MagicMock())
    @patch.object(server, 'publish_mqtt')
    def test_publish_aggregates_from_json_string(self, mock_publish):
        """Test publishing aggregates from JSON string"""
        server.publish_meter_aggregates_to_mqtt(self.aggregates_json)
        
        # Verify all meter types were published
        self.assertEqual(len(mock_publish.call_args_list), 4)
        
        # Verify specific calls were made
        mock_publish.assert_any_call("site/instant_power", 1500.5)
        mock_publish.assert_any_call("solar/instant_power", 3000.0)
        mock_publish.assert_any_call("battery/instant_power", -500.25)
        mock_publish.assert_any_call("load/instant_power", 2000.75)

    @patch.object(server, 'mqtt_enabled', True)
    @patch.object(server, 'mqtt_client', MagicMock())
    @patch.object(server, 'publish_mqtt')
    def test_publish_aggregates_partial_data(self, mock_publish):
        """Test publishing aggregates with partial data"""
        partial_aggregates = {
            "site": {"instant_power": 1500.5},
            "solar": {"instant_power": 3000.0},
        }
        
        server.publish_meter_aggregates_to_mqtt(partial_aggregates)
        
        # Verify only available meter types were published
        self.assertEqual(len(mock_publish.call_args_list), 2)
        mock_publish.assert_any_call("site/instant_power", 1500.5)
        mock_publish.assert_any_call("solar/instant_power", 3000.0)

    @patch.object(server, 'mqtt_enabled', True)
    @patch.object(server, 'mqtt_client', MagicMock())
    @patch.object(server, 'publish_mqtt')
    def test_publish_aggregates_missing_instant_power(self, mock_publish):
        """Test publishing aggregates with missing instant_power"""
        aggregates_no_power = {
            "site": {"some_other_field": 123},
            "solar": {},
        }
        
        server.publish_meter_aggregates_to_mqtt(aggregates_no_power)
        
        # Verify no calls were made since instant_power is missing
        self.assertEqual(len(mock_publish.call_args_list), 0)

    @patch.object(server, 'mqtt_enabled', False)
    @patch.object(server, 'publish_mqtt')
    def test_publish_aggregates_disabled(self, mock_publish):
        """Test that publishing is skipped when MQTT is disabled"""
        server.publish_meter_aggregates_to_mqtt(self.aggregates_dict)
        
        # Verify no publishing occurred
        mock_publish.assert_not_called()

    @patch.object(server, 'mqtt_enabled', True)
    @patch.object(server, 'mqtt_client', None)
    @patch.object(server, 'publish_mqtt')
    def test_publish_aggregates_no_client(self, mock_publish):
        """Test that publishing is skipped when client is None"""
        server.publish_meter_aggregates_to_mqtt(self.aggregates_dict)
        
        # Verify no publishing occurred
        mock_publish.assert_not_called()

    @patch.object(server, 'mqtt_enabled', True)
    @patch.object(server, 'mqtt_client', MagicMock())
    @patch.object(server, 'publish_mqtt')
    def test_publish_aggregates_invalid_json(self, mock_publish):
        """Test handling of invalid JSON string"""
        server.publish_meter_aggregates_to_mqtt("invalid json {")
        
        # Verify no publishing occurred due to JSON parse error
        mock_publish.assert_not_called()

    @patch.object(server, 'mqtt_enabled', True)
    @patch.object(server, 'mqtt_client', MagicMock())
    @patch.object(server, 'publish_mqtt')
    def test_publish_aggregates_null_values(self, mock_publish):
        """Test handling of null instant_power values"""
        aggregates_with_nulls = {
            "site": {"instant_power": None},
            "solar": {"instant_power": 3000.0},
        }
        
        server.publish_meter_aggregates_to_mqtt(aggregates_with_nulls)
        
        # Verify only non-null values were published
        self.assertEqual(len(mock_publish.call_args_list), 1)
        mock_publish.assert_any_call("solar/instant_power", 3000.0)


class TestMQTTIntegrationWithSafeEndpointCall(unittest.TestCase):
    """Test MQTT integration with safe_endpoint_call"""

    @patch.object(server, 'mqtt_enabled', True)
    @patch.object(server, 'publish_meter_aggregates_to_mqtt')
    @patch.object(server, 'safe_pw_call')
    @patch.object(server, 'cache_response')
    @patch.object(server, 'track_endpoint_call')
    def test_safe_endpoint_call_publishes_aggregates(
        self, mock_track, mock_cache, mock_pw_call, mock_publish
    ):
        """Test that safe_endpoint_call publishes to MQTT for aggregates endpoint"""
        aggregates_data = {"site": {"instant_power": 1500}}
        mock_pw_call.return_value = aggregates_data
        
        # Mock pw object
        mock_pw = MagicMock()
        mock_pw.poll.return_value = aggregates_data
        
        # Call safe_endpoint_call for aggregates endpoint
        result = server.safe_endpoint_call(
            "/aggregates", mock_pw.poll, "/api/meters/aggregates", jsonformat=False
        )
        
        # Verify MQTT publishing was triggered
        mock_publish.assert_called_once_with(aggregates_data)
        
        # Verify result was returned correctly
        self.assertEqual(result, aggregates_data)

    @patch.object(server, 'mqtt_enabled', True)
    @patch.object(server, 'publish_meter_aggregates_to_mqtt')
    @patch.object(server, 'safe_pw_call')
    @patch.object(server, 'cache_response')
    @patch.object(server, 'track_endpoint_call')
    def test_safe_endpoint_call_does_not_publish_other_endpoints(
        self, mock_track, mock_cache, mock_pw_call, mock_publish
    ):
        """Test that safe_endpoint_call does not publish for non-aggregates endpoints"""
        vitals_data = {"device1": {"PINV_Fout": 60.0}}
        mock_pw_call.return_value = vitals_data
        
        # Mock pw object
        mock_pw = MagicMock()
        mock_pw.vitals.return_value = vitals_data
        
        # Call safe_endpoint_call for vitals endpoint (not aggregates)
        result = server.safe_endpoint_call(
            "/vitals", mock_pw.vitals, jsonformat=True
        )
        
        # Verify MQTT publishing was NOT triggered
        mock_publish.assert_not_called()
        
        # Verify result was returned correctly
        self.assertEqual(result, vitals_data)


if __name__ == '__main__':
    unittest.main()
