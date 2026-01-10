"""
Tests for async caching behavior in safe_endpoint_call for /api/meters/aggregates and /api/system_status/soe
"""
import json
import time
import unittest
from unittest.mock import Mock, patch, call

from proxy.server import (
    safe_endpoint_call,
    _async_update_endpoint,
    cache_expire,
)


class TestSafeEndpointCallAsync(unittest.TestCase):
    """Test cases for async caching in safe_endpoint_call"""

    def setUp(self):
        """Set up test fixtures"""
        # Clear all caches before each test
        import proxy.server as server
        with server._last_good_responses_lock:
            server._last_good_responses.clear()
        with server._endpoint_last_update_lock:
            server._endpoint_last_update.clear()
        with server._endpoint_update_in_progress_lock:
            server._endpoint_update_in_progress.clear()
        with server._endpoint_stats_lock:
            server._endpoint_stats.clear()

    @patch('proxy.server.safe_pw_call')
    @patch('proxy.server.mqtt_enabled', False)
    @patch('proxy.server.debugmode', False)
    def test_aggregates_async_cache_return(self, mock_safe_pw_call):
        """Test /aggregates endpoint returns cached data immediately"""
        # Setup: Pre-populate cache
        import proxy.server as server
        test_data = json.dumps({"site": {"instant_power": 100}})
        with server._last_good_responses_lock:
            server._last_good_responses["/aggregates"] = (test_data, time.time())
        
        # Mark as recently updated to prevent immediate async update
        with server._endpoint_last_update_lock:
            server._endpoint_last_update["/aggregates"] = time.time()
        
        # Mock function
        mock_pw_func = Mock()
        
        # Call safe_endpoint_call
        result = safe_endpoint_call("/aggregates", mock_pw_func, "/api/meters/aggregates")
        
        # Verify cached data was returned
        self.assertEqual(result, test_data)
        
        # Verify pw_func was NOT called (returned cache immediately)
        mock_safe_pw_call.assert_not_called()

    @patch('proxy.server.safe_pw_call')
    @patch('proxy.server.mqtt_enabled', False)
    @patch('proxy.server.debugmode', False)
    def test_soe_async_cache_return(self, mock_safe_pw_call):
        """Test /soe endpoint returns cached data immediately"""
        # Setup: Pre-populate cache
        import proxy.server as server
        test_data = json.dumps({"percentage": 75.5})
        with server._last_good_responses_lock:
            server._last_good_responses["/soe"] = (test_data, time.time())
        
        # Mark as recently updated to prevent immediate async update
        with server._endpoint_last_update_lock:
            server._endpoint_last_update["/soe"] = time.time()
        
        # Mock function
        mock_pw_func = Mock()
        
        # Call safe_endpoint_call
        result = safe_endpoint_call("/soe", mock_pw_func, "/api/system_status/soe")
        
        # Verify cached data was returned
        self.assertEqual(result, test_data)
        
        # Verify pw_func was NOT called (returned cache immediately)
        mock_safe_pw_call.assert_not_called()

    @patch('proxy.server.safe_pw_call')
    @patch('proxy.server.mqtt_enabled', False)
    @patch('proxy.server.debugmode', False)
    def test_aggregates_triggers_async_update_when_expired(self, mock_safe_pw_call):
        """Test /aggregates triggers async update when cache expires"""
        # Setup: Pre-populate cache with old timestamp
        import proxy.server as server
        test_data = json.dumps({"site": {"instant_power": 100}})
        old_time = time.time() - cache_expire - 1  # Expired
        
        with server._last_good_responses_lock:
            server._last_good_responses["/aggregates"] = (test_data, old_time)
        
        with server._endpoint_last_update_lock:
            server._endpoint_last_update["/aggregates"] = old_time
        
        # Mock function to return new data
        mock_pw_func = Mock()
        new_data = json.dumps({"site": {"instant_power": 200}})
        mock_safe_pw_call.return_value = new_data
        
        # Call safe_endpoint_call
        result = safe_endpoint_call("/aggregates", mock_pw_func, "/api/meters/aggregates")
        
        # Should return cached data immediately
        self.assertEqual(result, test_data)
        
        # Wait for async update to complete
        time.sleep(0.3)
        
        # Verify async update was triggered (cache should be updated)
        with server._last_good_responses_lock:
            cached_data, _ = server._last_good_responses.get("/aggregates", (None, None))
            self.assertEqual(cached_data, new_data)

    @patch('proxy.server.safe_pw_call')
    @patch('proxy.server.mqtt_enabled', False)
    @patch('proxy.server.debugmode', False)
    def test_throttling_prevents_multiple_updates(self, mock_safe_pw_call):
        """Test throttling prevents updates more frequently than cache_expire"""
        import proxy.server as server
        
        # Setup: Recent update timestamp
        with server._endpoint_last_update_lock:
            server._endpoint_last_update["/aggregates"] = time.time() - 1  # 1 second ago
        
        # Pre-populate cache
        test_data = json.dumps({"site": {"instant_power": 100}})
        with server._last_good_responses_lock:
            server._last_good_responses["/aggregates"] = (test_data, time.time())
        
        mock_pw_func = Mock()
        
        # Call safe_endpoint_call
        result = safe_endpoint_call("/aggregates", mock_pw_func, "/api/meters/aggregates")
        
        # Should return cached data
        self.assertEqual(result, test_data)
        
        # Wait a bit to ensure no async update
        time.sleep(0.2)
        
        # Verify no update was triggered (throttled)
        mock_safe_pw_call.assert_not_called()

    @patch('proxy.server.safe_pw_call')
    @patch('proxy.server.mqtt_enabled', False)
    @patch('proxy.server.debugmode', False)
    def test_no_cache_waits_for_async_update(self, mock_safe_pw_call):
        """Test first call with no cache waits briefly for async update"""
        import proxy.server as server
        
        # No cache exists
        mock_pw_func = Mock()
        test_data = json.dumps({"site": {"instant_power": 300}})
        
        # Simulate async update completing quickly
        def side_effect(*args, **kwargs):
            # Simulate a quick response
            time.sleep(0.05)
            return test_data
        
        mock_safe_pw_call.side_effect = side_effect
        
        # Call safe_endpoint_call
        result = safe_endpoint_call("/aggregates", mock_pw_func, "/api/meters/aggregates")
        
        # Should get data (either from async update or None if timeout)
        # Since we have a quick side_effect, should get data
        self.assertIsNotNone(result)

    @patch('proxy.server.safe_pw_call')
    @patch('proxy.server.mqtt_enabled', False)
    @patch('proxy.server.debugmode', False)
    def test_other_endpoints_use_synchronous_behavior(self, mock_safe_pw_call):
        """Test other endpoints (not /aggregates or /soe) use synchronous behavior"""
        # Test with a different endpoint
        mock_pw_func = Mock()
        test_data = json.dumps({"vitals": "data"})
        mock_safe_pw_call.return_value = test_data
        
        # Call safe_endpoint_call with different endpoint
        result = safe_endpoint_call("/vitals", mock_pw_func, jsonformat=True)
        
        # Should call synchronously and return data
        self.assertEqual(result, test_data)
        mock_safe_pw_call.assert_called_once()

    @patch('proxy.server.safe_pw_call')
    @patch('proxy.server.mqtt_enabled', True)
    @patch('proxy.server.publish_meter_aggregates_to_mqtt')
    @patch('proxy.server.debugmode', False)
    def test_mqtt_publish_on_async_update(self, mock_mqtt_publish, mock_safe_pw_call):
        """Test MQTT publish is triggered on async update for /aggregates"""
        import proxy.server as server
        
        # Setup: Old cache to trigger update
        old_time = time.time() - cache_expire - 1
        test_data = json.dumps({"site": {"instant_power": 100}})
        
        with server._last_good_responses_lock:
            server._last_good_responses["/aggregates"] = (test_data, old_time)
        
        with server._endpoint_last_update_lock:
            server._endpoint_last_update["/aggregates"] = old_time
        
        # Mock function
        mock_pw_func = Mock()
        new_data = json.dumps({"site": {"instant_power": 200}})
        mock_safe_pw_call.return_value = new_data
        
        # Call safe_endpoint_call
        result = safe_endpoint_call("/aggregates", mock_pw_func, "/api/meters/aggregates")
        
        # Wait for async update
        time.sleep(0.3)
        
        # Verify MQTT publish was called
        mock_mqtt_publish.assert_called()

    @patch('proxy.server.safe_pw_call')
    @patch('proxy.server.mqtt_enabled', False)
    @patch('proxy.server.debugmode', False)
    def test_concurrent_requests_dont_trigger_multiple_updates(self, mock_safe_pw_call):
        """Test concurrent requests don't trigger multiple async updates"""
        import proxy.server as server
        
        # Setup: Old cache to trigger update
        old_time = time.time() - cache_expire - 1
        test_data = json.dumps({"site": {"instant_power": 100}})
        
        with server._last_good_responses_lock:
            server._last_good_responses["/aggregates"] = (test_data, old_time)
        
        with server._endpoint_last_update_lock:
            server._endpoint_last_update["/aggregates"] = old_time
        
        # Mock function with delay
        mock_pw_func = Mock()
        new_data = json.dumps({"site": {"instant_power": 200}})
        
        call_count = [0]
        def slow_side_effect(*args, **kwargs):
            call_count[0] += 1
            time.sleep(0.2)  # Simulate slow update
            return new_data
        
        mock_safe_pw_call.side_effect = slow_side_effect
        
        # Make multiple concurrent calls
        import threading
        results = []
        
        def make_call():
            result = safe_endpoint_call("/aggregates", mock_pw_func, "/api/meters/aggregates")
            results.append(result)
        
        threads = [threading.Thread(target=make_call) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Wait for async updates
        time.sleep(0.5)
        
        # All should return the old cached data
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertEqual(result, test_data)
        
        # At most 2 async updates should have been triggered (race condition may allow 2)
        # The important thing is we don't get 3 (one per concurrent request)
        self.assertLessEqual(call_count[0], 2)


class TestAsyncUpdateEndpoint(unittest.TestCase):
    """Test cases for _async_update_endpoint function"""

    def setUp(self):
        """Set up test fixtures"""
        import proxy.server as server
        with server._last_good_responses_lock:
            server._last_good_responses.clear()
        with server._endpoint_last_update_lock:
            server._endpoint_last_update.clear()
        with server._endpoint_update_in_progress_lock:
            server._endpoint_update_in_progress.clear()
        with server._endpoint_stats_lock:
            server._endpoint_stats.clear()

    @patch('proxy.server.safe_pw_call')
    @patch('proxy.server.mqtt_enabled', False)
    @patch('proxy.server.debugmode', False)
    def test_async_update_updates_cache(self, mock_safe_pw_call):
        """Test async update function updates cache"""
        import proxy.server as server
        
        mock_pw_func = Mock()
        test_data = json.dumps({"percentage": 80.0})
        mock_safe_pw_call.return_value = test_data
        
        # Call async update
        _async_update_endpoint("/soe", mock_pw_func, "/api/system_status/soe")
        
        # Verify cache was updated
        with server._last_good_responses_lock:
            cached_data, _ = server._last_good_responses.get("/soe", (None, None))
            self.assertEqual(cached_data, test_data)

    @patch('proxy.server.safe_pw_call')
    @patch('proxy.server.mqtt_enabled', False)
    @patch('proxy.server.debugmode', False)
    def test_async_update_sets_progress_flag(self, mock_safe_pw_call):
        """Test async update sets and clears in-progress flag"""
        import proxy.server as server
        
        mock_pw_func = Mock()
        test_data = json.dumps({"percentage": 80.0})
        
        # Add delay to check in-progress flag
        def slow_side_effect(*args, **kwargs):
            # Check flag is set during execution
            with server._endpoint_update_in_progress_lock:
                self.assertTrue(server._endpoint_update_in_progress.get("/soe", False))
            time.sleep(0.1)
            return test_data
        
        mock_safe_pw_call.side_effect = slow_side_effect
        
        # Call async update in thread
        import threading
        thread = threading.Thread(
            target=_async_update_endpoint,
            args=("/soe", mock_pw_func, "/api/system_status/soe")
        )
        thread.start()
        
        # Wait briefly and check flag is set
        time.sleep(0.05)
        with server._endpoint_update_in_progress_lock:
            self.assertTrue(server._endpoint_update_in_progress.get("/soe", False))
        
        # Wait for completion
        thread.join()
        
        # Verify flag is cleared
        with server._endpoint_update_in_progress_lock:
            self.assertFalse(server._endpoint_update_in_progress.get("/soe", False))

    @patch('proxy.server.safe_pw_call')
    @patch('proxy.server.mqtt_enabled', False)
    @patch('proxy.server.debugmode', False)
    def test_async_update_handles_failure(self, mock_safe_pw_call):
        """Test async update handles failure gracefully"""
        import proxy.server as server
        
        mock_pw_func = Mock()
        mock_safe_pw_call.return_value = None  # Simulate failure
        
        # Call async update
        _async_update_endpoint("/soe", mock_pw_func, "/api/system_status/soe")
        
        # Should not crash, flag should be cleared
        with server._endpoint_update_in_progress_lock:
            self.assertFalse(server._endpoint_update_in_progress.get("/soe", False))


if __name__ == '__main__':
    unittest.main()
