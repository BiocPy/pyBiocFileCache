import tempfile
import uuid

def create_tmp_dir():
    return tempfile.mkdtemp()

def generate_id():
    return uuid.uuid4().hex