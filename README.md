# Twitch Drops Miner

This application allows you to AFK farm timed Twitch drops, without having to worry about switching channels when the one you were watching goes offline, or even receiving the stream data itself. This helps both you and Twitch save on bandwidth and hassle. Everybody wins!

**Features:**

- Stream-less drop mining - save on bandwidth.
- Stream tags and drop campaign validation, so you don't end up watching a stream that can't earn you the drop.
- Stream switching when the one you were currently watching goes offline.
- Cookie saving between sessions, so you don't need to login every time.
- Mining is stopped if the last available drop has been mined.

**Not managed / TODO / manual:**

- Adding additional drop campaigns from other games to your inventory (requires you to do [account linking](https://www.twitch.tv/drops/campaigns) yourself)

**Usage:**

- Download the [lastest release](https://github.com/DevilXD/TwitchDropsMiner/releases) - it's recommended to keep it in the folder it comes with.
- Run it and login into your Twitch using your username and password, and a 2FA key if you have one setup.
- After successful login, the app should fetch a list of all available live channels and start mining right away.
- Persistent cookies will be stored in the `cookies.jar` file, from which the authorization information will be restored on each subsequent run.
- Note: Make sure to keep your cookies file safe, as the authorization information it stores can give another person access to your Twitch account.

**Notes:**

- Successfully logging into your Twitch account in the application, may cause Twitch to send you a "New Login" notification email. This is normal - you can verify that it comes from your own IP address. The application uses Chrome's user agent, so the detected browser during the login should signify that as well.
