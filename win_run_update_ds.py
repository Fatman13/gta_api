import subprocess
import pprint
import os
import logging

updateds_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'updateds.py')

# prod
python_path = '/home/lengyu/.virtualenv/faskdeploy/bin/python'
# test
#python_path = 'python'

# subprocess.call(['python', updateds_path, '--country', 'Canada'])
# pprint.pprint('+ Done Updating prices of... Canada...')

# subprocess.call(['python', updateds_path, '--country', 'Austria'])
# pprint.pprint('+ Done Updating prices of... Austria...')

# subprocess.call(['python', updateds_path, '--country', 'Belgium'])
# pprint.pprint('+ Done Updating prices of... Belgium...')

# subprocess.call(['python', updateds_path, '--country', 'Germany'])
# pprint.pprint('+ Done Updating prices of... Germany...')

# subprocess.call(['python', updateds_path, '--country', 'United Kingdom'])
# pprint.pprint('+ Done Updating prices of... United Kingdom...')

# subprocess.call(['python', updateds_path, '--country', 'Spain'])
# pprint.pprint('+ Done Updating prices of... Spain...')

# subprocess.call(['python', updateds_path, '--country', 'Italy'])
# pprint.pprint('+ Done Updating prices of... Italy...')

# subprocess.call(['python', updateds_path, '--country', 'Greece'])
# pprint.pprint('+ Done Updating prices of... Greece...')

# subprocess.call(['python', updateds_path, '--country', 'Netherlands'])
# pprint.pprint('+ Done Updating prices of... Netherlands...')

# subprocess.call(['python', updateds_path, '--country', 'Portugal'])
# pprint.pprint('+ Done Updating prices of... Portugal...')

subprocess.call(['python', updateds_path, '--country', 'D'])
subprocess.call(['python', updateds_path, '--country', 'IS'])
subprocess.call(['python', updateds_path, '--country', 'A'])
subprocess.call(['python', updateds_path, '--country', 'SF'])
subprocess.call(['python', updateds_path, '--country', 'I'])
subprocess.call(['python', updateds_path, '--country', 'EI'])
subprocess.call(['python', updateds_path, '--country', 'NL'])
subprocess.call(['python', updateds_path, '--country', 'CH'])
subprocess.call(['python', updateds_path, '--country', 'GB'])

# asia
subprocess.call(['python', updateds_path, '--country', 'IA'])
subprocess.call(['python', updateds_path, '--country', 'VI'])
subprocess.call(['python', updateds_path, '--country', 'RS'])
subprocess.call(['python', updateds_path, '--country', 'MA'])
subprocess.call(['python', updateds_path, '--country', 'TH'])