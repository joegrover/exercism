# Take Home Exercise

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
* [ ] Reports API server
  * [ ] Flask
  * [ ] Mimic example report
* [ ] Docker-eyes
