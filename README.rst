gd.bot
=============

.. image:: https://img.shields.io/pypi/l/gd.bot.svg
    :target: https://opensource.org/licenses/MIT
    :alt: Project License

.. image:: https://img.shields.io/pypi/v/gd.bot.svg
    :target: https://pypi.python.org/pypi/gd.bot
    :alt: PyPI Library Version

.. image:: https://img.shields.io/pypi/pyversions/gd.bot.svg
    :target: https://pypi.python.org/pypi/gd.bot
    :alt: Required Python Versions

.. image:: https://img.shields.io/pypi/status/gd.bot.svg
    :target: https://github.com/nekitdev/gd.bot
    :alt: Project Development Status

.. image:: https://img.shields.io/pypi/dm/gd.bot.svg
    :target: https://pypi.python.org/pypi/gd.bot
    :alt: Library Downloads/Month

.. image:: https://img.shields.io/endpoint.svg?url=https%3A%2F%2Fshieldsio-patreon.herokuapp.com%2Fnekit%2Fpledges
    :target: https://patreon.com/nekit
    :alt: Patreon Page [Support]

gd.bot is a Discord Bot which aims to provide interaction with Geometry Dash servers.

Installing
----------

**Python 3.6 or higher is required**

To install the library, you can just run the following command:

.. code:: sh

    # Linux/OS X
    python3 -m pip install -U gd.bot

    # Windows
    py -3 -m pip install -U gd.bot

In order to install the library from source, you can do the following:

.. code:: sh

    $ git clone https://github.com/nekitdev/gd.bot
    $ cd gd.bot
    $ python -m pip install -U .

Running
-------

Running the bot is quite simple.

You can either invoke it from python:

.. code:: python3

    import gd.bot
    gd.bot.run_bot_sync(BOT_TOKEN)

Or run a console command:

.. code:: sh

    $ python -m gd.bot --token BOT_TOKEN

    # OR

    $ gd.bot --token BOT_TOKEN

Authors
-------

This project is mainly developed by `nekitdev <https://github.com/nekitdev>`_.
