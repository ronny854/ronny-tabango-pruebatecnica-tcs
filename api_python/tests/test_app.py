import json
import jwt


class TestHealthCheck:
    def test_health_returns_200(self, client):
        response = client.get('/health')
        assert response.status_code == 200

    def test_health_returns_healthy_status(self, client):
        data = response = client.get('/health').get_json()
        assert data['status'] == 'healthy'

    def test_health_contains_service_name(self, client):
        data = client.get('/health').get_json()
        assert data['service'] == 'DevOps Microservice'

    def test_health_contains_timestamp(self, client):
        data = client.get('/health').get_json()
        assert 'timestamp' in data


class TestDevOpsPostValid:
    def test_valid_post_returns_200(self, client, valid_headers, valid_payload):
        response = client.post('/DevOps', headers=valid_headers,
                               data=json.dumps(valid_payload))
        assert response.status_code == 200

    def test_valid_post_returns_message(self, client, valid_headers, valid_payload):
        response = client.post('/DevOps', headers=valid_headers,
                               data=json.dumps(valid_payload))
        data = response.get_json()
        assert data['message'] == 'Hello Juan Perez your message will be send'

    def test_valid_post_returns_jwt_header(self, client, valid_headers, valid_payload):
        response = client.post('/DevOps', headers=valid_headers,
                               data=json.dumps(valid_payload))
        assert 'X-JWT-KWY' in response.headers

    def test_valid_post_jwt_is_decodable(self, client, valid_headers, valid_payload):
        response = client.post('/DevOps', headers=valid_headers,
                               data=json.dumps(valid_payload))
        token = response.headers.get('X-JWT-KWY')
        decoded = jwt.decode(token, 'test-secret-key', algorithms=['HS256'])
        assert 'transaction_id' in decoded
        assert 'timestamp' in decoded

    def test_valid_post_different_recipient(self, client, valid_headers):
        payload = {"to": "Maria Garcia", "message": "test"}
        response = client.post('/DevOps', headers=valid_headers,
                               data=json.dumps(payload))
        data = response.get_json()
        assert 'Maria Garcia' in data['message']

    def test_valid_post_empty_to_field(self, client, valid_headers):
        payload = {"message": "test"}
        response = client.post('/DevOps', headers=valid_headers,
                               data=json.dumps(payload))
        assert response.status_code == 200
        data = response.get_json()
        assert 'Hello' in data['message']

    def test_each_post_generates_unique_jwt(self, client, valid_headers, valid_payload):
        r1 = client.post('/DevOps', headers=valid_headers,
                         data=json.dumps(valid_payload))
        r2 = client.post('/DevOps', headers=valid_headers,
                         data=json.dumps(valid_payload))
        assert r1.headers['X-JWT-KWY'] != r2.headers['X-JWT-KWY']


class TestDevOpsPostInvalidApiKey:
    def test_invalid_api_key_returns_401(self, client, valid_payload):
        headers = {
            'Content-Type': 'application/json',
            'X-Parse-REST-API-Key': 'wrong-api-key'
        }
        response = client.post('/DevOps', headers=headers,
                               data=json.dumps(valid_payload))
        assert response.status_code == 401

    def test_invalid_api_key_returns_error_message(self, client, valid_payload):
        headers = {
            'Content-Type': 'application/json',
            'X-Parse-REST-API-Key': 'wrong-api-key'
        }
        data = client.post('/DevOps', headers=headers,
                           data=json.dumps(valid_payload)).get_json()
        assert 'Unauthorized' in data['error']

    def test_missing_api_key_returns_401(self, client, valid_payload):
        headers = {'Content-Type': 'application/json'}
        response = client.post('/DevOps', headers=headers,
                               data=json.dumps(valid_payload))
        assert response.status_code == 401


class TestDevOpsInvalidMethods:
    def test_get_returns_405(self, client, valid_headers):
        response = client.get('/DevOps', headers=valid_headers)
        assert response.status_code == 405

    def test_get_returns_error_text(self, client, valid_headers):
        response = client.get('/DevOps', headers=valid_headers)
        assert b'ERROR' in response.data

    def test_put_returns_405(self, client, valid_headers):
        response = client.put('/DevOps', headers=valid_headers)
        assert response.status_code == 405

    def test_delete_returns_405(self, client, valid_headers):
        response = client.delete('/DevOps', headers=valid_headers)
        assert response.status_code == 405

    def test_patch_returns_405(self, client, valid_headers):
        response = client.patch('/DevOps', headers=valid_headers)
        assert response.status_code == 405


class TestDevOpsInvalidPayload:
    def test_no_json_body_returns_400(self, client, valid_headers):
        response = client.post('/DevOps', headers=valid_headers)
        assert response.status_code == 400

    def test_no_json_body_returns_error(self, client, valid_headers):
        data = client.post('/DevOps', headers=valid_headers).get_json()
        assert 'error' in data

    def test_empty_content_type_returns_400(self, client, valid_api_key):
        headers = {'X-Parse-REST-API-Key': valid_api_key}
        response = client.post('/DevOps', headers=headers, data='not json')
        assert response.status_code == 400


class TestWebInterface:
    def test_index_returns_200(self, client):
        response = client.get('/')
        assert response.status_code == 200

    def test_index_returns_html(self, client):
        response = client.get('/')
        assert b'<!DOCTYPE html>' in response.data

    def test_index_contains_title(self, client):
        response = client.get('/')
        assert b'DevOps Microservice' in response.data
