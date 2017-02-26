"""Discord bot for getting info from DSDA"""

import asyncio

from datetime import datetime
from discord.ext import commands
from dsda_client.dsda_client_class import DSDAClient

__author__ = '4shockblast'


HELP_STRING = '''```Available commands to DSDA:
  - !dsda get_record (gr) <wad_name> <category> (<map_number>)
      Get record for given wad name, category, and map number
      if provided.

      If map number is not provided, the client will only search
      through the first map on the wad page. Map number format
      must be "e#m#" or "map##" or "d#ep#" or "d#all". If the
      format is # or ##, it will be assumed to be for map##.

      Wad and category names with spaces must be put in quotes,
      e.g. "2 (1994)".

  - !dsda playerstats (ps) <player_name>
      Get player stats for player with player_name or containing
      player_name.

  - !dsda wadstats (ws) <wad_name>
      Get wad stats for wad with wad_name or containing
      wad_name.

  - !dsda random_player_page (rpp)
      Returns random player page URL and name.

  - !dsda random_wad_page (rwp)
      Returns random wad page URL and name.

  - !dsda help
      You're reading it.```'''


class DSDACog:
    """DSDA cog object

    Defines commands used to get info from DSDA through the DSDA client
    """
    PLAYER_STATS_RESULT_STRING = ('```Player name: {player}\n'
                                  'Total demo count: {run_count}\n'
                                  'Total demo time: {total_time}\n'
                                  'Longest demo: {longest_time}\n'
                                  'Average demo time: {avg_time}\n'
                                  'TAS demo count: {tas_count}\n'
                                  'Average demos per wad: {avg_demos}\n'
                                  'Number of distinct wads: {num_distinct}\n'
                                  'Maximum recorded wad: {max_wad}, '
                                  '{count_wad} demos\n'
                                  'Maximum recorded category: {max_cat}, '
                                  '{count_cat} demos```')
    WAD_STATS_RESULT_STRING = ('```Wad name: {wad}\n'
                               'Total demo count: {run_count}\n'
                               'Total demo time: {total_time}\n'
                               'Average demo time: {avg_time}\n'
                               'Number of players: {num_players}\n'
                               'Player with most demos: {player}, {count} '
                               'demos```')
    NEW_UPDATE_MESSAGE = 'A new update was posted! Check it out at: \n' \
                         'http://doomedsda.us/updates.html'

    LATEST_UPDATE_FILE = 'latest_update.txt'

    def __init__(self, _bot):
        """Initialize whatever is needed"""
        self.bot = _bot
        self.bot.loop.create_task(self.get_latest_update())

        self._dsda_client = DSDAClient()
        self.notify_dsda_updates = True

    @commands.group(pass_context=True)
    async def dsda(self, ctx):
        """Returns the current list of entrants of the race.

        Only possible if race has been started. Does not mention the players.
        """
        if ctx.invoked_subcommand is None:
            await bot.say('Invalid DSDA command passed.')

    @dsda.command(pass_context=True)
    async def help(self, ctx):
        """Command to get record from DSDA

        Long command version
        """
        await bot.send_message(ctx.message.author, HELP_STRING)

    @dsda.command()
    async def get_record(self, wad: str, category: str, map_number=None):
        """Command to get record from DSDA

        Long command version
        """
        await self._get_record(wad, category, map_number)

    @dsda.command()
    async def gr(self, wad: str, category: str, map_number=None):
        """Command to get record from DSDA

        Short command version
        """
        await self._get_record(wad, category, map_number)

    async def _get_record(self, wad: str, category: str, map_number=None):
        """Gets record from DSDA"""
        record_tuple = self._dsda_client.get_record(wad, category, map_number)
        record_info = record_tuple[0]
        if record_info is not None:
            await bot.say('**{time}** by **{player}**\nDemo link: '
                          '{demo}'.format(time=record_info[0],
                                          player=record_info[1],
                                          demo=record_info[2]))
        else:
            await bot.say(record_tuple[1])

    @dsda.command()
    async def playerstats(self, *, player: str):
        """Command to get player stats from DSDA

        Long command version
        """
        await self._playerstats(player)

    @dsda.command()
    async def ps(self, *, player: str):
        """Command to get player stats from DSDA

        Short command version
        """
        await self._playerstats(player)

    async def _playerstats(self, player):
        """Gets player stats from DSDA"""
        player_stats_tuple = self._dsda_client.get_player_stats(player)
        player_stats = player_stats_tuple[0]
        if player_stats:
            if not player_stats['max_wad'][1]:
                player_stats['max_wad'] = None, 'no'
            if not player_stats['max_category'][1]:
                player_stats['max_category'] = None, 'no'
            stats_string = self.PLAYER_STATS_RESULT_STRING.format(
                player=player_stats['player_name'],
                run_count=player_stats['total_run_count'],
                total_time=player_stats['total_time'],
                longest_time=player_stats['longest_time'],
                avg_time=player_stats['average_time'],
                tas_count=player_stats['tas_run_count'],
                avg_demos=player_stats['average_runs_per_wad'],
                num_distinct=player_stats['num_distinct_wads'],
                max_wad=player_stats['max_wad'][0],
                count_wad=player_stats['max_wad'][1],
                max_cat=player_stats['max_category'][0],
                count_cat=player_stats['max_category'][1]
            )
            await bot.say(stats_string)
        else:
            await bot.say(player_stats_tuple[1])

    @dsda.command()
    async def wadstats(self, *, wad: str):
        """Command to get wad stats from DSDA

        Long command version
        """
        await self._wadstats(wad)

    @dsda.command()
    async def ws(self, *, wad: str):
        """Command to get wad stats from DSDA

        Short command version
        """
        await self._wadstats(wad)

    async def _wadstats(self, wad):
        """Gets wad stats from DSDA"""
        wad_stats_tuple = self._dsda_client.get_wad_stats(wad)
        wad_stats = wad_stats_tuple[0]
        if wad_stats:
            if not wad_stats['max_player'][1]:
                wad_stats['max_player'] = None, 'no'
            stats_string = self.WAD_STATS_RESULT_STRING.format(
                wad=wad_stats['wad_name'],
                run_count=wad_stats['total_run_count'],
                total_time=wad_stats['total_time'],
                avg_time=wad_stats['average_time'],
                num_players=wad_stats['num_distinct_players'],
                player=wad_stats['max_player'][0],
                count=wad_stats['max_player'][1]
            )
            await bot.say(stats_string)
        else:
            await bot.say(wad_stats_tuple[1])

    @dsda.command()
    async def random_player_page(self):
        """Command to get random player page from DSDA

        Long command version
        """
        await self._random_player_page()

    @dsda.command()
    async def rpp(self):
        """Command to get random player page from DSDA

        Short command version
        """
        await self._random_player_page()

    async def _random_player_page(self):
        """Gets random player page from DSDA"""
        random_player_page_tuple = self._dsda_client.random_player_page()
        await self.bot.say('{player_name}: {player_url}'.format(
            player_name=random_player_page_tuple[1],
            player_url=random_player_page_tuple[0]
        ))

    @dsda.command()
    async def random_wad_page(self):
        """Command to get random wad page from DSDA

        Long command version
        """
        await self._random_wad_page()

    @dsda.command()
    async def rwp(self):
        """Command to get random wad page from DSDA

        Short command version
        """
        await self._random_wad_page()

    async def _random_wad_page(self):
        """Gets random wad page from DSDA"""
        random_wad_page_tuple = self._dsda_client.random_wad_page()
        await self.bot.say('{wad_name}: {wad_url}'.format(
            wad_name=random_wad_page_tuple[1],
            wad_url=random_wad_page_tuple[0]
        ))

    async def get_latest_update(self):
        """Polls for and gets latest update from DSDA

        Polling happens only at the end of the week and only once per each
        five minute period. Only runs if it can post to a channel called
        "speed".
        """
        await self.bot.wait_until_ready()
        speed_channel = None
        for channel in bot.get_all_channels():
            if channel.name == 'speed':
                speed_channel = channel
        if speed_channel is not None:
            while not self.bot.is_closed:
                day_of_week = datetime.today().weekday()
                # Check only if it's the end of the week (Saturday, Sunday,
                # or Monday)
                if (day_of_week == 0 or
                        day_of_week == 5 or
                        day_of_week == 6):
                    with open(self.LATEST_UPDATE_FILE) as latest_update_file:
                        latest_known_update = latest_update_file.read()
                    latest_update = self._dsda_client.get_last_update_date()
                    if latest_update != latest_known_update:
                        await self.bot.send_message(speed_channel,
                                                    self.NEW_UPDATE_MESSAGE)
                        with open(self.LATEST_UPDATE_FILE, 'w') as \
                                latest_update_file:
                            latest_update_file.write(latest_update)
                        self._dsda_client.sync_full()
                # Update check runs every five minutes
                await asyncio.sleep(300)


PREFIXES = ['!', '\N{HEAVY EXCLAMATION MARK SYMBOL}']
DESCRIPTION = '''Bot for getting info from DSDA'''
bot = commands.Bot(command_prefix=PREFIXES, description=DESCRIPTION)


@bot.event
async def on_ready():
    """Prints debug info on startup."""
    print('------')
    print('Username: ' + bot.user.name)
    print('User ID: ' + bot.user.id)
    print('------')


@bot.event
async def on_resumed():
    """Triggered when bot resumes after interruption"""
    print('Resumed...')


@bot.event
async def on_command_error(error, ctx):
    """Catches errors and sends messages to channel."""
    if isinstance(error, commands.MissingRequiredArgument):
        await bot.send_message(ctx.message.channel,
                               'Missing required argument for command.')


if __name__ == '__main__':
    with open('token.txt') as token_file:
        token = token_file.readline()
    bot.add_cog(DSDACog(bot))
    bot.run(token.rstrip())
