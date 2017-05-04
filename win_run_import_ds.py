import subprocess
import pprint

subprocess.call(['python', 'importds.py', '--country', 'Canada'])
pprint.pprint('Done importing Canada...')

subprocess.call(['python', 'importds.py', '--country', 'Austria'])
pprint.pprint('Done importing Austria...')

subprocess.call(['python', 'importds.py', '--country', 'Belgium'])
pprint.pprint('Done importing Belgium...')

subprocess.call(['python', 'importds.py', '--country', 'Germany'])
pprint.pprint('Done importing Belgium...')

subprocess.call(['python', 'importds.py', '--country', 'United Kingdom'])
pprint.pprint('Done importing UK...')

subprocess.call(['python', 'importds.py', '--country', 'Spain'])
pprint.pprint('Done importing Spain...')

subprocess.call(['python', 'importds.py', '--country', 'Italy'])
pprint.pprint('Done importing Italy...')

subprocess.call(['python', 'importds.py', '--country', 'Greece'])
pprint.pprint('Done importing Greece...')

subprocess.call(['python', 'importds.py', '--country', 'Netherlands'])
pprint.pprint('Done importing Netherlands...')

subprocess.call(['python', 'importds.py', '--country', 'Portugal'])
pprint.pprint('Done importing Portugal...')
