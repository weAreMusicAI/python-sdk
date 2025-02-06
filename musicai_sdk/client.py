import time
import requests
import os
import json
from requests.exceptions import HTTPError
from urllib.parse import urlencode
from .utils import extract_file_extension_from_url, extract_name_from_url


class MusicAiClient:
    def __init__(self, api_key, job_monitor_interval=2, save_output_to_folder=True):
        self.api_key = api_key
        self.base_url = "https://api.music.ai/api"
        self.job_monitor_interval = job_monitor_interval
        self.save_output_to_folder = save_output_to_folder

    def get_headers(self):
        return {"Authorization": self.api_key}

    def upload_file(self, file_path):
        response = requests.get(f"{self.base_url}/upload", headers=self.get_headers())
        if response.status_code // 100 != 2:
            raise HTTPError(
                f"Error uploading file: {response.status_code} {response.text}"
            )
        upload_url = response.json()["uploadUrl"]
        with open(file_path, "rb") as file:
            put_response = requests.put(upload_url, data=file.read())
            if put_response.status_code // 100 != 2:
                raise HTTPError(
                    f"Error uploading file to provided URL: {put_response.status_code} {put_response.text}"
                )
        return response.json()["downloadUrl"]

    def get_job(self, job_id):
        response = requests.get(
            f"{self.base_url}/job/{job_id}", headers=self.get_headers()
        )
        if response.status_code // 100 != 2:
            raise HTTPError(
                f"Error getting job: {response.status_code} {response.text}"
            )
        return response.json()

    def get_job_status(self, job_id):
        response = requests.get(
            f"{self.base_url}/job/{job_id}/status", headers=self.get_headers()
        )
        if response.status_code // 100 != 2:
            raise HTTPError(
                f"Error getting job: {response.status_code} {response.text}"
            )
        return response.json()

    def list_jobs(self, filters=None):
        params = {}

        if filters:
            for key, values in filters.items():
                if isinstance(values, (list, tuple)):
                    params.update({key: value for value in values})
                else:
                    params[key] = values

        query_string = urlencode(params)
        url = (
            f"{self.base_url}/job?{query_string}"
            if query_string
            else f"{self.base_url}/job"
        )
        response = requests.get(url, headers=self.get_headers())

        if response.status_code // 100 != 2:
            raise HTTPError(
                f"Error getting jobs: {response.status_code} {response.text}"
            )

        return response.json()

    def add_job(self, job_name, workflow_slug, params):
        data = {"name": job_name, "workflow": workflow_slug, "params": params}
        response = requests.post(
            f"{self.base_url}/job", headers=self.get_headers(), json=data
        )
        if response.status_code // 100 != 2:
            raise HTTPError(
                f"Error creating job: {response.status_code} {response.text}"
            )
        return response.json()

    def delete_job(self, job_id):
        response = requests.delete(
            f"{self.base_url}/job/{job_id}", headers=self.get_headers()
        )
        if response.status_code // 100 != 2:
            raise HTTPError(
                f"Error deleting job: {response.status_code} {response.text}"
            )
        return response.json()

    def list_workflows(self, filters=None):
        params = {}

        if filters:
            for key, values in filters.items():
                if isinstance(values, (list, tuple)):
                    params.update({key: value for value in values})
                else:
                    params[key] = values

        query_string = urlencode(params)
        url = (
            f"{self.base_url}/workflow?{query_string}"
            if query_string
            else f"{self.base_url}/workflow"
        )
        print("url=", url)
        response = requests.get(url, headers=self.get_headers())

        if response.status_code // 100 != 2:
            raise HTTPError(
                f"Error getting workflows: {response.status_code} {response.text}"
            )

        return response.json()

    def wait_for_job_completion(self, id):
        while True:
            job = self.get_job_status(id)
            if job["status"] in ["SUCCEEDED", "FAILED"]:
                return self.get_job(id)
            time.sleep(self.job_monitor_interval),

    def get_application_info(self):
        response = requests.get(
            f"{self.base_url}/application", headers=self.get_headers()
        )
        if response.status_code // 100 != 2:
            raise HTTPError(
                f"Error getting application info: {response.status_code} {response.text}"
            )
        return response.json()

    def download_job_results(self, job_id_or_job_data, output_dir):
        job = (
            self.get_job(job_id_or_job_data)
            if isinstance(job_id_or_job_data, str)
            else job_id_or_job_data
        )

        if job["status"] in ["QUEUED", "STARTED"]:
            raise HTTPError(
                f"Can't download job results: Job '{job['id']}' is not completed"
            )
        if job["status"] == "FAILED":
            raise HTTPError(f"Can't download job results: Job '{job['id']}' failed")

        download_result = {}
        result_json_downloads = {}

        for result, value in job["result"].items():
            if value.startswith("https://"):
                file_name = (
                    f"{result}.{extract_file_extension_from_url(value)}"
                    if self.save_output_to_folder
                    else extract_name_from_url(value)
                )
                download_destination = os.path.join(output_dir, file_name)
                self.download_file(value, download_destination)
                download_result[result] = download_destination
                result_json_downloads[result] = f"./{file_name}"

        result_json = json.dumps({**job["result"], **result_json_downloads})
        with open(os.path.join(output_dir, "workflow.result.json"), "w") as file:
            file.write(result_json)

        return download_result

    def download_file(self, url, file_destination):
        os.makedirs(os.path.dirname(file_destination), exist_ok=True)
        response = requests.get(url)
        if response.status_code // 100 != 2:
            raise HTTPError(
                f"Error downloading file: {response.status_code} {response.text}"
            )
        with open(file_destination, "wb") as file:
            file.write(response.content)
