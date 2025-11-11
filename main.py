import click

from src.api_manager import ApiManager
from src.click_extensions.aliased_group import AliasedGroup
from src.commands.task_checker import TaskChecker
from src.commands.task_selector import TaskSelector
from src.commands.task_status import TaskStatusCommand
from src.commands.task_hint import TaskHintCommand
from src.commands.task_solution import TaskSolutionCommand
from src.config import Config
from src.exception.app_exception import AppException
from src.exception.app_exception_handler import AppExceptionHandler


@click.group(cls=AliasedGroup)
@click.option('-c', '--config', default="/etc/validay/config.yaml", help="Path to the general config file.")
@click.pass_context
def cli(ctx, config):
    ctx.ensure_object(dict)
    cfg = Config.from_file(config)

    ctx.obj['config'] = cfg
    ctx.obj['api_manager'] = ApiManager(
        cfg.base_url, cfg.api_token
    )


@cli.command(name='select', help='Select a task')
@click.argument('task_id', required=False)
@click.pass_context
def select_task(ctx, task_id: str):
    ts = TaskSelector(ctx.obj['config'], ctx.obj['api_manager'])
    ts.run(task_id)


# Should be also displayed on 'vd'
@cli.command(name='status', help='Display current task status')
@click.pass_context
def display_status(ctx):
    config: Config = ctx.obj['config']
    api: ApiManager = ctx.obj['api_manager']

    cmd = TaskStatusCommand(config, api)
    cmd.run()


@cli.command(name='hint', help='Show hint for the next subtask')
@click.pass_context
def hint(ctx):
    config: Config = ctx.obj['config']
    api: ApiManager = ctx.obj['api_manager']
    cmd = TaskHintCommand(config, api)
    cmd.run()


@cli.command(name='solution', help='Show solution for the next subtask (asks to confirm if hint not viewed)')
@click.pass_context
def solution(ctx):
    config: Config = ctx.obj['config']
    api: ApiManager = ctx.obj['api_manager']
    cmd = TaskSolutionCommand(config, api)
    cmd.run()


@cli.command(name="check", help="Check the current task")
@click.pass_context
def check(ctx):
    ch = TaskChecker(ctx.obj['config'], ctx.obj['api_manager'])
    ch.run()


if __name__ == "__main__":
    exception_handler = AppExceptionHandler()

    try:
        cli(obj={})
    except AppException as e:
        exception_handler.handle(e)
