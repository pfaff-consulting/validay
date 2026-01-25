import click
import sys
import os
import runpy

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


def handle_ansible_call():
    if len(sys.argv) < 2:
        return

    is_ansible_module = "AnsiballZ_" in sys.argv[1] or ".ansible/tmp" in sys.argv[1]

    is_playbook_call = any(arg.endswith(('.yaml', '.yml')) for arg in sys.argv) or \
                       any(arg in sys.argv for arg in ['--check', '--inventory', '-i'])

    try:
        if is_ansible_module:
            script_path = sys.argv[1]
            sys.argv = sys.argv[1:]
            runpy.run_path(script_path, run_name='__main__')
            sys.exit(0)

        elif is_playbook_call:
            from ansible.cli.playbook import PlaybookCLI
            ansible_argv = sys.argv[:]
            ansible_argv[0] = 'ansible-playbook'

            cli = PlaybookCLI(ansible_argv)
            cli.run()
            sys.exit(0)

    except Exception as e:
        with open("/tmp/ansible_hijack_error.txt", "a") as f:
            import traceback
            f.write(f"--- Error at {os.path.basename(sys.argv[0])} ---\n")
            f.write(f"Args: {sys.argv}\n")
            f.write(traceback.format_exc())
            f.write("\n")


if __name__ == "__main__":
    handle_ansible_call()

    exception_handler = AppExceptionHandler()

    try:
        cli(obj={})
    except AppException as e:
        exception_handler.handle(e)
