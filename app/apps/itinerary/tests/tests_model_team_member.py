from apps.itinerary.models import Itinerary, ItineraryTeamMember
from apps.users.models import User
from django.test import TestCase


class TeamMemberModelTest(TestCase):
    def test_create_team_member(self):
        """
        TeamMember can be created
        """
        user = User.objects.create(email="foo@foo.com")
        itinerary = Itinerary.objects.create()

        self.assertEqual(ItineraryTeamMember.objects.count(), 0)
        ItineraryTeamMember.objects.create(user=user, itinerary=itinerary)
        self.assertEqual(ItineraryTeamMember.objects.count(), 1)

    def test_reverse_relationship_itinerary(self):
        """
        An Itinerary's team can be accessed using the reverse relationship
        """
        user_a = User.objects.create(email="foo_a@foo.com")
        user_b = User.objects.create(email="foo_b@foo.com")
        itinerary = Itinerary.objects.create()

        self.assertEqual(itinerary.team_members.count(), 0)
        ItineraryTeamMember.objects.create(user=user_a, itinerary=itinerary)
        ItineraryTeamMember.objects.create(user=user_b, itinerary=itinerary)
        self.assertEqual(itinerary.team_members.count(), 2)

    def test_reverse_relationship_user(self):
        """
        Teams can be accessed from users using the reverse relationship
        """
        user = User.objects.create(email="foo@foo.com")
        itinerary_a = Itinerary.objects.create()
        itinerary_b = Itinerary.objects.create()

        self.assertEqual(user.teams.count(), 0)
        ItineraryTeamMember.objects.create(user=user, itinerary=itinerary_a)
        ItineraryTeamMember.objects.create(user=user, itinerary=itinerary_b)
        self.assertEqual(user.teams.count(), 2)

    def test_string_representation(self):
        """
        String representation of the team member should be its full name
        """
        user = User.objects.create(email="f.foo@foo.com")
        itinerary = Itinerary.objects.create()
        itinerary_team_member = ItineraryTeamMember.objects.create(
            user=user, itinerary=itinerary
        )

        self.assertEqual("F. Foo", str(itinerary_team_member))
