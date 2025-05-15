import os
import re
import shutil
import tempfile
import uuid
import requests

import pytest

from musicai_sdk.client import MusicAiClient

UUID_REGEX = r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'


class TestMusicAiClient:
    
    @pytest.fixture
    def client(self):
        # Get API key and host from environment variables
        api_key = os.environ.get("MUSIC_AI_TEST_API_KEY")
        host = os.environ.get("MUSIC_AI_TEST_HOST")
        
        if not api_key:
            pytest.skip("MUSIC_AI_TEST_API_KEY environment variable not set")
            
        # Create client with custom host if provided
        client = MusicAiClient(api_key)
        if host:
            # Use the host directly, expecting it to include https://
            client.base_url = f"{host}/api"
            print(f"Using base URL: {client.base_url}")
        
        return client
    
    @pytest.fixture
    def temp_dir(self):
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp(prefix="sdk-test-")
        yield temp_dir
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)
    
    def test_upload_file(self, client):
        """Test uploading a file"""
        # Act
        download_url = client.upload_file("./tests/data/demo.ogg")
        
        # Assert
        assert re.match(r'^https://storage\.googleapis\.com/moises-.+/', download_url)
    
    def test_download_file(self, client, temp_dir):
        """Test downloading a file"""
        # Arrange
        tmp_file = os.path.join(temp_dir, str(uuid.uuid4()))
        
        # Act
        client.download_file("https://music.ai/demo.ogg", tmp_file)
        
        # Assert
        assert os.path.exists(tmp_file)
    
    def test_add_job(self, client):
        """Test adding a job"""
        # Act
        result = client.add_job("sdk-test", "sdk-test", {
            "file": "https://music.ai/demo.ogg"
        })
        
        # Assert
        assert isinstance(result, dict)
        job_id = result.get("id")
        assert job_id is not None
        assert re.match(UUID_REGEX, job_id)
    
    def test_add_job_with_custom_storage(self, client):
        """Test adding a job with custom storage"""
        # Arrange
        upload_response = requests.get(f"{client.base_url}/upload", headers=client.get_headers())
        upload_response.raise_for_status()
        upload_url = upload_response.json()["uploadUrl"]
        
        # Act
        result = client.add_job(
            "sdk-test-custom-storage",
            "sdk-test",
            {
                "file": "https://music.ai/demo.ogg",
            },
            copy_results_to={
                "file": upload_url
            }
        )
        
        # Assert
        assert isinstance(result, dict)
        job_id = result.get("id")
        assert job_id is not None
        assert re.match(UUID_REGEX, job_id)
        
        # Additional verification for custom storage
        completed_job = client.wait_for_job_completion(job_id)
        assert completed_job["status"] == "SUCCEEDED"
        assert "result" in completed_job
        assert "file" in completed_job["result"]
        assert completed_job["result"]["file"] == "[custom storage]"
    
    def test_get_job(self, client):
        """Test getting job details"""
        # Arrange
        result = client.add_job("sdk-test", "sdk-test", {
            "file": "https://music.ai/demo.ogg"
        })
        job_id = result.get("id")
        
        # Act
        job = client.get_job(job_id)
        
        # Assert
        assert isinstance(job, dict)
        assert job["id"] == job_id
        assert job["name"] == "sdk-test"
        assert job["workflow"] == "sdk-test"
        assert job["workflowParams"]["file"] == "https://music.ai/demo.ogg"
    
    def test_get_job_status(self, client):
        """Test getting job status"""
        # Arrange
        result = client.add_job("sdk-test", "sdk-test", {
            "file": "https://music.ai/demo.ogg"
        })
        job_id = result.get("id")
        
        # Act
        job_status = client.get_job_status(job_id)
        
        # Assert
        assert isinstance(job_status, dict)
        assert job_status["id"] == job_id
        assert job_status["status"] in ["QUEUED", "STARTED", "SUCCEEDED", "FAILED"]
    
    def test_wait_for_job_completion(self, client):
        """Test waiting for job completion"""
        # Arrange
        result = client.add_job("sdk-test", "sdk-test", {
            "file": "https://music.ai/demo.ogg"
        })
        job_id = result.get("id")
        
        # Act
        job = client.wait_for_job_completion(job_id)
        
        # Assert
        assert isinstance(job, dict)
        assert job["id"] == job_id
        assert job["status"] == "SUCCEEDED"
    
    def test_download_job_results(self, client, temp_dir):
        """Test downloading job results"""
        # Arrange
        result = client.add_job("sdk-test", "sdk-test", {
            "file": "https://music.ai/demo.ogg"
        })
        job_id = result.get("id")
        client.wait_for_job_completion(job_id)
        
        # Act
        job_results = client.download_job_results(job_id, temp_dir)
        
        # Assert
        assert isinstance(job_results, dict)
        assert "file" in job_results
        assert os.path.exists(job_results["file"])
    
    def test_list_jobs(self, client):
        """Test listing jobs"""
        # Act
        response = client.list_jobs()
        
        # Assert
        assert isinstance(response, list) or (isinstance(response, dict) and "jobs" in response)
        job_list = response if isinstance(response, list) else response.get("jobs", [])
        assert len(job_list) > 0
    
    def test_list_jobs_with_filter(self, client):
        """Test listing jobs with filter"""
        # Act
        filled_response = client.list_jobs({"workflow": ["sdk-test"]})
        empty_response = client.list_jobs({"workflow": [str(uuid.uuid4())]})
        
        # Assert
        filled_jobs = filled_response if isinstance(filled_response, list) else filled_response.get("jobs", [])
        empty_jobs = empty_response if isinstance(empty_response, list) else empty_response.get("jobs", [])
        assert len(filled_jobs) > 0
        assert len(empty_jobs) == 0
    
    def test_delete_job(self, client):
        """Test deleting a job"""
        # Arrange
        result = client.add_job("sdk-test", "sdk-test", {
            "file": "https://music.ai/demo.ogg"
        })
        job_id = result.get("id")
        
        # Act
        client.delete_job(job_id)
        
        # Assert
        with pytest.raises(Exception):
            client.get_job(job_id)
    
    def test_list_workflows(self, client):
        """Test listing available workflows"""
        # Act
        result = client.list_workflows()
        
        # Verify the result has expected structure
        assert isinstance(result, dict)
        assert "workflows" in result
        
        # Check the workflows list
        workflows = result["workflows"]
        assert isinstance(workflows, list)
        
        # Verify a specific workflow exists
        assert any(w.get("slug") == "sdk-test" for w in workflows)
    
    def test_list_workflows_with_filter(self, client):
        """Test listing workflows with filter"""
        # Act
        empty_workflow_list = client.list_workflows({"page": 999})
        
        # Assert
        assert len(empty_workflow_list["workflows"]) == 0
    
    def test_get_application_info(self, client):
        """Test getting application info"""
        # Act
        result = client.get_application_info()
        
        # Verify the result has expected structure
        assert isinstance(result, dict)
        assert "id" in result
        assert re.match(UUID_REGEX, result["id"])
        assert "name" in result 
