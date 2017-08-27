import threading
import datetime
from enum import Enum
from .transports import TransportError


class JobStatus(Enum):
    NONE = "none"
    QUEUED = "queued"
    PRINTING = "printing"
    DONE = "done"
    CANCELLED = "cancelled"
    ERROR = "error"


class Printer(object):
    """
    Represents a printer object.

    This base class implements the job queueing.
    """
    def __init__(self):
        self._jobs = []
        self._completed_jobs = []
        self.queue_lock = threading.RLock()
        self._worker_thread = None
        self._work_available_event = threading.Event()
        self._label_types = {}
        self._next_job_id = 1

    @property
    def label_types(self):
        return self._label_types

    def add_label_type(self, label_type):
        self._label_types[label_type.id] = label_type

    def add_job(self, job):
        if not job:
            raise ValueError("No job specified")
        with self.queue_lock:
            if job not in self._jobs:
                self._assign_job_id(job)
                job.status = JobStatus.QUEUED
                job.printer = self
                self._jobs.append(job)
        self._work_available_event.set()

    def cancel_job(self, job):
        self.finish_job(job, status=JobStatus.CANCELLED)

    def finish_job(self, job, status=JobStatus.DONE):
        with self.queue_lock:
            if job in self._jobs:
                job.status = status
                self._jobs.remove(job)
                self._completed_jobs.append(job)

    def top_job(self):
        """
        Get the top job from the print queue, or None if the queue is empty.

        This won't pop it from the queue, as it's desirable for the job
        currently being processed to stay in the queue.
        """
        with self.queue_lock:
            job = self._jobs[0] if self._jobs else None
            return job

    def jobs(self):
        with self.queue_lock:
            return list(self._jobs)

    def _assign_job_id(self, job):
        job.id = self._next_job_id
        self._next_job_id += 1

    def print(self, job):
        """
        Print a job now.

        Usually this method will be called by the server worker thread.
        """
        raise NotImplementedError()

    def start(self):
        """
        Start an instance of the printer driver.

        This starts up a worker thread and will take jobs from the print queue
        calling the `print` method on each job.
        """
        if self._worker_thread and self._worker_thread.is_alive():
            raise Exception("Print server already running")

        self._worker_thread = threading.Thread(target=self._run_printer_thread, daemon=True)
        self._worker_thread.start()

    def _run_printer_thread(self):
        while True:
            job = self.top_job()
            if not job:
                self._work_available_event.clear()
                self._work_available_event.wait(timeout=2)
                continue
            job.status = JobStatus.PRINTING
            try:
                self.print(job)
            except Exception as e:
                self.finish_job(job, status=JobStatus.ERROR)
                print("Exception:", e)  #TODO
            else:
                self.finish_job(job, status=JobStatus.DONE)


    def stop(self):
        """
        Stop a running instance of the printer driver.

        By default, this method is a no-op, but this may be called when the
        program is shutting down to tidily close any resources used.
        """
        # TODO: shut down server thread gracefully.
        pass

    @classmethod
    def create(cls, id, printer_def):
        """
        Load a printer from a config dict.
        """
        raise NotImplementedError()


class LabelType(object):
    def __init__(self, id, name, label_template, schema):
        self.id = id
        self.name = name
        self.label_template = label_template
        self.schema = schema

    def prepare(self, label_data):
        """
        Prepares a job for printing.

        This method should create an instance of this label type from the
        supplied label data and return a Job object
        """
        prepared_data = self.schema.load(label_data).data if self.schema else label_data
        compiled_label = self.label_template % prepared_data
        return Job(compiled_label)


class Job(object):
    """
    A job submitted to a printer.
    """
    def __init__(self, data):
        self.id = None
        self.printer = None
        self.creation_time = datetime.datetime.now()
        self.status = JobStatus.NONE
        self.data = data

    def cancel(self):
        if self.printer:
            self.printer.cancel_job(self)
