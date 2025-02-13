import requests
import os
import json
from dotenv import load_dotenv

load_dotenv("./config/auth.env")

class JenkinsOperations:
    def __init__(self):
        self.base_url = os.getenv("JENKINS_URL", "http://10.70.46.85:8080/")
        self.auth_user = os.getenv("JENKINS_USER")
        self.auth_token = os.getenv("JENKINS_API_TOKEN")

        if not self.auth_user or not self.auth_token:
            raise ValueError("JENKINS_USER or JENKINS_API_TOKEN not set in environment variables!")
        
        self.auth = (self.auth_user, self.auth_token)

        base_dir = os.path.dirname(os.path.abspath(__file__))  # Gets the directory of the current script
        file_path = os.path.join(base_dir, "config", "endpoints.json")
        with open(file_path, "r") as f:
            self.endpoints = json.load(f)

    def _get_request(self, url):
        """Helper function to perform GET requests with error handling."""
        try:
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def _post_request(self, url, params={}):
        """Helper function to perform POST requests with error handling."""
        try:
            response = requests.post(url, auth=self.auth, params=params)
            response.raise_for_status()
            return {"message": "Request successful"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def get_all_jobs(self, user):
        """List all jobs available for the user."""
        url = f"{self.base_url}{self.endpoints['jobs_endpoint']}"
        data = self._get_request(url)

        if "error" in data:
            return data

        jobs = [job["name"] for job in data.get("jobs", [])]

        # Filter jobs based on user role
        if user["role"] != "admin":
            jobs = [job for job in jobs if not job.lower().startswith("admin")]

        return {"jobs": jobs}

    def trigger_job(self, user, job_name, params={}):
        """Trigger a Jenkins job."""
        if user["role"] != "admin" and job_name.lower().startswith("admin"):
            return {"error": "Access denied"}

        url = f"{self.base_url}{self.endpoints['build_endpoint'].format(job_name=job_name)}"
        return self._post_request(url, params)

    def get_last_build_summary(self, job_name):
        """Retrieve last build summary."""
        url = f"{self.base_url}{self.endpoints['last_build_summary'].format(job_name=job_name)}"
        return self._get_request(url)

    def get_specific_build_summary(self, job_name, build_number):
        """Retrieve a specific build summary."""
        url = f"{self.base_url}{self.endpoints['specific_build_summary'].format(job_name=job_name, build_number=build_number)}"
        return self._get_request(url)

    def get_job_health(self, job_name):
        """Get job health information."""
        url = f"{self.base_url}{self.endpoints['job_health'].format(job_name=job_name)}"
        return self._get_request(url)

