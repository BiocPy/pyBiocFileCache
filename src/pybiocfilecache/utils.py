import tempfile
import uuid

def create_tmp_dir():
    """create a temporary directory

    Returns:
        str: path to the directory
    """        
    return tempfile.mkdtemp()

def generate_id():
    """Generate uuid

    Returns:
        str: unique string for use as id
    """        
    return uuid.uuid4().hex