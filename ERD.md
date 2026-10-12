# Entity relationship diagram

This diagram reflects the SQLAlchemy models currently in `app/models`. Column names and declared SQLAlchemy types are shown; `PK` and `FK` mark primary and foreign keys.

```mermaid
erDiagram
    Patients {
        INTEGER patientID PK
        TEXT nationalID
        TEXT firstName
        TEXT lastName
        TEXT date_of_birth
        TEXT blood_group
        TEXT gender
        TEXT phone
        TEXT email
        DATE createdAt
    }

    PatientAddress {
        INTEGER AddressID PK
        INTEGER patientID FK
        TEXT Area
        TEXT HouseNumber
        TEXT Province
        TEXT City
        TEXT Street
        TEXT Block
    }

    MedicalRecords {
        INTEGER recordID PK
        INTEGER patientID FK
        INTEGER doctorID
        INTEGER hospitalID
        TIMESTAMP recordDATE
        VARCHAR recordType
        VARCHAR cheif_complaint
        DATE follow_up_date
    }

    ClinicalNotes {
        INTEGER noteID PK
        INTEGER recordID FK
        INTEGER DiagnosisID FK
        VARCHAR Notes
    }

    RecordDiagnosis {
        INTEGER noteID PK
        INTEGER recordID FK
        VARCHAR Diagnosis
        VARCHAR Diagnosisnotes
    }

    Medications {
        INTEGER MedID PK
        VARCHAR MedicineName
        VARCHAR Formula
        VARCHAR Strength
    }

    RecordMedicines {
        INTEGER recordID PK
        INTEGER medicineID FK
        VARCHAR dosage
        VARCHAR frequency
        VARCHAR duration
        INTEGER duration_days
    }

    medical_tests {
        INTEGER test_id PK
        VARCHAR name UK
        TEXT description
    }

    medical_record_tests {
        INTEGER id PK
        INTEGER record_id FK
        INTEGER test_id FK
        DATETIME performed_at
        TEXT result
        VARCHAR status
    }

    symptoms {
        INTEGER symptom_id PK
        VARCHAR name UK
        VARCHAR code
    }

    record_symptoms {
        INTEGER record_symptom_id PK
        INTEGER record_id FK
        INTEGER symptom_id FK
        VARCHAR severity
        INTEGER duration_days
        TEXT notes
    }

    Patients ||--o{ PatientAddress : has
    Patients ||--o{ MedicalRecords : has
    MedicalRecords ||--o{ ClinicalNotes : contains
    MedicalRecords ||--o{ RecordDiagnosis : includes
    Medications ||--o{ RecordMedicines : prescribed_as
    medical_tests ||--o{ medical_record_tests : included_in
    symptoms ||--o{ record_symptoms : recorded_as
```

## Foreign key references that do not resolve to a defined model table

- `ClinicalNotes.DiagnosisID` references `Diagnosis`, but no `Diagnosis` table/model is defined.
- `RecordMedicines.recordID` is a primary key but has no declared foreign key to `MedicalRecords`.
- `medical_record_tests.record_id` references `medical_records.record_id`, while the defined `MedicalRecords` model table is `MedicalRecords` with key `recordID`.
- `record_symptoms.record_id` has the same unresolved `medical_records.record_id` reference.
- `doctorID` and `hospitalID` have no foreign key declarations or corresponding models in the current folder.

The PII columns in `Patients` and address columns in `PatientAddress` are `TEXT`, including `date_of_birth`, to accommodate variable-length encrypted strings.
