from api.app import db
from database.models import User
from database.enums import Role
from tests.base_test_case import BaseTestCase


class UserTests(BaseTestCase):

    def create_user(self, email='testuser@example.com', role=Role.VIEWER):
        """Creates and saves a user to the database."""
        user = User(email=email, role=role)
        db.session.add(user)
        db.session.commit()
        return user

    def test_invite_user(self):
        """Test inviting a new user."""
        data = {
            'email': 'newuser@example.com',
            'role': Role.VIEWER.name
        }
        rv = self.client.post('/api/v1/users', json=data, headers=self.headers)
        assert rv.status_code == 201
        assert 'email' in rv.json and rv.json['email'] == 'newuser@example.com'

    def test_invite_existing_user(self):
        """Test inviting an existing user."""
        self.create_user(email='existing@example.com')
        data = {
            'email': 'existing@example.com',
            'role': Role.VIEWER.name
        }
        rv = self.client.post('/api/v1/users', json=data, headers=self.headers)
        assert rv.status_code == 400
        assert 'Bad Request' in rv.json['message']

    def test_delete_user(self):
        """Test deleting a user."""
        user = self.create_user()
        rv = self.client.delete(f'/api/v1/users/{user.id}', headers=self.headers)
        assert rv.status_code == 204

        rv = self.client.get(f'/api/v1/users/{user.id}', headers=self.headers)
        assert rv.status_code == 404

    def test_edit_user(self):
        """Test editing a user."""
        user = self.create_user()
        data = {'role': Role.ADMIN.name}
        rv = self.client.put(f'/api/v1/users/{user.id}', json=data, headers=self.headers)
        assert rv.status_code == 200
        assert 'role' in rv.json and rv.json['role'] == Role.ADMIN.name

    def test_get_all_users(self):
        """Test retrieving all users."""
        self.create_user()
        access_token = self.user.generate_auth_token().access_token_jwt
        headers = {'Authorization': f'Bearer {access_token}'}
        rv = self.client.get('/api/v1/users', headers=self.headers)
        assert rv.status_code == 200
        assert isinstance(rv.json, list)

    def test_get_user_by_id(self):
        """Test retrieving a user by id."""
        user = self.create_user()
        rv = self.client.get(f'/api/v1/users/{user.id}', headers=self.headers)
        assert rv.status_code == 200
        assert 'email' in rv.json and rv.json['email'] == user.email

    def test_get_authenticated_user(self):
        """Test retrieving the authenticated user."""
        rv = self.client.get('/api/v1/me', headers=self.headers)
        assert rv.status_code == 200
        assert 'email' in rv.json and rv.json['email'] == self.user.email
