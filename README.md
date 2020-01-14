# Take Home Exercise

## Requires:
* Docker
* virtualenv, or some other python environment manager (or just install stuff globally, see if I care)

## How to run:
1. _[Optional]_ Create a virtual environment here with `virtualenv venv`
2. _[Optional]_ Activate your virtual environment with `source venv/bin/activate`
3. Install python requirements with `pip install -r requirements`
4. Start up the mongodb docker container with `docker run -d -p 27017:27017 --name db mongo`
5. Start program with `python report.py`
    * This program starts by removing any existing 'extract_requests' database.
    * It then starts the RabbitMQ client to listen for messages
    * I then send a random number of randomly configured extract requests to the
      nhgis and usa endpoints to put some data in the database.
    * A first report is run and printed to the screen, but hte client remains running,
      ready to recieve any more extract requests for storing.
    * You can get the json extract report payload from to http://0.0.0.0:5000/report.json
6. Stop program with a Ctrl-C
7. Stop the MongoDB with `docker stop db` (you can restart it with `docker start db`)

## Closing thoughts:

I definitely chased a few rabbits a bit too far down the hole during this exercise, but
overall I really liked learning about these new-to-me tools. This exercise include my:
* First Flask app
* First experience with NoSQL databases
    - I completely rewrote my data model a few times while trying to get my head around
      how querying NoSQL databases works. I mostly flexed the ease of adding references
      within documents to make the final report a breeze, but I've included some of my
      thoughts in `data_model.py` on how things may need to change or could be improved
      as I get a better understading of how MongoDB works.
    - I chose to use MongEngine as an object data mapper because I liked the feel of the
      API. It used `pymongo`under the hood, but as I was struggling with some details it
      seems like I should start by learning pymongo first to get a better understanding
      of the actual interactions with the database.
* First experience with RabbitMQ
    - This was where I started and it came together pretty slick. I was trying to get a
      little fancy with some ideas about "oh we can just spin up more clients if there
      is a bunch more demand!", but then realized that since the exchange was a
      Publisher/Subscriber model this would just result in more copies of the same info.
      Reading about RabbitMQ and message brokers was super intersting.
* First experience with Docker
    - Ultimately, I wasn't able to get my solution to this exercise containerized, but
      this is clearly a skill that would benefit me. I got everything working except I
      couldn't get the `exercism` container to connect with the mongodb container. I
      feel like it most be something dead simple, and I tried a number of "fixes" to no
      avail.
There is a lot of room for improvement here. There is a lot of redundant querying and
general database interaction. Loading the sample_variables.csv into the database
multiple times results in... well a mess. But I'm happy with where I've ended and
I look forward to talking about my work further.



## TODO:

* [X] Set up conda environment: jg-ex
  * [X] Requires:
    * pika [RabbitMQ lib]
    * flask [creating reports API]
    * mongoengine [If I get ambitions and use MongoDB]
    * sqlite [lightweight DB for extract_requests]
    * jupyter [So this kernel can run in jupyter]
* [X] Add new kernel for jupyterlab fun.
* [X] Consume RabbitMQ extract_requests
  * [X] Exchange: "extract_requests", Type: "Topic", Routing Keys: ["usa", "nhgis"]
  * [X] Bind new queue(s) to "extract_requests"
  * [X] Make it a script
* [X] Create Database for storing RabbitMQ messages
  * [X] Try out MongoDB? Seems like one extract == one document makes sense...
  * ~~[ ] Could just do SQLite since, well I've actually used it before.~~
  * [X] Come up with model.
* [X] Generate report.
* [X] Reports API server
  * [X] Flask
  * [X] Mimic example report
* [ ] Docker-eyes
  * [X] pip requirements
  * [-] also start up mongodb docker container
    - Failing to connect to mongodb from app container
  * [X] run the report.py
  * [ ] Make it a real webapp
