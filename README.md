# Fever code challenge

In my opinion, there are two problems to address in this code challenge. The first would be the management of supplier data and the second the API service to provide the information to potential customers.
This separation of entities or systems is based on a number of factors set out in the description of the exercise, namely:
1. The third-party provider's service may fail, become slow, or even be disabled.
2. The internal search service must be able to search for events regardless of the state of possible external services.
3. The internal search service must be efficient and be able to handle a high volume of requests.

## External Providers Collector

This system will be a self-managed service that will run autonomously. Its purpose will be to collect the data from the different providers and store theirs data in the final event database.

The complete orchestration will be managed by the two components of the system: the scheduler and the job processor.

### Scheduler
The operation of the scheduler is based on the use of jobs, these jobs will be the basic work units to obtain data from external providers. Jobs can be scheduled, executed and tracked. The role of the scheculder is to track which jobs need to be processed and execute those that meet the conditions for execution.

The jobs can be programmed/scheduled so that the obtaining of the supplier's data can be configured to occur every x time, likewise it allows creating a monitoring system for said jobs. This monitoring system will allow us to detect problems in the provider's external system as well as other possible failures that occur during the data collection process.

### Job Processor
This process will be in charge of executing a job.

Each job, at a certain time, will be in a state:

- **Pending**. Every time a new job is created, it will be created with a this status.
- **Running**. The system is currently getting the data from the supplier.
- **Completed**. The data collection process has been satisfactory.
- **Failed**. An error occurred in data collection.

Every time a job is created, a job outcome record will be generated in the system. This record will give us with information related to the job, e.g. status, when it was processed as well as, if an error occurred, information about said error (message and type of error).

Since each job can be a data collection task for different providers, the job processor will be in charge of invoking the appropriate collector to the provider as well as processing the result of data collection from the provider, indicating the result of said operation in your job outcome.

Needless to say, the execution of these jobs could be parallelized by executing several jobs concurrently.

As a result, we will get the data collected from the clients into a Postgresql or AWS Aurora database system.

Note: The major drawback of this approach is the delay that can occur between the provider's data and the data in our side. This problem can be minimized by increasing the frequency gathering the data from the providers to low values; however, it is a problem to consider before implementing a definitive solution.


# APISearch
Once our provider's data is in our database, implementing the query API for said data will consist of a single endpoint that will allow us to retrieve those events that meet certain conditions by consulting our database. In our case, they will be those online type events that are between a defined period of dates.

Depending on the needs and required performance, an in-memory database could be implemented, for example Amazon's MemoryDB, which has good performance.

Regarding the specific implementation, I have to say that working with API's is not my current area of expertise so I have been struggling a little to set everything up and get the API running. The solution implemented does not have anything related to the scheduler and
events processer mentioned before is just a much simpler approach to try to meet the exercise requirements.

To run the app, clone the repo and run Uvicorn running the command from the src/fever folder:

    uvicorn main:app --reload

