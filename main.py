import click
from labelserver import app


@click.group()
@click.pass_context
def cli(ctx):
    pass

@cli.command()
@click.option("--host", '-h', default="localhost", help="Host address to listen on")
@click.option("--port", '-p', default=5000, help="Port to listen on")
@click.option("--threaded", is_flag=True)
@click.option("--debug/--no-debug", "-d/-D", is_flag=True, default=None, help="enable the Werkzeug debugger")
@click.option("use_reloader", "--reload/--no-reload", "-r/-R", is_flag=True, default=None,
              help="Monitor for changes and reload automatically")
def runserver(host, port, threaded, debug, use_reloader):
    use_reloader = debug if use_reloader is None else use_reloader
    app.run(host=host, port=port, threaded=threaded, debug=debug, use_reloader=use_reloader)


if __name__ == "__main__":
    cli()
