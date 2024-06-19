# to run the project in bash terminal, enter command
# python3 cli.py [store/verify] [file_path] --algorithm [algorithm_name] 
# for example:
# python3 cli.py store new.txt --algorithm sha256
# python3 cli.py verify new.txt --algorithm sha256
# python3 cli.py --help for further use

import click
from hash_utils import store_hash, verify_file

@click.group()
def cli():
    pass

@click.command()
@click.argument('file_path', type=click.File('rb'))
@click.option('--algorithm', default='sha256', help='Hashing algorithm to use (default: sha256)')
def store(file_path, algorithm):
    """Store the hash of the given file."""
    filename = file_path.name
    result = store_hash(file_path, filename, algorithm)
    
    if 'Error' in result:
        click.echo(click.style(result, fg='red'))
    else:
        click.echo(click.style(result, fg='yellow'))

@click.command()
@click.argument('file_path', type=click.File('rb'))
@click.option('--algorithm', default='sha256', help='Hashing algorithm to use (default: sha256)')
def verify(file_path, algorithm):
    """Verify the given file's hash."""
    result = verify_file(file_path, algorithm)
    
    if 'No Match Found' in result or 'Error' in result:
        click.echo(click.style(result, fg='red'))
    else:
        click.echo(click.style(result, fg='green'))

cli.add_command(store)
cli.add_command(verify)

if __name__ == '__main__':
    cli()
