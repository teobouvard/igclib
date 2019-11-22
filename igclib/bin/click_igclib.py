import click

@click.group()
@click.option('--progress', type=click.Choice(['gui', 'ratio', 'silent']))
@click.pass_context
def main(progress):
    """igclib command line tool"""
    pass

@main.command()
@click.option('--path', type=click.Path(exists=True))
@click.option('--task')
@click.option('--flights')
@click.option('--output')
def race(path, task, flights, output):
    if path is not None:
        race = Race(path=path, progress=progress)
    elif (flights and task) is not None:
        race = Race(tracks=flights, task=task, progress=progress)
    else:
        print('nope')
        exit()

    race.save(output=output)


@main.command()
@click.option('--year', type=click.IntRange(2012, 2020, clamp=True))
def crawl():
    crawler = TaskCrawler(args.provider, args.year, args.progress)
    crawler.crawl(output=args.output)