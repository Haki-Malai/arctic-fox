from api.app import db
from api.models import User, Folder
from api.enums import Role
from tests.base_test_case import BaseTestCase


class FolderTests(BaseTestCase):

    def test_new_folder(self):
        """Test creating a new folder."""
        data = {
            'name': 'testfolder',
            'description': 'This is a test folder'
        }
        rv = self.client.post('/api/v1/folders', json=data)
        print(rv.json)
        assert rv.status_code == 201
        assert 'name' in rv.json \
            and rv.json['name'] == 'testfolder'
        folder_id = rv.json['id']

        rv = self.client.get(f'/api/v1/folders/{folder_id}')
        assert rv.status_code == 200
        assert 'description' in rv.json \
            and rv.json['description'] == 'This is a test folder'

    def test_edit_folder(self):
        """Test editing a folder."""
        folder = Folder(name='testfolder',
                        description='This is a test folder',
                        created_by=self.user.id)
        db.session.add(folder)
        db.session.commit()

        rv = self.client.put(f'/api/v1/folders/{folder.id}',
                             json={'description': 'Updated test folder description'})
        assert rv.status_code == 200
        assert 'description' in rv.json \
            and rv.json['description'] == 'Updated test folder description'

    def test_delete_folder(self):
        """Test deleting a folder."""
        folder = Folder(name='testfolder',
                        description='This is a test folder',
                        created_by=self.user.id)
        db.session.add(folder)
        db.session.commit()

        rv = self.client.delete(f'/api/v1/folders/{folder.id}')
        assert rv.status_code == 204

        rv = self.client.get(f'/api/v1/folders/{folder.id}')
        assert rv.status_code == 404

    def test_permissions(self):
        """Test folder permissions."""
        folder = Folder(name='testfolder',
                        description='This is a test folder',
                        created_by=self.user.id)
        db.session.add(folder)
        db.session.commit()

        access_token = self.user.generate_auth_token()
        headers = {'Authorization': f'Bearer {access_token}'}

        rv = self.client.put(f'/api/v1/folders/{folder.id}',
                             json={'description': 'Authorized edit attempt'},
                             headers=headers)
        assert rv.status_code == 200, 'Expected successful edit for admin role'

        self.user.role = Role.VIEWER
        self.DISABLE_AUTH = False

        rv = self.client.put(f'/api/v1/folders/{folder.id}',
                             json={'description': 'Unauthorized edit attempt'},
                             headers=headers)
        assert rv.status_code == 403, 'Expected forbidden status for unauthorized edit'


        rv = self.client.get(f'/api/v1/folders/{folder.id}', headers=headers)
        assert rv.status_code == 200 \
            and rv.json['description'] == 'Authorized edit attempt', \
                'Edit should be visible'
