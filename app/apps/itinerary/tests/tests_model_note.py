from apps.itinerary.models import Itinerary, ItineraryItem, Note
from apps.users.models import User
from django.test import TestCase


class NoteModelTest(TestCase):
    def test_create_note(self):
        """
        A Note can be created
        """
        self.assertEqual(Note.objects.count(), 0)

        user = User.objects.create(email="foo@foo.com")
        itinerary = Itinerary.objects.create()
        itinerary_item = ItineraryItem.objects.create(itinerary=itinerary)
        Note.objects.create(itinerary_item=itinerary_item, author=user, text="hello")

        self.assertEqual(Note.objects.count(), 1)

    def test_multiple_authors(self):
        """
        Multiple authors can leave notes on the same ItineraryItem
        """
        self.assertEqual(Note.objects.count(), 0)

        user_a = User.objects.create(email="foo_a@foo.com")
        user_b = User.objects.create(email="foo_b@foo.com")

        itinerary = Itinerary.objects.create()
        itinerary_item = ItineraryItem.objects.create(itinerary=itinerary)

        Note.objects.create(itinerary_item=itinerary_item, author=user_a, text="hello")
        Note.objects.create(itinerary_item=itinerary_item, author=user_b, text="hello")

        self.assertEqual(Note.objects.count(), 2)

    def test_reverse_access(self):
        """
        Notes can be retrieved through an ItineraryItem using the reverse access 'notes' property
        """
        user_a = User.objects.create(email="foo_a@foo.com")
        user_b = User.objects.create(email="foo_b@foo.com")

        itinerary = Itinerary.objects.create()
        itinerary_item = ItineraryItem.objects.create(itinerary=itinerary)

        self.assertEqual(len(itinerary_item.notes.all()), 0)

        Note.objects.create(itinerary_item=itinerary_item, author=user_a, text="hello")
        Note.objects.create(itinerary_item=itinerary_item, author=user_b, text="hello")

        self.assertEqual(len(itinerary_item.notes.all()), 2)

    def test_string_representation(self):
        """
        __str__ is the full note
        """
        user = User.objects.create(email="foo@foo.com")
        itinerary = Itinerary.objects.create()
        itinerary_item = ItineraryItem.objects.create(itinerary=itinerary)
        note = Note.objects.create(
            itinerary_item=itinerary_item, author=user, text="hello"
        )

        self.assertEqual("hello", str(note))

    def test_string_representation_ellipsis(self):
        """
        __str__ is shortened with an ellipsis if the note is larger than 20 characters
        """
        user = User.objects.create(email="foo@foo.com")
        itinerary = Itinerary.objects.create()
        itinerary_item = ItineraryItem.objects.create(itinerary=itinerary)

        text = "is shortened with an ellipsis if the note is larger than 20 characters"
        note = Note.objects.create(
            itinerary_item=itinerary_item, author=user, text=text
        )

        expected_text = "is shortened with an..."
        self.assertEqual(expected_text, str(note))
