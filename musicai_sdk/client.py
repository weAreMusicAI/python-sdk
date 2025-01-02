import time
import requests
from requests.exceptions import HTTPError
from urllib.parse import urlencode

class MusicAiClient:
    def __init__(self, api_key, job_monitor_interval=2):
        self.api_key = api_key
        self.base_url = 'https://api.music.ai/api'
        self.job_monitor_interval = job_monitor_interval

    def get_headers(self):
        return {
            'Authorization': self.api_key
        }

    def upload_file(self, file_path):
        response = requests.get(f'{self.base_url}/upload', headers=self.get_headers())
        if response.status_code // 100 != 2:
            raise HTTPError(f'Error uploading file: {response.status_code} {response.text}')
        upload_url = response.json()['uploadUrl']
        with open(file_path, 'rb') as file:
            put_response = requests.put(upload_url, data=file.read())
            if put_response.status_code // 100 != 2:
                raise HTTPError(f'Error uploading file to provided URL: {put_response.status_code} {put_response.text}')
        return response.json()['downloadUrl']

    def get_job(self, job_id):
        response = requests.get(f'{self.base_url}/job/{job_id}', headers=self.get_headers())
        if response.status_code // 100 != 2:
            raise HTTPError(f'Error getting job: {response.status_code} {response.text}')
        return response.json()
    
    def get_job_status(self, job_id):
        response = requests.get(f'{self.base_url}/job/{job_id}/status', headers=self.get_headers())
        if response.status_code // 100 != 2:
            raise HTTPError(f'Error getting job: {response.status_code} {response.text}')
        return response.json()

    def list_jobs(self, filters=None):
        params = {}

        if filters:
            for key, values in filters.items(): 
                if isinstance(values, (list, tuple)):
                    params.update({ key: value for value in values })
                else:
                    params[key] = values

        query_string = urlencode(params)
        url = f'{self.base_url}/job?{query_string}' if query_string else f'{self.base_url}/job'
        response = requests.get(url, headers=self.get_headers())

        if response.status_code // 100 != 2:
            raise HTTPError(f'Error getting jobs: {response.status_code} {response.text}')
        
        return response.json()

    def add_job(self, job_name, workflow_slug, params):
        data = {
            'name': job_name,
            'workflow': workflow_slug,
            'params': params
        }
        response = requests.post(f'{self.base_url}/job', headers=self.get_headers(), json=data)
        if response.status_code // 100 != 2:
            raise HTTPError(f'Error creating job: {response.status_code} {response.text}')
        return response.json()

    def delete_job(self, job_id):
        response = requests.delete(f'{self.base_url}/job/{job_id}', headers=self.get_headers())
        if response.status_code // 100 != 2:
            raise HTTPError(f'Error deleting job: {response.status_code} {response.text}')
        return response.json()
    
    def list_workflows(self, filters=None):
        params = {}

        if filters:
            for key, values in filters.items(): 
                if isinstance(values, (list, tuple)):
                    params.update({ key: value for value in values })
                else:
                    params[key] = values

        query_string = urlencode(params)
        url = f'{self.base_url}/workflow?{query_string}' if query_string else f'{self.base_url}/workflow'
        response = requests.get(url, headers=self.get_headers())

        if response.status_code // 100 != 2:
            raise HTTPError(f'Error getting workflows: {response.status_code} {response.text}')
        
        return response.json()
    
    def wait_for_job_completion(self, id):
        while True:
            job = self.get_job_status(id)
            if job['status'] in ['SUCCEEDED', 'FAILED']:
                return self.get_job(id)
            time.sleep(self.job_monitor_interval),

    def get_application_info(self):
        response = requests.get(f'{self.base_url}/application', headers=self.get_headers())
        if response.status_code // 100 != 2:
            raise HTTPError(f'Error getting application info: {response.status_code} {response.text}')
        return response.json()
