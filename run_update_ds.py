import subprocess
import pprint
import os

updateds_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'updateds.py')

# prod
python_path = '/home/deploy/.deploy/bin/python'
# test
#python_path = 'python'

subprocess.call(['python', updateds_path, '--country', 'Austria'])
subprocess.call(['python', updateds_path, '--country', 'Germany'])
subprocess.call(['python', updateds_path, '--country', 'United Kingdom'])
subprocess.call(['python', updateds_path, '--country', 'Italy'])
subprocess.call(['python', updateds_path, '--country', 'Netherlands'])
subprocess.call(['python', updateds_path, '--country', 'Iceland'])
subprocess.call(['python', updateds_path, '--country', 'Finland'])
# subprocess.call(['python', updateds_path, '--country', 'Italy'])
subprocess.call(['python', updateds_path, '--country', 'Ireland'])
subprocess.call(['python', updateds_path, '--country', 'Switzerland'])

# subprocess.call(['python', updateds_path, '--country', 'Canada'])
# logging.info('+ Done Updating prices of... Canada...')

# subprocess.call(['python', updateds_path, '--country', 'Austria'])
# logging.info('+ Done Updating prices of... Austria...')

# subprocess.call(['python', updateds_path, '--country', 'Belgium'])
# logging.info('+ Done Updating prices of... Belgium...')

# subprocess.call(['python', updateds_path, '--country', 'Germany'])
# logging.info('+ Done Updating prices of... Germany...')

# subprocess.call(['python', updateds_path, '--country', 'United Kingdom'])
# logging.info('+ Done Updating prices of... United Kingdom...')

# subprocess.call(['python', updateds_path, '--country', 'Spain'])
# logging.info('+ Done Updating prices of... Spain...')

# subprocess.call(['python', updateds_path, '--country', 'Italy'])
# logging.info('+ Done Updating prices of... Italy...')

# subprocess.call(['python', updateds_path, '--country', 'Greece'])
# logging.info('+ Done Updating prices of... Greece...')

# subprocess.call(['python', updateds_path, '--country', 'Netherlands'])
# logging.info('+ Done Updating prices of... Netherlands...')

# subprocess.call(['python', updateds_path, '--country', 'Portugal'])
# logging.info('+ Done Updating prices of... Portugal...')