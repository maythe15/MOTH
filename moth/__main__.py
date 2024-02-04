if __name__=='__main__':
    import argparse
    import sqlalchemy
    import sqlalchemy_utils
    import moth.utils as utils
    import moth.server as server
    import sqlalchemy.orm as orm
    import sys
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers(dest='command')
    make = subs.add_parser('create')
    make.add_argument('-f', '--file', action='store', default='moth.db', help='File to store DB into')
    run = subs.add_parser('run')
    run.add_argument('-f', '--file', action='store', default='moth.db', help='File to store DB into')
    run.add_argument('-p', '--port', action='store', type=int, default=1000, help='Server port')
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    if args.command == 'create':
        engine = sqlalchemy.create_engine(f"sqlite:///{args.file}")
        if not sqlalchemy_utils.database_exists(engine.url):
            sqlalchemy_utils.create_database(engine.url)
        utils.Base.metadata.create_all(engine)
        with orm.Session(engine) as session:
            session.commit()
    elif args.command == 'run':
        server.run(args.file, args.port)
