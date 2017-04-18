def main(): 
	from crontab import CronTab

	cron = CronTab(tabfile='filename.tab')

	job = cron.new(command='python ds.py')
	job.minute.every(1)
	# job.hour.on(12)

	cron.write()

if __name__ == "__main__":
	main()

