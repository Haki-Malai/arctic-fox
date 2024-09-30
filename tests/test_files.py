from api import db
from database.models import File, Folder
from tests.base_test_case import BaseTestCase


class FileTests(BaseTestCase):

    def create_folder(self):
        """Initializes a folder and saves it to the database."""
        folder = Folder(name='testfolder',
                        description='This is a test folder',
                        created_by=self.user.id)
        db.session.add(folder)
        db.session.commit()
        return folder

    def create_file(self):
        """Initializes a file and saves it to the database."""
        folder = self.create_folder()
        file = File(filename='testfile.png',
                    mimetype='image/png',
                    description='This is a test file',
                    created_by=self.user.id,
                    folder_id=folder.id)
        db.session.add(file)
        db.session.commit()
        return file

    def test_new_file(self):
        """Test creating a new file."""
        folder = self.create_folder()
        data = {
            'filename': 'testfile.png',
            'mimetype': 'image/png',
            'description': 'This is a test file',
            'folder_id': folder.id
        }
        rv = self.client.post('/api/v1/files', json=data, headers=self.headers)
        assert rv.status_code == 201
        assert 'filename' in rv.json and rv.json['filename'] == 'testfile.png'
        file_id = rv.json['id']

        rv = self.client.get(f'/api/v1/files/{file_id}', headers=self.headers)
        assert rv.status_code == 200
        assert 'description' in rv.json and rv.json['description'] == 'This is a test file'
        assert 'preview_url' in rv.json
        assert 'folder' in rv.json and rv.json['folder']['id'] == folder.id

    def test_delete_file(self):
        """Test deleting a file."""
        file = self.create_file()
        db.session.add(file)
        db.session.commit()

        rv = self.client.delete(f'/api/v1/files/{file.id}', headers=self.headers)
        assert rv.status_code == 204

        rv = self.client.get(f'/api/v1/files/{file.id}', headers=self.headers)
        assert rv.status_code == 404
