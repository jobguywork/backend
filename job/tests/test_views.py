from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from job.models import Job
from utilities.utilities import slug_helper

User = get_user_model()


class JobTests(APITestCase):
    def setUp(self):
        # Creating test superuser
        user_data = {
            "username": "testsuperuser",
            "email": "testsuperuser@gmail.com",
            "password": "testuser123",
        }
        self.user = User.objects.create_superuser(**user_data)
        self.user.profile.email_confirmed = True
        self.user.profile.email = "testsuperuser@gmail.com"
        self.user.profile.save()

        # Getting token
        url = "/authnz/login_email/"
        self.token = self.client.post(url, user_data, format="json").json()["data"][
            "token"
        ]

        # Creating job
        Job.objects.create(
            name="برنامه نویس وب",
            job_slug=slug_helper("برنامه نویس وب"),
            cover="/default/system/cover.jpg",
            icon="fas fa-home",
            description="توسعه دهنده و برنامه نویس وب",
            is_deleted=False,
            approved=False,
        )

        Job.objects.create(
            name="برنامه نویس بک اند",
            job_slug=slug_helper("برنامه نویس بک اند"),
            cover="/default/system/cover.jpg",
            icon="fas fa-home",
            description="توسعه دهنده و برنامه نویس بک اند",
            is_deleted=False,
            approved=False,
        )

    def test_job_create_view(self):
        url = "/job/create/"
        data = {
            "name": "برنامه نویس پایتون",
            "cover": "/default/system/cover.jpg",
            "icon": "fas fa-home",
            "description": "برنامه نویس پایتون",
        }
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)
        response = self.client.post(url, data, format="json")
        job = Job.objects.last()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["content-type"], "application/json")
        self.assertEqual(Job.objects.count(), 3)
        self.assertEqual(job.name, "برنامه نویس پایتون")
        self.assertEqual(job.job_slug, slug_helper("برنامه نویس پایتون"))

    def test_job_list_view_with_no_query_params(self):
        url = "/job/list/"
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)
        response = self.client.get(url)
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            list(response_data["data"][0].keys()),
            [
                "id",
                "name",
                "job_slug",
                "cover",
                "icon",
                "description",
                "is_deleted",
                "approved",
            ],
        )
        self.assertEqual(response["content-type"], "application/json")
        self.assertEqual(len(response_data["data"]), 2)
        self.assertEqual(response_data["total"], 2)

    def test_job_list_view_with_query_params(self):
        index = 1
        size = 10
        order_by = "name"
        url = f"/job/list/?index={index}&size={size}&order_by={order_by}"
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)
        response = self.client.get(url)
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data["index"], 1)
        self.assertEqual(response_data["total"], 2)
        self.assertEqual(len(response_data["data"]), 1)
        self.assertEqual(response_data["data"][0]["name"], "برنامه نویس وب")

    def test_job_list_view_with_out_of_range_index_query_params(self):
        index = 100
        url = f"/job/list/?index={index}"
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)
        response = self.client.get(url)
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data["data"], [])
        self.assertEqual(response_data["index"], 100)
        self.assertEqual(response_data["total"], 2)

    def test_job_list_view_for_public_with_no_query_params(self):
        url = "/public/job/list/"
        response = self.client.get(url)
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["content-type"], "application/json")
        self.assertNotContains(response, "is_deleted")
        self.assertNotContains(response, "approved")
        self.assertNotContains(response, "id")
        self.assertEqual(len(response_data["data"]), 2)
        self.assertEqual(response_data["total"], 2)
        self.assertEqual(response_data["index"], 0)

    def test_job_list_view_for_public_with_query_params(self):
        index = 1
        size = 10
        order_by = "name"
        url = f"/public/job/list/?index={index}&size={size}&order_by={order_by}"
        response = self.client.get(url)
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data["index"], 1)
        self.assertEqual(response_data["total"], 2)
        self.assertEqual(len(response_data["data"]), 1)
        self.assertEqual(response_data["data"][0]["name"], "برنامه نویس وب")

    def test_job_list_view_for_public_with_out_of_range_index_query_params(self):
        index = 100
        url = f"/public/job/list/?index={index}"
        response = self.client.get(url)
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data["data"], [])
        self.assertEqual(response_data["index"], 100)
        self.assertEqual(response_data["total"], 2)

    def test_job_update_view_with_put_method_when_objects_exists(self):
        job = Job.objects.first()
        url = f"/job/{job.id}/update/"
        data = {
            "id": 10,
            "name": "برنامه نویس Go",
            "job_slug": slug_helper("برنامه نویس Go"),
            "cover": "/default/system/cover2.jpg",
            "icon": "fas fa-home2",
            "description": "برنامه نویس Go",
            "is_deleted": True,
            "approved": True,
        }
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)
        response = self.client.put(url, data, format="json")
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["content-type"], "application/json")
        # Constant fields
        self.assertEqual(job.id, response_data["data"]["id"])
        self.assertEqual(job.name, response_data["data"]["name"])
        self.assertEqual(job.job_slug, response_data["data"]["job_slug"])
        self.assertFalse(job.is_deleted)
        self.assertFalse(job.approved)
        # Changed fields
        self.assertEqual(response_data["data"]["cover"], data["cover"])
        self.assertEqual(response_data["data"]["icon"], data["icon"])
        self.assertEqual(response_data["data"]["description"], data["description"])

    def test_job_update_view_with_put_method_when_objects_not_exists(self):
        data = {
            "id": 10,
            "name": "برنامه نویس Go",
            "job_slug": slug_helper("برنامه نویس Go"),
            "cover": "/default/system/cover2.jpg",
            "icon": "fas fa-home2",
            "description": "برنامه نویس Go",
            "is_deleted": True,
            "approved": True,
        }
        url = "/job/5000/update/"
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)
        response = self.client.put(url, data, format="json")
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_data["message"], "Instance does not exist.")

    def test_job_update_view_with_patch_method_when_object_exists(self):
        job = Job.objects.first()
        url = f"/job/{job.id}/update/"
        partial_data = {
            "cover": "/default/system/cover3.jpg",
            "icon": "fas fa-home3",
            "description": "برنامه نویس Rust",
        }

        data = {
            "id": job.id,
            "name": "برنامه نویس وب",
            "job_slug": "برنامه-نویس-وب",
            "cover": "/default/system/cover3.jpg",
            "icon": "fas fa-home3",
            "description": "برنامه نویس Rust",
            "is_deleted": False,
            "approved": False,
        }
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)
        response = self.client.patch(url, partial_data, format="json")
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["content-type"], "application/json")
        self.assertEquals(response_data["data"], data)

    def test_job_update_with_patch_method_when_object_not_exists(self):
        partial_data = {
            "cover": "/default/system/cover3.jpg",
            "icon": "fas fa-home3",
            "description": "برنامه نویس Rust",
        }
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)
        url = "/job/5000/update/"
        response = self.client.patch(url, partial_data, format="json")
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_data["message"], "Instance does not exist.")

    def test_job_delete_view_when_object_exists(self):
        job = Job.objects.first()
        url = f"/job/{job.id}/delete/"
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)
        response = self.client.delete(url)
        response_data = response.json()
        self.assertEqual(response["content-type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data["data"], {})

    def test_job_delete_view_when_object_not_exists(self):
        url = "/job/5000/delete/"
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)
        response = self.client.delete(url)
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_data["message"], "Instance does not exist.")
