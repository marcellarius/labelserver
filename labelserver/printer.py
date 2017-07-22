import threading
from enum import Enum


class JobStatus(Enum):
    NONE = "none"
    QUEUED = "queued"
    PRINTING = "printing"
    DONE = "done"
    CANCELLED = "cancelled"


class Printer(object):
    """
    Represents a printer object.

    This base class implements the job queueing.
    """
    def __init__(self):
        self._jobs = []
        self._queue_lock = threading.Lock()

    def label_types(self):
        raise NotImplementedError()

    def add_job(self, job):
        if not job:
            raise ValueError("No job specified")
        with self._queue_lock:
            if job not in self._jobs:
                job.status = JobStatus.QUEUED
                self._jobs.append(job)

    def cancel_job(self, job):
        with self._queue_lock:
            if job in self._jobs:
                job.status = JobStatus.CANCELLED
                self._jobs.remove(job)

    def take_job(self):
        """
        Get the top job from the print queue, or None if the queue is empty
        """
        with self._queue_lock:
            job = self._jobs.pop(0) if self._jobs else None
            if job:
                job.status = JobStatus.PRINTING
            return job

    def start(self):
        """
        Start an instance of the printer driver.

        The exact details of this are left up to the printer driver but it
        may start a worker thread to deal with requests.
        """
        raise NotImplementedError()

    def stop(self):
        """
        Stop a running instance of the printer driver.

        By default, this method is a no-op, but this may be called when the
        program is shutting down to tidily close any resources used.
        """
        pass

    @classmethod
    def load_config(cls, id, printer_def):
        """
        Load a printer from a config dict.
        """
        raise NotImplementedError()


class LabelType(object):
    def prepare(self, label_data):
        """
        Prepares a job for printing.

        This method should create an instance of this label type from the
        supplied label data and return a Job object
        """
        raise NotImplementedError()


class Job(object):
    """
    A job submitted to a printer.

    This base class is extended by a specific printer class to store any
    printer-specific data.
    """
    def __init__(self, printer, label_type):
        self.printer = printer
        self.label_type = label_type
        self.creation_time = datetime.datetime.now()
        self.status = JobStatus.NONE


    def cancel(self):
        self.printer.cancel_job(self)
