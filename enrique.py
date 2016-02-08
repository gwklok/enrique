#!/usr/bin/env python

import sys
import threading
import time
import math
import random
import json

import mesos.interface
from mesos.interface import mesos_pb2
import mesos.native

#import magic_client

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

            # print "query is: {}".format(parsed_json['query'])
            #print "searchSpace is: {}".format(parsed_json['searchSpace'])
            # print "index 0 is: " + str(parsed_json['searchSpace'][0])

            parsed_json = json.loads(task.data)
            uid = parsed_json['uid'] #just echo
            location = parsed_json['location'] #starting search location
            temperature = parsed_json['temperature'] #starting temperature, decreases
            cooling_rate = parsed_json['cooling_rate'] #final
            num_mutations = parsed_json['num_mutations'] #final

            print "start: uid is: ".format(uid)
            print "start: location is: ".format(location)
            print "start: temperature is: ".format(temperature)
            print "start: cooling rate is: ".format(cooling_rate)
            print "start: num_mutations is: ".format(num_mutations)

            # if location is None:
            #     location = magic_random_function()

            e = math.e

        #for i,element in enumerate(1000): # hardcoded number of iterations.. could be higher

            # qfm, floor = quadgram_fitness_from_text(compile_corpora())
            #e = math.e

            # best_key = parent_key = gen_rand_playfair_key()
            best_fitness = parent_fitness = None
            best_key = location
            T = temperature
            while T >= 0:
                print("Temperature: {}".format(T))
                print("Cooling rate: {}".format(cooling_rate))
                print("Fitness: {}".format(parent_fitness))
                print("Key: {}".format(parent_key))
                start = time()
                for i in xrange(num_mutations):
                    new_key = magic_mutation(parent_key) #from client library
                    fitness = magic_fitness_score(new_key) #from client library
                    if parent_fitness is None:
                        parent_fitness = fitness
                        parent_key = new_key
                        continue
                    dF = fitness - parent_fitness
                    if dF > 0.0:
                        best_fitness = parent_fitness = fitness
                        best_key = parent_key = new_key
                    else:
                        prob = e**(dF/T)
                        if prob > random.uniform(0, 1):
                            parent_fitness = fitness
                            parent_key = new_key
                print("Keys/s: {:.2f}".format(num_mutations/(time() - start)))
                print("")
                T -= cooling_rate

            print "Best Fitness: {}".format(best_fitness)
            print "Best Key: {}".format(best_key)
            print "end: uid is: ".format(uid)
            print "end: location is: ".format(location)
            print "end: temperature is: ".format(temperature)
            print "end: cooling rate is: ".format(cooling_rate)
            print "end: num_mutations is: ".format(num_mutations)

            update = mesos_pb2.TaskStatus()
            update.task_id.value = task.task_id.value
            update.state = mesos_pb2.TASK_FINISHED
            update.data = json.dumps({"uid": uid},{"best_location": best_key},{"fitness_score": best_fitness})
            driver.sendStatusUpdate(update)
            return parent_key


            # parsed_json = json.loads(task.data)
            # found = False
            # length = len(parsed_json['searchSpace'])
            # for i,element in enumerate(parsed_json['searchSpace']):
            #     if i%(length/20) == 0:
            #         update = mesos_pb2.TaskStatus()
            #         update.task_id.value = task.task_id.value
            #         update.state = mesos_pb2.TASK_RUNNING
            #         update.data = json.dumps({"progress": float(i)/len(parsed_json['searchSpace'])})
            #         driver.sendStatusUpdate(update)
            #
            #     if parsed_json['query'] == element:
            #         print "found it"
            #         print "got it. neat. index is {} and value is: {}".format(i, element)
            #         update = mesos_pb2.TaskStatus()
            #         update.task_id.value = task.task_id.value
            #         update.state = mesos_pb2.TASK_FINISHED
            #         update.data = json.dumps({"result": i+parsed_json['offset']})
            #         driver.sendStatusUpdate(update)
            #         found = True
            #         break
            #
            # # This is where one would perform the requested task.
            #
            # print "Finished..."
            # if(found == False):
            #     update = mesos_pb2.TaskStatus()
            #     update.task_id.value = task.task_id.value
            #     update.state = mesos_pb2.TASK_FINISHED
            #     update.data = json.dumps({"result": -1})
            #     driver.sendStatusUpdate(update)
            # print "Sent status update"

        thread = threading.Thread(target=run_task)
        thread.start()

    def frameworkMessage(self, driver, message):
        # Send it back to the scheduler.
        driver.sendFrameworkMessage(message)

if __name__ == "__main__":
    print "Starting executor"
    driver = mesos.native.MesosExecutorDriver(MyExecutor())
    sys.exit(0 if driver.run() == mesos_pb2.DRIVER_STOPPED else 1)
