#!/usr/bin/python
import sys
import threading
from time import time
import math
import random
import json

import mesos.interface
from mesos.interface import mesos_pb2
#import mesos.native

# XXX Hardcode client for testing
sys.path.append("/home/vagrant/traveling-sailor")
sys.path.append("../traveling-sailor")
import traveling_sailor
# latitude and longitude for the twenty largest U.S. cities
cities = {
    'New York City': (40.72, 74.00),
    'Los Angeles': (34.05, 118.25),
    'Chicago': (41.88, 87.63),
    'Houston': (29.77, 95.38),
    'Phoenix': (33.45, 112.07),
    'Philadelphia': (39.95, 75.17),
    'San Antonio': (29.53, 98.47),
    'Dallas': (32.78, 96.80),
    'San Diego': (32.78, 117.15),
    'San Jose': (37.30, 121.87),
    'Detroit': (42.33, 83.05),
    'San Francisco': (37.78, 122.42),
    'Jacksonville': (30.32, 81.70),
    'Indianapolis': (39.78, 86.15),
    'Austin': (30.27, 97.77),
    'Columbus': (39.98, 82.98),
    'Fort Worth': (32.75, 97.33),
    'Charlotte': (35.23, 80.85),
    'Memphis': (35.12, 89.97),
    'Baltimore': (39.28, 76.62)
}


class MyExecutor(mesos.interface.Executor):
    def registered(self, driver, executorInfo, frameworkInfo, slaveInfo):
        print "Executor registered"

    def disconnected(self, driver):
        print "Executor disconnected"

    def launchTask(self, driver, task):
        # Create a thread to run the task. Tasks should always be run in new
        # threads or processes, rather than inside launchTask itself.
        def run_task():
            print "Running task %s" % task.task_id.value
            update = mesos_pb2.TaskStatus()
            update.task_id.value = task.task_id.value
            update.state = mesos_pb2.TASK_RUNNING
            update.data = 'task running'
            driver.sendStatusUpdate(update)
            print task.data

            parsed_json = json.loads(task.data)
            uid = parsed_json['uid'] #just echo
            location = parsed_json['location'] #starting search location
            # temperature = parsed_json['temperature'] #starting temperature, decreases
            # cooling_rate = parsed_json['cooling_rate'] #final
            # num_mutations = parsed_json['num_mutations'] #final
            task_seconds = parsed_json['task_seconds']
            task_name = parsed_json['task_name']

            print "start: uid is: ".format(uid)
            print "start: location is: ".format(location)
            # print "start: temperature is: ".format(temperature)
            # print "start: cooling rate is: ".format(cooling_rate)
            # print "start: num_mutations is: ".format(num_mutations)

            # XXX
            tsp = traveling_sailor.TSPSA(cities, location)
            tsp.copy_strategy = "slice"
            auto_schedule = tsp.auto(task_seconds/60.0)
            tsp.set_schedule(auto_schedule)
            best_key, best_fitness = tsp.anneal()

            print "Best Fitness: {}".format(best_fitness)
            print "Best Key: {}".format(best_key)
            print "end: uid is: ".format(uid)
            print "end: location is: ".format(location)
            # print "end: temperature is: ".format(temperature)
            # print "end: cooling rate is: ".format(cooling_rate)
            # print "end: num_mutations is: ".format(num_mutations)

            update = mesos_pb2.TaskStatus()
            update.task_id.value = task.task_id.value
            update.state = mesos_pb2.TASK_FINISHED
            update.data = json.dumps({"uid": uid},{"best_location": best_key},{"fitness_score": best_fitness})
            driver.sendStatusUpdate(update)

        thread = threading.Thread(target=run_task)
        thread.start()

    def frameworkMessage(self, driver, message):
        # Send it back to the scheduler.
        driver.sendFrameworkMessage(message)


def main():
    print "Starting executor"
    driver = mesos.native.MesosExecutorDriver(MyExecutor())
    sys.exit(0 if driver.run() == mesos_pb2.DRIVER_STOPPED else 1)
