from __future__ import annotations

import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from constants import GQL_QUERIES, State
from twitch import Twitch
from utils import Game


class CampaignRefreshTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.miner = object.__new__(Twitch)
        self.miner._state = State.CHANNEL_SWITCH
        self.miner._state_change = asyncio.Event()
        self.miner._campaign_fingerprint = frozenset()
        self.miner._channel_retry_games = None
        self.miner.inventory = []
        self.miner.wanted_games = []
        self.miner.gql_request = AsyncMock()

    @staticmethod
    def campaign(campaign_id: str, status: str) -> dict[str, str]:
        return {"id": campaign_id, "status": status}

    def respond_with(self, *campaigns: dict[str, str]) -> None:
        self.miner.gql_request.return_value = {
            "data": {"currentUser": {"dropCampaigns": list(campaigns)}}
        }

    async def test_new_campaign_requests_full_inventory_refresh(self) -> None:
        self.miner._campaign_fingerprint = frozenset({("known", "ACTIVE")})
        self.respond_with(
            self.campaign("known", "ACTIVE"),
            self.campaign("new", "ACTIVE"),
        )

        await self.miner._check_campaign_updates()

        self.assertIs(self.miner._state, State.INVENTORY_FETCH)
        self.assertEqual(
            self.miner._campaign_fingerprint,
            frozenset({("known", "ACTIVE")}),
        )
        self.miner.gql_request.assert_awaited_once_with(GQL_QUERIES["Campaigns"])

    async def test_order_and_expired_campaigns_do_not_trigger_refresh(self) -> None:
        self.miner._campaign_fingerprint = frozenset(
            {("first", "ACTIVE"), ("second", "UPCOMING")}
        )
        self.respond_with(
            self.campaign("expired", "EXPIRED"),
            self.campaign("second", "UPCOMING"),
            self.campaign("first", "ACTIVE"),
        )

        await self.miner._check_campaign_updates()

        self.assertIs(self.miner._state, State.CHANNEL_SWITCH)

    async def test_campaign_status_change_triggers_refresh(self) -> None:
        self.miner._campaign_fingerprint = frozenset({("known", "UPCOMING")})
        self.respond_with(self.campaign("known", "ACTIVE"))

        await self.miner._check_campaign_updates()

        self.assertIs(self.miner._state, State.INVENTORY_FETCH)

    async def test_idle_non_acl_campaign_requests_channel_rediscovery(self) -> None:
        game = Game({"id": 1, "name": "Example"})
        self.miner._state = State.IDLE
        self.miner._campaign_fingerprint = frozenset({("known", "ACTIVE")})
        self.miner.wanted_games = [game]
        self.miner.inventory = [
            SimpleNamespace(
                game=game,
                allowed_channels=[],
                can_earn=lambda: True,
            )
        ]
        self.respond_with(self.campaign("known", "ACTIVE"))

        await self.miner._check_campaign_updates()

        self.assertIs(self.miner._state, State.CHANNELS_FETCH)
        self.assertEqual(self.miner._channel_retry_games, {game})

    async def test_idle_acl_campaign_relies_on_existing_subscriptions(self) -> None:
        game = Game({"id": 1, "name": "Example"})
        self.miner._state = State.IDLE
        self.miner._campaign_fingerprint = frozenset({("known", "ACTIVE")})
        self.miner.wanted_games = [game]
        self.miner.inventory = [
            SimpleNamespace(
                game=game,
                allowed_channels=[object()],
                can_earn=lambda: True,
            )
        ]
        self.respond_with(self.campaign("known", "ACTIVE"))

        await self.miner._check_campaign_updates()

        self.assertIs(self.miner._state, State.IDLE)
        self.assertIsNone(self.miner._channel_retry_games)

    async def test_probe_loop_randomizes_phase_and_five_minute_cadence(self) -> None:
        self.miner._check_campaign_updates = AsyncMock()
        sleep = AsyncMock(side_effect=[None, asyncio.CancelledError()])
        with (
            patch("twitch.random.uniform", side_effect=[120, 300]) as uniform,
            patch("twitch.asyncio.sleep", sleep),
            self.assertRaises(asyncio.CancelledError),
        ):
            await self.miner._campaign_probe_loop()

        self.miner._check_campaign_updates.assert_awaited_once_with()
        self.assertEqual(
            [args.args for args in uniform.call_args_list],
            [(0, 300.0), (270.0, 330.0)],
        )
        self.assertEqual(
            [args.args for args in sleep.await_args_list],
            [(120,), (300,)],
        )


if __name__ == "__main__":
    unittest.main()
