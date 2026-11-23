# FinDocAI: System Architecture, Data Flow & Module Design

**Course:** CSET400C Capstone Project, Milestone-2  
**Group ID:** G382 | **SDG Focus:** SDG 9 (Primary), SDG 8 (Secondary)  
**Authors:** Harsh Shukla (`E23CSEU0003`) & Akshita Singh (`E23CSEU0030`)

---

## 1. System Architecture Diagram

```mermaid
flowchart TD
    User["Human Reviewer / Financial Analyst"]
    
    subgraph UI_Layer["Presentation Layer"]
        StreamlitApp["Streamlit Dashboard (app/main.py)"]
        DemoTriggers["One-Click Demo Triggers"]
        DataEditor["Interactive Correction Editor (st.data_editor)"]
    end
    
    subgraph API_Layer["API & Service Layer"]
        FastAPIServer["FastAPI Server (findoc/api/app.py)"]
        Endpoints["REST Endpoints: /upload, /documents, /corrections, /export"]
    end

    subgraph Pipeline_Layer["FinDoc Core Pipeline"]
        Ingest["Ingestion Engine (PyMuPDF & Tesseract OCR)"]
        Classify["Dual Classifier (Keyword Rules & TF-IDF ML)"]
        Extract["Information Extractor (Regex & Positional Anchors)"]
        Validate["Validation Engine (10 Explicit Arithmetic & Regulatory Rules)"]
        FlagsEngine["Review Priority Engine (Weighted Indicators & Flags)"]
    end
    
    subgraph Storage_Layer["Storage & Privacy Layer"]
        SQLiteDB["SQLite Database (data/findoc.db)"]
        PrivacyGuard["PII Masking & Privacy Guard (PAN/Aadhaar/Account)"]
        AuditLog["Audit History of Human Corrections"]
    end

    User --> StreamlitApp
    StreamlitApp --> FastAPIServer
    StreamlitApp --> DemoTriggers
    StreamlitApp --> DataEditor
    
    FastAPIServer --> Ingest
    Ingest --> Classify
    Classify --> Extract
    Extract --> Validate
    Validate --> FlagsEngine
    
    FlagsEngine --> PrivacyGuard
    PrivacyGuard --> SQLiteDB
    SQLiteDB --> AuditLog
    SQLiteDB --> StreamlitApp
```

---

## 2. Data Flow Diagram Level 0 (Context Diagram)

```mermaid
flowchart LR
    Reviewer["Financial Reviewer / Auditor"]
    System["FinDocAI Processing Core"]
    Database["Local Secure SQLite Store"]
    
    Reviewer -->|"Submits PDF Document or Scanned Image"| System
    Reviewer -->|"Submits Field Corrections"| System
    System -->|"Outputs Extracted Tables, Validation Flags & Review Priority"| Reviewer
    System -->|"Exports Normalized JSON / Audit CSV"| Reviewer
    
    System -->|"Stores Masked Extracted Data & Audit Trails"| Database
    Database -->|"Retrieves Document History & Corrections"| System
```

---

## 3. Data Flow Diagram Level 1 (Pipeline Decomposition)

```mermaid
flowchart TD
    DocInput["Uploaded PDF / Scanned Image"] --> P1["1. Ingestion & Format Detection"]
    
    P1 -->|"Digital Vector Stream"| TextStream["Extracted Text & Plumber Tables"]
    P1 -->|"Raster Image Stream"| OCR["Tesseract OCR Fallback"]
    OCR --> TextStream
    
    TextStream --> P2["2. Document Type Classification"]
    P2 -->|"Keyword Heuristic Rules"| ClsDecision["Consensus Classifier"]
    P2 -->|"TF-IDF + Logistic Regression"| ClsDecision
    
    ClsDecision --> P3["3. Normalized Schema Extraction"]
    P3 -->|"Normalized JSON + Field Confidences"| P4["4. Rule-Based Validation Engine"]
    
    P4 -->|"Arithmetic & Format Check Results"| P5["5. Review Priority & Flags Engine"]
    
    P5 --> P6["6. Storage, Privacy Masking & Audit Trail"]
    P6 --> DB[(SQLite Database)]
    
    P5 --> P7["7. Human Review & Correction Workflow"]
    P7 -->|"Human Correction Trigger"| P4
    P7 --> Export["Export Audited JSON / CSV"]
```

---

## 4. Use Case Diagram

```mermaid
flowchart TD
    Analyst(("Financial Analyst"))
    Supervisor(("Compliance Supervisor"))
    
    subgraph FinDocAI_UseCases["FinDocAI Use Case Boundaries"]
        UC1["Upload Financial Document (PDF/Image)"]
        UC2["Inspect Document Type & Model Agreement"]
        UC3["Examine Rule Failures with Plain-English Reasons"]
        UC4["Review High/Medium Priority Transaction Flags"]
        UC5["Correct Extracted Field & Trigger Re-Validation"]
        UC6["Export Normalized Financial JSON & CSV"]
        UC7["Permanently Delete Document (Privacy Right)"]
        UC8["Inspect Historical Audit Logs"]
    end
    
    Analyst --> UC1
    Analyst --> UC2
    Analyst --> UC3
    Analyst --> UC4
    Analyst --> UC5
    Analyst --> UC6
    
    Supervisor --> UC4
    Supervisor --> UC7
    Supervisor --> UC8
```

---

## 5. Sequence Diagram: Document Processing & Human-in-the-Loop Re-Validation

```mermaid
sequenceDiagram
    autonumber
    actor Reviewer as Human Reviewer
    participant UI as Streamlit UI / REST API
    participant Ingest as Ingestion & OCR Engine
    participant Classify as Dual Classifier
    participant Extract as Schema Extractor
    participant Validate as Validation Engine
    participant Flags as Review Priority Engine
    participant DB as SQLite Storage

    Reviewer->>UI: Uploads bank statement (PDF)
    UI->>Ingest: extract_text_and_tables(file_path)
    Ingest-->>UI: Extracted text, tables, digital status
    UI->>Classify: classify_document(text)
    Classify-->>UI: Type: bank_statement (Rules: 100%, ML: 100%)
    UI->>Extract: extract_document(type, parsed_doc)
    Extract-->>UI: Normalized data + field confidences
    UI->>Validate: validate_document(extracted_data)
    Validate-->>UI: Validation report (e.g. VAL_BNK_REC: FAIL)
    UI->>Flags: evaluate_review_priority(extracted_data, validation)
    Flags-->>UI: Review Priority: HIGH (Score: 65, Contributing flags)
    UI->>DB: save_processed_document(...)
    UI-->>Reviewer: Displays Red FAIL, High Review Priority, & Reason
    
    Note over Reviewer, UI: Human-in-the-Loop Correction Cycle
    Reviewer->>UI: Corrects closing balance to INR 55,000.00
    UI->>DB: record_field_correction(doc_id, closing_balance, 55000.0)
    UI->>Validate: validate_document(corrected_data)
    Validate-->>UI: Re-validation report: PASS
    UI->>Flags: evaluate_review_priority(corrected_data, re_validation)
    Flags-->>UI: Review Priority drops to LOW (Score: 0)
    UI->>DB: save_processed_document(status='CORRECTED')
    UI-->>Reviewer: Updates badge to Green PASS, Low Priority
```

---

## 6. Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    DOCUMENTS ||--|| EXTRACTED_DATA : "has structured"
    DOCUMENTS ||--|| VALIDATIONS : "evaluated by"
    DOCUMENTS ||--|| REVIEW_FLAGS : "scored with"
    DOCUMENTS ||--o{ CORRECTIONS : "audited by"

    DOCUMENTS {
        string doc_id PK
        string file_name
        string doc_type
        boolean is_scanned
        string processing_status
        string error_message
        timestamp created_at
        timestamp updated_at
    }

    EXTRACTED_DATA {
        string doc_id PK, FK
        text data_json
        text confidences_json
        timestamp extracted_at
    }

    VALIDATIONS {
        string doc_id PK, FK
        string overall_status
        int passed_count
        int failed_count
        text rules_json
        timestamp validated_at
    }

    REVIEW_FLAGS {
        string doc_id PK, FK
        string review_priority
        int priority_score
        text flags_json
        string disclaimer
        timestamp flagged_at
    }

    CORRECTIONS {
        int id PK
        string doc_id FK
        string field_name
        string old_value
        string new_value
        string corrected_by
        timestamp corrected_at
    }
```

---

## 7. Modular Design Architecture

The FinDocAI codebase is architected into single-responsibility, highly decoupled modules:

```
src/findoc/
├── ingest/
│   ├── pdf_parser.py          # PyMuPDF fast digital parsing + pdfplumber tables
│   └── ocr_engine.py          # Tesseract OCR wrapper with graceful failure handling
├── classify/
│   ├── rule_classifier.py     # Keyword heuristic baseline
│   ├── ml_classifier.py       # TF-IDF + Logistic Regression ML classifier
│   └── classifier_service.py  # Dual-model consensus dispatcher
├── extract/
│   ├── schemas.py             # Pydantic normalized schemas, normalizers, PII maskers
│   ├── bank_statement_extractor.py # Bank statements, balances, transaction tables
│   ├── invoice_extractor.py   # Invoices, GSTINs, line items, subtotals, GST
│   ├── kyc_extractor.py       # PAN and Aadhaar identity card extractors
│   └── extractor_service.py   # Routing dispatcher
├── validate/
│   ├── rules.py               # 10 explicit rules returning rule IDs and reasons
│   └── validator.py           # Complete validation suite runner
├── flags/
│   ├── rules.py               # Outlier, duplicate, bounced, cash withdrawal flags
│   └── engine.py              # Review Priority (Low/Med/High) weighted aggregator
├── storage/
│   ├── db.py                  # SQLite CRUD with foreign keys & audit logging
│   └── privacy.py             # Data sanitization, PII masking, deletion
└── api/
    └── app.py                 # FastAPI REST API
```
