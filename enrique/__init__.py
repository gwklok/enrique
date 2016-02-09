import sys
import threading
import json
import imp

import mesos.interface
from mesos.interface import mesos_pb2
import mesos.native


class Enrique(mesos.interface.Executor):
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

            task_data = json.loads(task.data)
            uid = task_data['uid']

            location = task_data['location']
            # Location is serialized
            if not location:
                location = None
            else:
                location = json.loads(location)

            job_data = task_data['job_data']
            task_seconds = task_data['task_seconds']
            task_name = task_data['task_name']

            print "start: uid is: ".format(uid)
            print "start: location is: ".format(location)

            # XXX
            module = imp.load_source(
                task_name,
                '/home/vagrant/{0}/problem.py'.format(task_name)
            )
            annealer = module.Problem(job_data, location)
            auto_schedule = annealer.auto(minutes=task_seconds/60.0)
            annealer.set_schedule(auto_schedule)
            best_key, best_fitness = annealer.anneal()

            print "Best Fitness: {}".format(best_fitness)
            print "Best Key: {}".format(best_key)
            print "end: uid is: ".format(uid)
            print "end: location is: ".format(location)

            update = mesos_pb2.TaskStatus()
            update.task_id.value = task.task_id.value
            update.state = mesos_pb2.TASK_FINISHED
            update.data = json.dumps({
                "uid": uid,
                "best_location": json.dumps(best_key),
                "fitness_score": best_fitness
            })
            driver.sendStatusUpdate(update)

        thread = threading.Thread(target=run_task)
        thread.start()

    def frameworkMessage(self, driver, message):
        # Send it back to the scheduler.
        driver.sendFrameworkMessage(message)


def main():
    print "Starting executor"
    driver = mesos.native.MesosExecutorDriver(Enrique())
    sys.exit(0 if driver.run() == mesos_pb2.DRIVER_STOPPED else 1)
