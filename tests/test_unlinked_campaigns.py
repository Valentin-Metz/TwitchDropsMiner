from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from constants import PriorityMode
from inventory import BenefitType, DropsCampaign
from settings import Settings
from twitch import Twitch
from utils import Game


class UnlinkedCampaignSelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime.now(timezone.utc)
        self.settings = SimpleNamespace(
            priority=[],
            exclude=set(),
            priority_mode=PriorityMode.PRIORITY_ONLY,
            unlinked_campaigns=False,
            enable_badges_emotes=False,
        )
        self.miner = object.__new__(Twitch)
        self.miner.settings = self.settings

    def campaign(
        self,
        game_id: int,
        name: str,
        *,
        linked: bool,
        hours_remaining: int,
        availability: float = 1.0,
        badge: bool = False,
    ) -> DropsCampaign:
        campaign = object.__new__(DropsCampaign)
        campaign._twitch = self.miner
        campaign.game = Game({"id": game_id, "name": name})
        campaign.linked = linked
        campaign._valid = True
        campaign.starts_at = self.now - timedelta(minutes=1)
        campaign.ends_at = self.now + timedelta(hours=hours_remaining)
        benefits = [SimpleNamespace(type=BenefitType.BADGE)] if badge else []
        campaign.timed_drops = {
            "drop": SimpleNamespace(
                benefits=benefits,
                availability=availability,
                _can_earn_within=lambda stamp: True,
            )
        }
        return campaign

    def selected_names(self) -> list[str]:
        next_hour = self.now + timedelta(hours=1)
        return [game.name for game in self.miner._get_wanted_games(next_hour)]

    def test_priority_only_requires_every_campaign_to_be_listed(self) -> None:
        self.settings.unlinked_campaigns = True
        self.settings.priority = ["First", "Second"]
        self.miner.inventory = [
            self.campaign(3, "Fallback late", linked=False, hours_remaining=3),
            self.campaign(5, "Linked unlisted", linked=True, hours_remaining=1),
            self.campaign(2, "Second", linked=True, hours_remaining=5),
            self.campaign(4, "Fallback soon", linked=False, hours_remaining=2),
            self.campaign(1, "First", linked=False, hours_remaining=4),
        ]

        self.assertEqual(self.selected_names(), ["First", "Second"])

    def test_ending_soonest_prioritizes_list_then_all_campaigns(self) -> None:
        self.settings.priority_mode = PriorityMode.ENDING_SOONEST
        self.settings.unlinked_campaigns = True
        self.settings.priority = ["First", "Second"]
        self.miner.inventory = [
            self.campaign(4, "Linked later", linked=True, hours_remaining=4),
            self.campaign(3, "Unlinked soon", linked=False, hours_remaining=1),
            self.campaign(2, "Second", linked=True, hours_remaining=5),
            self.campaign(1, "First", linked=False, hours_remaining=6),
        ]

        self.assertEqual(
            self.selected_names(),
            ["First", "Second", "Unlinked soon", "Linked later"],
        )

    def test_disabled_setting_preserves_priority_only_behavior(self) -> None:
        self.settings.priority = ["Unlinked", "Linked"]
        self.miner.inventory = [
            self.campaign(1, "Unlinked", linked=False, hours_remaining=1),
            self.campaign(2, "Linked", linked=True, hours_remaining=2),
            self.campaign(3, "Linked unlisted", linked=True, hours_remaining=1),
        ]

        self.assertEqual(self.selected_names(), ["Linked"])

    def test_existing_sort_modes_still_ignore_unlinked_campaigns(self) -> None:
        linked_soon = self.campaign(
            1, "Linked soon", linked=True, hours_remaining=1, availability=0.8
        )
        linked_low_availability = self.campaign(
            2, "Linked low availability", linked=True, hours_remaining=3, availability=0.1
        )
        unlinked = self.campaign(
            3, "Unlinked", linked=False, hours_remaining=1, availability=0.0
        )
        self.miner.inventory = [linked_low_availability, unlinked, linked_soon]

        expected_by_mode = {
            PriorityMode.ENDING_SOONEST: ["Linked soon", "Linked low availability"],
            PriorityMode.LOW_AVBL_FIRST: ["Linked low availability", "Linked soon"],
        }
        for mode, expected in expected_by_mode.items():
            with self.subTest(mode=mode):
                self.settings.priority_mode = mode
                self.assertEqual(self.selected_names(), expected)

    def test_unlinked_toggle_does_not_enable_badge_campaigns(self) -> None:
        self.settings.unlinked_campaigns = True
        direct_entitlement = self.campaign(
            1, "Direct entitlement", linked=False, hours_remaining=1
        )
        badge = self.campaign(
            2, "Badge", linked=False, hours_remaining=1, badge=True
        )

        self.assertTrue(direct_entitlement.eligible)
        self.assertFalse(badge.eligible)
        self.settings.enable_badges_emotes = True
        self.assertTrue(badge.eligible)

    def test_missing_settings_use_mine_everything_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_path = Path(temp_dir, "settings.json")
            settings_path.write_text("{}", encoding="utf8")
            with patch("settings.SETTINGS_PATH", settings_path):
                loaded = Settings(SimpleNamespace())

        self.assertTrue(loaded.unlinked_campaigns)
        self.assertIs(loaded.priority_mode, PriorityMode.ENDING_SOONEST)

    def test_explicit_campaign_settings_are_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_path = Path(temp_dir, "settings.json")
            settings_path.write_text(
                '{"unlinked_campaigns": false, "priority_mode": '
                '{"__type": "PriorityMode", "data": 0}}',
                encoding="utf8",
            )
            with patch("settings.SETTINGS_PATH", settings_path):
                loaded = Settings(SimpleNamespace())

        self.assertFalse(loaded.unlinked_campaigns)
        self.assertIs(loaded.priority_mode, PriorityMode.PRIORITY_ONLY)


if __name__ == "__main__":
    unittest.main()
