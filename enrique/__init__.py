import sys
import threading
import json
import imp
from importlib import import_module

import mesos.interface
import mesos.native
from mesos.interface import mesos_pb2

from pyrallelsa import group_runner
from pyrallelsa import ProblemClassPath
from pyrallelsa import Solution


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
            problem_name = task_data['name']
            task_command = task_data['command']
            problem_data = task_data['problem_data']


            sys.path.append("/home/vagrant/{0}".format(problem_name))
            pccls_module = import_module("problem")
            PCCls = getattr(pccls_module, "Problem")
            pcp = ProblemClassPath("problem", "Problem")

            if task_command == 'divisions':
                task_divisions = task_data['divisions']
                res = list(PCCls.divide(
                    divisions=task_divisions,
                    problem_data=problem_data
                ))
                res_data = {
                    "divisions": res
                }
            elif task_command == 'anneal':
                minutes_per_division = task_data['minutes_per_division']
                sstates = task_data['sstates']
                solutions = group_runner((uid, pcp, sstates,
                                         minutes_per_division,
                                    problem_data, None))
                winner = sorted(
                    (solution for solution in solutions),
                    key=lambda s: s.energy
                )[0]
                res_data = {
                    "best_location": winner.state,
                    "fitness_score": winner.energy
                }
            else:
                raise ValueError("Invalid task_command {}".format(task_command))

            update = mesos_pb2.TaskStatus()
            update.task_id.value = task.task_id.value
            update.state = mesos_pb2.TASK_FINISHED
            update.data = json.dumps(dict(
                uid=uid
                **res_data
            ))
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
