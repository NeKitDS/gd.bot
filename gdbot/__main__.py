from typing import Optional

import click


@click.command(name="gdbot")
@click.option("--token", required=True, type=str)
@click.option("--user", type=str)
@click.option("--password", type=str)
def main(token: str, user: Optional[str], password: Optional[str]) -> None:
    import gdbot

    gdbot.run_bot_sync(token, user, password)


if __name__ == "__main__":
    main()
