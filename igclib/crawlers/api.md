## Requests

```
GET api/calendar/<year>     
GET api/events/<event_id>     
GET api/tasks/<task_id>     
GET api/flights/<task_id>   
``` 

or

```
GET api/calendar?year=<year>
GET api/events?event=<event_id>
GET api/tasks?task=<task_id>  
GET api/flights?task=<task_id>
```

## Responses

```
GET api/calendar/2018

[
    {
        "id": NUMBER, 
        "name": STRING, 
        "date": STRING
    },
    {
        "id": 3642, 
        "name": "Les Saisies (Signal de Bisanne)", 
        "date": "21/04/18"
    }, 
    ...
]
```

```
GET api/events/3642

[
    {
        "id": NUMBER,
        "day" : NUMBER
    },
    {
        "id": 1547,
        "day" : 2
    },
]
```

```
GET api/tasks/1547

format task ?
```

```
GET api/flights/1547

zip file with all igc tracks of task 1547
```