from apps.itinerary.models import Itinerary, ItineraryItem, Note
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.utils.unittest_helpers import (
    get_authenticated_client,
    get_test_user,
    get_unauthenticated_client,
)


class NoteViewsCreateTest(APITestCase):
    """
    Tests for the API endpoint for creating Notes
    """

    def test_unauthenticated_post(self):
        """
        An unauthenticated request should not be possible
        """

        url = reverse("v1:notes-list")
        client = get_unauthenticated_client()
        response = client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_create(self):
        """
        An authenticated post should create a note
        """
        user = get_test_user()
        itinerary = Itinerary.objects.create()
        itinerary_item = ItineraryItem.objects.create(itinerary=itinerary)

        self.assertEquals([], list(itinerary_item.notes.all()))

        FOO_TEXT = "FOO NOTE TEXT"

        note_data = {
            "text": FOO_TEXT,
            "itinerary_item": itinerary_item.id,
            "author": {"id": user.id},
        }

        url = reverse("v1:notes-list")
        client = get_authenticated_client()
        response = client.post(url, note_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        notes_create = list(itinerary_item.notes.all())
        self.assertEqual(1, len(notes_create))
        self.assertEqual(FOO_TEXT, notes_create[0].text)


class NoteViewsUpdateTest(APITestCase):
    """
    Tests for the API endpoint for updating Notes
    """

    def test_unauthenticated_put(self):
        """
        An unauthenticated request should not be possible
        """
        url = reverse("v1:notes-detail", kwargs={"pk": "foo"})
        client = get_unauthenticated_client()
        response = client.put(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_update(self):
        """
        An authenticated post should update a note
        """
        NOTE_TEXT = "FOO NOTE TEXT"
        NOTE_TEXT_UPDATED = "FOO NOTE TEXT UPDATED"

        user = get_test_user()
        itinerary = Itinerary.objects.create()
        itinerary_item = ItineraryItem.objects.create(itinerary=itinerary)
        note = Note.objects.create(
            itinerary_item=itinerary_item, author=user, text=NOTE_TEXT
        )

        url = reverse("v1:notes-detail", kwargs={"pk": note.id})
        client = get_authenticated_client()
        response = client.put(
            url,
            {"text": NOTE_TEXT_UPDATED, "itinerary_item": itinerary_item.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(NOTE_TEXT_UPDATED, itinerary_item.notes.all()[0].text)


class NoteViewsDeleteTest(APITestCase):
    """
    Tests for the API endpoint for deleting Notes
    """

    def test_unauthenticated_delete(self):
        """
        An unauthenticated request should not be possible
        """
        url = reverse("v1:notes-detail", kwargs={"pk": "foo"})
        client = get_unauthenticated_client()
        response = client.delete(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_delete(self):
        """
        An authenticated delete should remove a note
        """
        user = get_test_user()
        itinerary = Itinerary.objects.create()
        itinerary_item = ItineraryItem.objects.create(itinerary=itinerary)
        note = Note.objects.create(
            itinerary_item=itinerary_item, author=user, text="foo"
        )

        self.assertEqual(1, len(itinerary_item.notes.all()))

        url = reverse("v1:notes-detail", kwargs={"pk": note.id})
        client = get_authenticated_client()
        response = client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(0, len(itinerary_item.notes.all()))


class NoteViewsGetTest(APITestCase):
    """
    Tests for the API endpoint for getting Notes
    """

    def test_unauthenticated_get(self):
        """
        An unauthenticated request should not be possible
        """
        url = reverse("v1:notes-detail", kwargs={"pk": "foo"})
        client = get_unauthenticated_client()
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_get(self):
        """
        An authenticated get should get notes
        """
        NOTE_TEXT = "FOO NOTE TEXT"
        user = get_test_user()
        itinerary = Itinerary.objects.create()
        itinerary_item = ItineraryItem.objects.create(itinerary=itinerary)
        note = Note.objects.create(
            itinerary_item=itinerary_item, author=user, text=NOTE_TEXT
        )

        url = reverse("v1:notes-detail", kwargs={"pk": note.id})
        client = get_authenticated_client()
        response = client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["text"], NOTE_TEXT)
