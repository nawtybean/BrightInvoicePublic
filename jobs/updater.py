'''
@author: Shaun De Ponte, nawtybean3d@gmail.com

----- The MIT License (MIT) ----- 
Copyright (c) 2023, Shaun De Ponte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .jobs import schedule_billing

def start():
	"""
    Start a background scheduler to execute the schedule_billing function at regular intervals.

    This function initializes a background scheduler using apscheduler library and schedules 
    the execution of the schedule_billing function to occur every day.

    Parameters:
    None

    Returns:
    None
    """

	 # Initialize a BackgroundScheduler object
	scheduler = BackgroundScheduler()
	# Add a job to execute schedule_billing function every day
	scheduler.add_job(schedule_billing, 'interval', days=1)
	# Start the scheduler to begin executing the jobs
	scheduler.start()