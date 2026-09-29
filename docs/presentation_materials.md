# TrustLens PowerPoint Presentation & Visual Diagrams

This guide compiles presentation outlines and UML diagrams to help demonstrate the TrustLens architecture, system components, database schemas, and processes.

---

## 1. PowerPoint Presentation Outline

*   **Slide 1: Title Slide**
    *   **Header**: TrustLens: Intelligent Webpage Manipulation and Dark Pattern Detection
    *   **Footer**: Academic Final-Year Project Presentation
    *   **Content**: Project Scope, Author Details, Technical Supervisors.
*   **Slide 2: The Problem Statement**
    *   **Header**: The Rise of Deceptive Web UI (Dark Patterns)
    *   **Points**:
        *   Standard consumers are constantly exposed to artificial urgency and scarcity traps.
        *   Privacy terms are intentionally long and complex, obscuring third-party tracking.
        *   Existing security software detects malware but ignores psychological manipulation.
*   **Slide 3: Project Objectives**
    *   **Header**: TrustLens Objectives
    *   **Points**:
        *   Develop Manifest V3 extension providing real-time local and cloud scan diagnostics.
        *   Combine rule-based Lexical analysis with Machine Learning (Logistic Regression & MLP Classifier).
        *   Generate human-readable explanations (XAI) and summarize privacy terms.
        *   Provide system alerts for suspicious and blacklisted sites.
*   **Slide 4: System Architecture**
    *   **Header**: Dual-Engine (Hybrid) System Architecture
    *   **Content**: Explain Local vs Cloud vs Hybrid settings, and data flows between content scripts, service workers, FastAPI, and SQLAlchemy databases.
*   **Slide 5: Machine Learning and Model Tuning**
    *   **Header**: AI Classifier & Evaluation Results
    *   **Points**:
        *   Logistic Regression & MLP Classifier comparison.
        *   Evaluation metrics: 100% accuracy on standard tests with zero False Positives.
        *   Dynamic resource tracking: Latency (0.002ms) and Memory footprints.
*   **Slide 6: Explainable AI & Privacy Highlights**
    *   **Header**: Transparency & Trust Focus
    *   **Points**:
        *   Feature attribution: top 5 keywords contributing to risk classification.
        *   Rule-based sentence extraction summarizing cookie sharing, data retention, and user rights.
*   **Slide 7: Admin Analytics Panel**
    *   **Header**: Central Security Console
    *   **Points**:
        *   Aggregated scan histories, average risk rating, blacklist statuses, and top dark patterns.
*   **Slide 8: Conclusion & Future Scope**
    *   **Header**: Conclusion
    *   **Points**: Integrate real WHOIS lookup endpoints and support ONNX web browser model execution.

---

## 2. Mermaid Visual UML Diagrams

### A. System Architecture Flowchart
```mermaid
graph TD
    subgraph "Chrome Client Extension"
        CS["Content Script (riskAnalyzer.ts)"]
        SW["Background Service Worker (serviceWorker.ts)"]
        UI["Popup App View (App.tsx)"]
    end

    subgraph "FastAPI Server Stack"
        API["REST Router (endpoints.py)"]
        Rules["Rule Engine (rules_service.py)"]
        ML["AI Engine (ml_service.py)"]
        SUM["Privacy Summarizer (privacy_summarizer.py)"]
        REP["Reputation Engine (reputation_service.py)"]
    end

    subgraph "Storage Layer"
        DB[("SQL Database (SQLite/PostgreSQL)")]
    end

    CS -->|1. Scrape text| UI
    UI -->|2. Send request| API
    SW -.->|Background check| API
    API --> Rules
    API --> ML
    API --> SUM
    API --> REP
    API -->|Save records| DB
```

### B. Use Case Diagram
```mermaid
usecaseDiagram
    actor User as "Extension User"
    actor Admin as "System Administrator"

    User --> (Scan Active Webpage)
    User --> (Toggle Background Scanning)
    User --> (Change Active AI Model)
    User --> (View Privacy Summary)
    User --> (View Trust Score & Reputation)
    User --> (Submit Classification Feedback)

    Admin --> (View Admin Dashboard)
    Admin --> (Inspect Scan Metrics & Charts)
    Admin --> (Review User Feedback Logs)
    Admin --> (Manage Blacklisted Domains)
```

### C. Sequence Diagram (Page Scan Loop)
```mermaid
sequenceDiagram
    autonumber
    actor User as Extension User
    participant App as Popup View (App.tsx)
    participant CS as Content Script (riskAnalyzer.ts)
    participant Backend as FastAPI Server
    participant DB as SQLite/PostgreSQL

    User->>App: Clicks "Scan Webpage"
    App->>CS: Message "SCAN_PAGE"
    CS->>CS: Normalize text & run local rules
    CS-->>App: Return local score & raw text
    App->>Backend: POST /api/scan (Text, activeModel)
    Backend->>Backend: Execute active ML model (LR/MLP)
    Backend->>Backend: Calculate reputation & privacy summary
    Backend->>DB: Log scan history
    DB-->>Backend: Return scanId
    Backend-->>App: Return unified trust score, XAI & privacy summary
    App-->>User: Render visual tabs, alerts, and badges
```

### D. Data Flow Diagram (DFD) Level 0
```mermaid
graph LR
    User["Extension User"]
    System["TrustLens System"]
    Admin["System Administrator"]

    User -->|Webpage text & feedback| System
    System -->|Trust scores, XAI warnings, privacy summaries| User
    Admin -->|Configuration & blacklists| System
    System -->|Aggregated metrics & logs| Admin
```

### E. Data Flow Diagram (DFD) Level 1
```mermaid
graph TD
    User["Extension User"]
    Admin["System Administrator"]
    
    P1["1. Text Preprocessing & Parsing"]
    P2["2. Lexical Rule Matching"]
    P3["3. AI Classification (LR/MLP)"]
    P4["4. Privacy Policy Summarizer"]
    P5["5. Website Reputation check"]
    P6["6. Combined Score Assembly"]
    P7["7. Feedback logging & Analytics"]
    
    DS1[("Scan History Store")]
    DS2[("Feedback Database")]
    
    User -->|Raw text| P1
    P1 -->|Clean tokens| P2
    P1 -->|Clean tokens| P3
    P1 -->|Full text| P4
    P1 -->|Domain URL| P5
    
    P2 -->|Rule weight matrix| P6
    P3 -->|ML probabilities & XAI features| P6
    P4 -->|Summarized sections| P6
    P5 -->|Reputation ratings| P6
    
    P6 -->|Unified report| User
    
    User -->|Submit rating| P7
    P7 -->|Insert feedback| DS2
    P6 -->|Log scan history| DS1
    
    DS1 -->|Metric tables| Admin
    DS2 -->|Audit reports| Admin
```

### F. Entity-Relationship Diagram (ERD)
```mermaid
erDiagram
    USERS {
        int id PK
        string user_id UK
        string email
        boolean privacy_mode
        datetime created_at
    }
    SCAN_HISTORY {
        int scan_id PK
        string user_id FK
        string url_hash
        string domain
        string page_title
        int rule_score
        int ml_score
        int final_score
        string risk_label
        string matched_keywords_json
        string page_text
        datetime timestamp
    }
    FEEDBACK {
        int id PK
        int scan_id FK
        string feedback_type
        string comment
        datetime created_at
    }
    MODEL_INFO {
        int id PK
        string version UK
        float accuracy
        float precision
        float recall
        float f1_score
        string trained_date
        datetime created_at
    }

    USERS ||--o{ SCAN_HISTORY : "initiates"
    SCAN_HISTORY ||--o| FEEDBACK : "attaches"
```

### G. Class Diagram (Backend API architecture)
```mermaid
classDiagram
    class Base {
        +metadata
    }
    class User {
        +int id
        +string user_id
        +string email
        +boolean privacy_mode
        +datetime created_at
    }
    class ScanHistory {
        +int scan_id
        +string user_id
        +string url_hash
        +string domain
        +string page_title
        +int rule_score
        +int ml_score
        +int final_score
        +string risk_label
        +string matched_keywords_json
        +string page_text
        +datetime timestamp
    }
    class Feedback {
        +int id
        +int scan_id
        +string feedback_type
        +string comment
        +datetime created_at
    }
    
    class RulesService {
        +analyze_text_rules(visible_text)
    }
    class MLService {
        +load_models()
        +predict_webpage_ml(page_text, active_model_type)
        +preprocess_text(text)
    }
    class PrivacySummarizer {
        +detect_privacy_policy(url, title, text)
        +summarize_privacy_policy(text)
    }
    class ReputationService {
        +evaluate_website_reputation(url)
        +calculate_unified_trust_score(scan_risk_score, reputation_data)
    }

    Base <|-- User
    Base <|-- ScanHistory
    Base <|-- Feedback
    ScanHistory "1" *-- "0..1" Feedback
```

### H. Component Diagram
```mermaid
graph LR
    subgraph "User Interface Component"
        Popup["React Popup Module"]
        Dashboard["React Admin Dashboard"]
    end
    
    subgraph "Background Agent Component"
        Worker["Background Service Worker"]
    end
    
    subgraph "Core Business Component"
        API["FastAPI App Router"]
        Rules["Rules Evaluator Component"]
        ML["AI Engine (LR / MLP neural net)"]
        Privacy["Privacy Extractor Component"]
        Rep["Reputation Auditor Component"]
    end
    
    subgraph "System Database Component"
        DB["SQL Database Engine"]
    end

    Popup -->|Scan payload| API
    Dashboard -->|Query metrics| API
    Worker -->|Silent verify| API
    API --> Rules
    API --> ML
    API --> Privacy
    API --> Rep
    API -->|Write data| DB
```

### I. Deployment Diagram
```mermaid
graph TD
    subgraph "Client Computer Node"
        subgraph "Chrome Web Browser Instance"
            Ext["TrustLens Manifest V3 Extension"]
        end
    end

    subgraph "Docker Deployment Server Node"
        subgraph "Docker Compose Mesh"
            Backend["FastAPI Container (Port 8000)"]
            DB["PostgreSQL Container (Port 5432)"]
        end
    end

    Ext -->|HTTP REST JSON over HTTPS| Backend
    Backend -->|SQL DB Connections| DB
```
