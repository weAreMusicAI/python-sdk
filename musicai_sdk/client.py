import json
import os
import time
from urllib.parse import urlencode

import requests
from requests.exceptions import HTTPError

from .utils import (
    extract_file_extension_from_url,
    extract_name_from_url,
    get_user_agent,
)

# Sentinel used to distinguish "no per-call timeout given" (fall back to the
# instance default) from an explicit `timeout=None` (disable the timeout).
class _Unset:
    def __repr__(self):
        return "UNSET"


_UNSET = _Unset()


class MusicAiClient:
    def __init__(
        self,
        api_key,
        job_monitor_interval=2,
        save_output_to_folder=True,
        user_agent=None,
        timeout=None,
    ):
        self.api_key = api_key
        self.base_url = "https://api.music.ai/v1"
        self.job_monitor_interval = job_monitor_interval
        self.save_output_to_folder = save_output_to_folder
        self.user_agent = user_agent or get_user_agent()
        self.timeout = timeout

    def get_headers(self):
        return {
            "Authorization": self.api_key,
            "User-Agent": self.user_agent,
        }

    def _request(self, method, url, timeout=_UNSET, **kwargs):
        resolved_timeout = self.timeout if timeout is _UNSET else timeout
        return requests.request(method, url, timeout=resolved_timeout, **kwargs)

    def upload_file(self, file_path, timeout=_UNSET):
        response = self._request(
            "get",
            f"{self.base_url}/upload",
            headers=self.get_headers(),
            timeout=timeout,
        )
        if response.status_code // 100 != 2:
            raise HTTPError(
                f"Error uploading file: {response.status_code} {response.text}"
            )
        upload_url = response.json()["uploadUrl"]
        with open(file_path, "rb") as file:
            put_response = self._request(
                "put", upload_url, data=file.read(), timeout=timeout
            )
            if put_response.status_code // 100 != 2:
                raise HTTPError(
                    f"Error uploading file to provided URL: {put_response.status_code} {put_response.text}"
                )
        return response.json()["downloadUrl"]

    def get_job(self, job_id, timeout=_UNSET):
        response = self._request(
            "get",
            f"{self.base_url}/job/{job_id}",
            headers=self.get_headers(),
            timeout=timeout,
        )
        if response.status_code // 100 != 2:
            raise HTTPError(
                f"Error getting job: {response.status_code} {response.text}"
            )
        return response.json()

    def get_job_status(self, job_id, timeout=_UNSET):
        response = self._request(
            "get",
            f"{self.base_url}/job/{job_id}/status",
            headers=self.get_headers(),
            timeout=timeout,
        )
        if response.status_code // 100 != 2:
            raise HTTPError(
                f"Error getting job: {response.status_code} {response.text}"
            )
        return response.json()

    def list_jobs(self, filters=None, timeout=_UNSET):
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
        response = self._request(
            "get", url, headers=self.get_headers(), timeout=timeout
        )

        if response.status_code // 100 != 2:
            raise HTTPError(
                f"Error getting jobs: {response.status_code} {response.text}"
            )

        return response.json()

    def add_job(self, job_name, workflow_slug, params, timeout=_UNSET, **options):
        data = {
            "name": job_name,
            "workflow": workflow_slug,
            "params": params,
        }

        if "metadata" in options:
            data["metadata"] = options["metadata"]

        if "copy_results_to" in options:
            data["copyResultsTo"] = options["copy_results_to"]

        response = self._request(
            "post",
            f"{self.base_url}/job",
            headers=self.get_headers(),
            json=data,
            timeout=timeout,
        )
        if response.status_code // 100 != 2:
            raise HTTPError(
                f"Error creating job: {response.status_code} {response.text}"
            )
        return response.json()

    def delete_job(self, job_id, timeout=_UNSET):
        response = self._request(
            "delete",
            f"{self.base_url}/job/{job_id}",
            headers=self.get_headers(),
            timeout=timeout,
        )
        if response.status_code // 100 != 2:
            raise HTTPError(
                f"Error deleting job: {response.status_code} {response.text}"
            )
        return response.json()

    def list_workflows(self, filters=None, timeout=_UNSET):
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
        response = self._request(
            "get", url, headers=self.get_headers(), timeout=timeout
        )

        if response.status_code // 100 != 2:
            raise HTTPError(
                f"Error getting workflows: {response.status_code} {response.text}"
            )

        return response.json()

    def wait_for_job_completion(self, id, timeout=_UNSET):
        while True:
            job = self.get_job_status(id, timeout=timeout)
            if job["status"] in ["SUCCEEDED", "FAILED"]:
                return self.get_job(id, timeout=timeout)
            time.sleep(self.job_monitor_interval),

    def get_application_info(self, timeout=_UNSET):
        response = self._request(
            "get",
            f"{self.base_url}/application",
            headers=self.get_headers(),
            timeout=timeout,
        )
        if response.status_code // 100 != 2:
            raise HTTPError(
                f"Error getting application info: {response.status_code} {response.text}"
            )
        return response.json()

    def download_job_results(self, job_id_or_job_data, output_dir, timeout=_UNSET):
        job = (
            self.get_job(job_id_or_job_data, timeout=timeout)
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
            if isinstance(value, str) and value.startswith("https://"):
                file_name = (
                    f"{result}.{extract_file_extension_from_url(value)}"
                    if self.save_output_to_folder
                    else extract_name_from_url(value)
                )
                download_destination = os.path.join(output_dir, file_name)
                self.download_file(value, download_destination, timeout=timeout)
                download_result[result] = download_destination
                result_json_downloads[result] = f"./{file_name}"

        result_json = json.dumps({**job["result"], **result_json_downloads})
        with open(os.path.join(output_dir, "workflow.result.json"), "w") as file:
            file.write(result_json)

        return download_result

    def download_file(self, url, file_destination, timeout=_UNSET):
        os.makedirs(os.path.dirname(file_destination), exist_ok=True)
        response = self._request("get", url, timeout=timeout)
        if response.status_code // 100 != 2:
            raise HTTPError(
                f"Error downloading file: {response.status_code} {response.text}"
            )
        with open(file_destination, "wb") as file:
            file.write(response.content)
