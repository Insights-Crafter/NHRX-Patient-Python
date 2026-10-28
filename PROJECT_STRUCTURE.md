# Project structure

The backend is organized by domain. Patient, Doctor, and Hospital code each has its own models, schemas, repositories, services, and routes. Appointment handling is kept in a separate shared domain because it connects patients and doctors.

```text
app/
|-- Patient/
|   |-- models/
|   |-- repositories/
|   |-- routes/
|   |-- schemas/
|   `-- services/
|-- Doctor/
|   |-- models/
|   |-- repositories/
|   |-- routes/
|   |-- schemas/
|   `-- services/
|-- Hospital/
|   |-- models/
|   |-- repositories/
|   |-- routes/
|   |-- schemas/
|   `-- services/
|-- appointments/
|   |-- models/
|   |-- repositories/
|   |-- routes/
|   |-- schemas/
|   `-- services/
|-- database/
|-- JWT/
|-- utilityfunctions/
`-- main.py
```

`database`, `JWT`, and `utilityfunctions` contain infrastructure used across domains. `app/main.py` assembles the domain routers and imports each domain model package so SQLAlchemy registers all models. Route handlers call domain services directly. Existing HTTP paths and request/response behavior are unchanged.
