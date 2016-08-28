import sqlite3
import fileinput
import sys
import argparse
# import re

def process_sql(cur, line):
    cur.execute(line)

class tcolors:
    INFO = '\033[93m'
    ERROR = '\033[95m'
    RESET = '\033[0m'

if __name__ == '__main__':

    # Initialize the command parser
    parser = argparse.ArgumentParser(description='Initialize a DB.')
    parser.add_argument('-f', '--force-all', action='store_true')
    parser.add_argument('db')
    parser.add_argument('sql', nargs='+')

    args = parser.parse_args()

    # Load the sqlite db
    conn = sqlite3.connect(args.db)

    # For every line in every file run the command.
    for filename in args.sql:
        try:
            f = open(filename, 'r');

            # Get rid of newlines and split every semicolon.
            text = f.read()

            # text = re.sub('#.*', ' ', text)

            for query in text.replace('\n', ' ').split(';'):
                # If we have a blank line don't even bother
                if query.strip() != '':
                    cur = conn.cursor()
                    try:
                        process_sql(cur, query)
                    except Exception as e:
                        query_clean = ' '.join(query.split())
                        print('Error in:',
                              tcolors.INFO + query_clean + tcolors.RESET,
                              tcolors.ERROR + '(' + str(e) + ')' +
                              tcolors.RESET)
                        if not args.force_all:
                            sys.exit(1)
                    conn.commit()
                    cur.close()

        except OSError as err:
            pass
    conn.close()
