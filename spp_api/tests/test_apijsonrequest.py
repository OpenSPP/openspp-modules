from unittest.mock import Mock

from werkzeug.exceptions import NotFound

from odoo.tests.common import TransactionCase

from ..controllers.apijsonrequest import (
    ApiJsonRequest,
    SessionExpiredException,
    serialize_exception,
)


class TestApiJsonRequest(TransactionCase):
    def setUp(self):
        super().setUp()
        # Add any setup code here that should run before each test

    def test_serialize_exception(self):
        # Test basic exception
        exc = ValueError("test error")
        result = serialize_exception(exc)
        self.assertEqual(result["name"], "builtins.ValueError")
        self.assertEqual(result["message"], "test error")
        self.assertEqual(result["arguments"], ("test error",))
        self.assertEqual(result["context"], {})
        # Debug info might not be available in test environment
        self.assertIsNotNone(result["debug"])

        # Test exception with context
        exc = ValueError("test error")
        exc.context = {"additional": "info"}
        result = serialize_exception(exc)
        self.assertEqual(result["context"], {"additional": "info"})

    def test_api_json_request_dispatch(self):
        # Mock request object
        mock_request = Mock()
        mock_request.params = {}
        mock_request.get_http_params.return_value = {"param1": "value1"}
        mock_request.db = self.env.cr.dbname  # Use actual test database name

        # Setup registry mock with dict-like behavior
        mock_http = Mock()
        mock_registry = {"ir.http": mock_http}
        mock_request.registry = mock_registry

        # Mock endpoint
        mock_endpoint = Mock()
        mock_endpoint.return_value.json = {"result": "success"}
        mock_endpoint.return_value.status = 200

        # Create ApiJsonRequest instance
        api_request = ApiJsonRequest(mock_request)

        # Test dispatch with database
        api_request.dispatch(mock_endpoint, {"arg1": "value1"})

        # Verify calls
        self.assertEqual(mock_request.params, {"arg1": "value1", "param1": "value1"})
        mock_http._dispatch.assert_called_once_with(mock_endpoint)

    def test_handle_error(self):
        # Mock request object
        mock_request = Mock()
        mock_request.make_json_response = Mock()
        api_request = ApiJsonRequest(mock_request)

        # Test regular exception
        exc = ValueError("test error")
        api_request.handle_error(exc)
        mock_request.make_json_response.assert_called_with(
            {
                "code": 200,
                "message": "Odoo Server Error",
                "data": serialize_exception(exc),
            }
        )

        # Test NotFound exception
        exc = NotFound()
        api_request.handle_error(exc)
        mock_request.make_json_response.assert_called_with(
            {
                "code": 404,
                "message": "404: Not Found",
                "data": serialize_exception(exc),
            }
        )

        # Test SessionExpiredException
        exc = SessionExpiredException()
        api_request.handle_error(exc)
        mock_request.make_json_response.assert_called_with(
            {
                "code": 100,
                "message": "Odoo Session Expired",
                "data": serialize_exception(exc),
            }
        )

    def test_is_compatible_with(self):
        self.assertTrue(ApiJsonRequest.is_compatible_with(None))
