from datetime import datetime, timedelta
from tests.base_test_case import BaseTestCase
from unittest import mock


class AuthenticationTestCase(BaseTestCase):

    def test_no_auth(self):
        rv = self.client.get('http://localhost:5001/api/users')
        self.assertTrue(rv.status_code == 401)

    def test_get_token(self):
        rv = self.client.post('/api/tokens', auth=(self.username, self.password))
        self.assertTrue(rv.status_code == 200)
        access_token = rv.json['access_token']
        refresh_token = rv.json['refresh_token']

        rv = self.client.get('/api/users', headers={
            'Authorization': f'Bearer {access_token}'})
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(rv.json['data'][0]['username'] == self.username)

        rv = self.client.get('/api/users', headers={
            'Authorization': f'Bearer {access_token + "x"}'})
        self.assertTrue(rv.status_code == 401)

        rv = self.client.get('/api/users', headers={
            'Authorization': f'Bearer {refresh_token}'})
        self.assertTrue(rv.status_code == 401)

    def test_get_token_in_cookie_only(self):
        self.app.config['REFRESH_TOKEN_IN_BODY'] = False
        self.app.config['REFRESH_TOKEN_IN_COOKIE'] = True
        rv = self.client.post('/api/tokens', auth=(self.username, self.password))
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(rv.json['refresh_token'] is None)
        self.assertTrue(rv.headers['Set-Cookie'].startswith('refresh_token='))

    def test_get_token_in_body_only(self):
        rv = self.client.post('/api/tokens', auth=(self.username, self.password))
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(rv.json['refresh_token'] is not None)
        self.assertTrue('Set-Cookie' not in rv.headers)

    def test_token_expired(self):
        rv = self.client.post('/api/tokens', auth=(self.username, self.password))
        self.assertTrue(rv.status_code == 200)
        access_token = rv.json['access_token']

        with mock.patch('api.models.datetime') as dt:
            dt.utcnow.return_value = datetime.utcnow() + timedelta(days=1)
            rv = self.client.get('/api/users', headers={
                'Authorization': f'Bearer {access_token}'})
            self.assertTrue(rv.status_code == 401)

    def test_refresh_token(self):
        rv = self.client.post('/api/tokens', auth=(self.email, self.password))
        self.assertTrue(rv.status_code == 200)
        access_token1 = rv.json['access_token']
        refresh_token1 = rv.json['refresh_token']

        self.client.set_cookie('localhost', 'refresh_token', refresh_token1)
        rv = self.client.put('/api/tokens', json={'access_token': access_token1})
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(rv.json['access_token'] != access_token1)
        self.assertTrue(rv.json['refresh_token'] != refresh_token1)
        access_token2 = rv.json['access_token']

        rv = self.client.get('/api/users', headers={
            'Authorization': f'Bearer {access_token2}'})
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(rv.json['data'][0]['username'] == self.username)

        rv = self.client.get('/api/users', headers={
            'Authorization': f'Bearer {access_token1}'})
        self.assertTrue(rv.status_code == 401)

    def test_refresh_token_failure(self):
        rv = self.client.post('/api/tokens', auth=(self.username, self.password))
        self.assertTrue(rv.status_code == 200)
        access_token = rv.json['access_token']
        refresh_token = rv.json['refresh_token']

        self.client.cookie_jar.clear()
        rv = self.client.put('/api/tokens', json={
            'access_token': access_token})
        self.assertTrue(rv.status_code == 401)
        rv = self.client.put('/api/tokens', json={
            'access_token': access_token,
            'refresh_token': refresh_token + 'x',
        })
        rv = self.client.put('/api/tokens', json={
            'access_token': access_token + 'x',
            'refresh_token': refresh_token,
        })
        self.assertTrue(rv.status_code == 401)

    def test_refresh_revoke_all(self):
        rv = self.client.post('/api/tokens', auth=(self.username, self.password))
        self.assertTrue(rv.status_code == 200)
        access_token1 = rv.json['access_token']
        refresh_token1 = rv.json['refresh_token']

        rv = self.client.get('/api/users', headers={
            'Authorization': f'Bearer {access_token1}'})
        self.assertTrue(rv.status_code == 200)

        rv = self.client.post('/api/tokens', auth=(self.username, self.password))
        self.assertTrue(rv.status_code == 200)
        access_token2 = rv.json['access_token']
        refresh_token2 = rv.json['refresh_token']

        rv = self.client.put('/api/tokens', json={
            'access_token': access_token2, 'refresh_token': refresh_token2})
        self.assertTrue(rv.status_code == 200)
        access_token3 = rv.json['access_token']
        refresh_token3 = rv.json['refresh_token']

        rv = self.client.put('/api/tokens', json={
            'access_token': access_token2,
            'refresh_token': refresh_token2})
        self.assertTrue(rv.status_code == 401)  # duplicate refresh

        rv = self.client.get('/api/users', headers={
            'Authorization': f'Bearer {access_token1}'})
        self.assertTrue(rv.status_code == 401)
        rv = self.client.get('/api/users', headers={
            'Authorization': f'Bearer {access_token2}'})
        self.assertTrue(rv.status_code == 401)
        rv = self.client.get('/api/users', headers={
            'Authorization': f'Bearer {access_token3}'})
        self.assertTrue(rv.status_code == 401)

        rv = self.client.put('/api/tokens', json={
            'access_token': access_token1,
            'refresh_token': refresh_token1})
        self.assertTrue(rv.status_code == 401)
        rv = self.client.put('/api/tokens', json={
            'access_token': access_token2,
            'refresh_token': refresh_token2})
        self.assertTrue(rv.status_code == 401)
        rv = self.client.put('/api/tokens', json={
            'access_token': access_token3,
            'refresh_token': refresh_token3})
        self.assertTrue(rv.status_code == 401)

    def test_revoke(self):
        rv = self.client.post('/api/tokens', auth=(self.username, self.password))
        self.assertTrue(rv.status_code == 200)
        access_token = rv.json['access_token']

        rv = self.client.get('/api/users', headers={
            'Authorization': f'Bearer {access_token}'})
        self.assertTrue(rv.status_code == 200)

        rv = self.client.delete('/api/tokens', headers={
            'Authorization': f'Bearer {access_token}'})
        self.assertTrue(rv.status_code == 204)

        rv = self.client.get('/api/users', headers={
            'Authorization': f'Bearer {access_token}'})
        self.assertTrue(rv.status_code == 401)

    def test_no_login(self):
        rv = self.client.post('/api/tokens')
        self.assertTrue(rv.status_code == 401)

    def test_bad_login(self):
        rv = self.client.post('/api/tokens', auth=(self.username, 'bar'))
        self.assertTrue(rv.status_code == 401)

    def test_reset_password(self):
        with mock.patch('api.tokens.send_email') as send_email:
            rv = self.client.post('/api/tokens/reset', json={
                'email': 'bad@example.com',
            })
            self.assertTrue(rv.status_code == 204)
            rv = self.client.post('/api/tokens/reset', json={
                'email': self.email,
            })
            self.assertTrue(rv.status_code == 204)
        send_email.assert_called_once()
        self.assertTrue(send_email.call_args[0] == (
            self.email, 'Reset Your Password', 'reset'))
        reset_token = send_email.call_args[1]['token']
        reset_url = send_email.call_args[1]['url']

        rv = self.client.put('/api/tokens/reset', json={
            'token': reset_token + 'x',
            'new_password': 'new_password',
        })
        self.assertTrue(rv.status_code == 400)

        rv = self.client.put('/api/tokens/reset', json={
            'token': reset_token,
            'new_password': 'new_password',
        })
        self.assertTrue(rv.status_code == 204)

        rv = self.client.post('/api/tokens', auth=(self.username, self.password))
        self.assertTrue(rv.status_code == 401)

        rv = self.client.post('/api/tokens', auth=(self.username, 'new_password'))
        self.assertTrue(rv.status_code == 200)

        rv = self.client.get(f'/api/tokens/confirm/{reset_token}')
        self.assertTrue(rv.status_code == 400)