# Take Home Exercise

## TODO:

* [ ] Consume RabbitMQ extract_requests
  * [ ] Exchange: "extract_requests", Type: "Topic", Routing Keys: ["usa", "nhgis"]
  * [ ] Bind new queue(s) to "extract_requests"
* [ ] Create Database for storing RabbitMQ messages
  * [ ] Try out MongoDB? Seems like one extract == one document makes sense...
  * [ ] Could just do SQLight since, well I've actually used it before.
  * [ ] Come up with model.
* [ ] Reports API server
  * [ ] Flask
  * [ ] Mimic example report
