**Privacy-Preserving** **AI-Based** **Cheating** **Detection** **in**
**Online** **Exams** **—** **Roadmap**

**Abstract**

A practical, research-grade implementation roadmap to build a
camera-free cheating detection system for online exams. The system uses
behavioral biometrics (keystroke dynamics, hesitation/idle patterns,
navigation/editing behavior) and answer-similarity analysis, fusing them
with machine learning to produce a transparent, privacy-preserving
cheating probability score.

**Table** **of** **Contents**

> 1\. Objectives and Research Questions 2. High-Level Architecture
>
> 3\. Timeline & Milestones (Weeks 1–14) 4. Phase-by-Phase
> Implementation Plan 5. Data Collection & Labeling Protocol 6. Feature
> Engineering (Detailed)
>
> 7\. Modeling Strategy
>
> 8\. Real-time Inference & Integration 9. Evaluation, Ablation &
> Experiments
>
> 10\. Ethics, Privacy & Legal Considerations 11. Deployment &
> Monitoring
>
> 12\. Deliverables Checklist 13. Suggested Paper Outline
>
> 14\. Appendix: Code Snippets & API Examples

**1.Objectives** **and** **Research** **Questions**

**Primary** **objective:** Build a camera-free, privacy-first system
that detects cheating during online exams by analyzing behavioral
signals and semantic similarity of answers.

**Research** **questions:** - Can behavioral signals (typing rhythm,
hesitation, navigation, editing) reliably indicate cheating without
cameras? - Does adding answer-similarity (semantic + structural) improve
detection performance and reduce false positives? - Which fusion
approach (rule-based vs learned) yields best accuracy while remaining
explainable?

**2.High-Level** **Architecture**

> • **Frontend** **(Exam** **Client):** React-based exam UI that logs
> events (keydown/keyup, focus/blur, paste, clipboard, edits), buffers
> locally, and uploads securely.
>
> • **Backend** **API:** FastAPI service for receiving logs, storing raw
> events, and returning inference results.
>
> 1
>
> • **Processing** **Pipeline:** Real-time & batch feature extractor
> (Python), feature store (Postgres/ Mongo), and model-serving layer.
>
> • **AI** **Models:** (a) Behavioral anomaly models, (b)
> Answer-similarity detector, (c) Fusion decision model.
>
> • **Dashboard:** Admin UI for reviewing flagged attempts, visual
> timeline of events, and exporting reports.

**3.Timeline** **&** **Milestones** **(Weeks** **1–14)**

> • **Week** **1** **(Phase** **0):** Research framing, finalize title,
> metrics, and baseline literature table. • **Week** **2** **(Phase**
> **1):** System design, diagrams, data schema, API contract.
>
> • **Weeks** **3–4** **(Phase** **2):** Frontend logging implementation
> and secure upload.
>
> • **Weeks** **5–6** **(Phase** **3):** Backend logging, storage, and
> feature engineering code. • **Week** **7** **(Phase** **4):**
> Controlled dataset creation and labeling.
>
> • **Weeks** **8–9** **(Phase** **5):** Model training and validation
> (behavioral & similarity models). • **Week** **10** **(Phase** **6):**
> Integration, real-time inference, and dashboard.
>
> • **Weeks** **11–12** **(Phase** **7):** Evaluation, ablation studies,
> robustness tests. • **Weeks** **13–14** **(Phase** **8):** Paper
> writing, polishing, artifact packaging.

**4.Phase-by-Phase** **Implementation** **Plan** **Phase** **0** **—**
**Research** **Framing** **(Week** **1)**

> • Deliverables: 1–2 page proposal, finalized metrics
> (precision/recall/F1/ROC/FPR), success criteria, short related-work
> table.

**Phase** **1** **—** **System** **Design** **(Week** **2)**

> • Create architecture diagram.
>
> • Define data model: raw events, feature vectors, session metadata.
>
> • Define endpoints: /upload_events , /extract_features , /infer ,
> /admin/flag .

**Phase** **2** **—** **Frontend** **Behavioral** **Data** **Capture**
**(Weeks** **3–4)**

> • Implement React UI question component that:
>
> • Captures keydown / keyup with timestamps and key codes. • Detects
> paste via onPaste and captures clipboard-length. • Monitors focus /
> blur events and visibilitychange .
>
> • Tracks edit events (insert, delete count) and submission events. •
> Buffers events locally and POSTs every 3–5s via HTTPS.
>
> • Security: Include session token and HMAC of batch payload.

**Phase** **3** **—** **Backend** **Logging** **&** **Feature**
**Engineering** **(Weeks** **5–6)**

> • Implement FastAPI receiver and persistent storage (Postgres for
> relational metadata + time-series log table; or MongoDB for
> flexibility).
>
> • Implement feature extractor module (Python). Unit-test feature
> outputs against synthetic logs. • Export per-question, per-student
> feature vectors as Parquet/CSV.
>
> 2

**Phase** **4** **—** **Dataset** **Creation** **&** **Labeling**
**(Week** **7)**

> • Design experiments for honest vs cheating sessions.
>
> • Recruit participants or run controlled sessions (simulate multiple
> cheating modes: copying, phone-lookup, collusion, AI-assisted typing).
>
> • Label each session with ground truth and annotate event ranges that
> are suspicious.

**Phase** **5** **—** **Model** **Development** **(Weeks** **8–9)**

> • Behavioral Anomaly Models:
>
> • IsolationForest / One-Class SVM for anomaly scoring.
>
> • LSTM/Transformer autoencoder on key-timestamp sequences for
> reconstruction error anomalies.
>
> • Hesitation Classifier:
>
> • Feature-based (XGBoost / RandomForest) using pause statistics. •
> Answer Similarity Detector:
>
> • Use sentence-transformers e.g., all-MiniLM-L6-v2 to embed answers;
> compute cosine similarity and pairwise clustering.
>
> • Fusion Decision Model:
>
> • Logistic regression baseline; then small MLP that inputs
> standardized scores. • Calibration: Use Platt scaling / isotonic
> regression.

**Phase** **6** **—** **Integration** **&** **Real-Time** **Inference**
**(Week** **10)**

> • Serve models as REST endpoints or via TorchServe / BentoML.
>
> • Inference flow: incoming event batches → feature extractor →
> per-question score → fusion → send risk update to dashboard.
>
> • Implement threshold policies and human-in-the-loop flagging for
> low-confidence cases.

**Phase** **7** **—** **Evaluation** **&** **Ablation** **Study**
**(Weeks** **11–12)**

> • Experiments:
>
> • Single-signal baselines (typing-only, similarity-only,
> hesitation-only). • Fusion vs baselines.
>
> • Cross-device testing (mobile/desktop), slow/fast typists analysis.
>
> • Metrics to record: precision, recall, F1, ROC-AUC, false positive
> rate per hour, fairness across demographics.

**Phase** **8** **—** **Paper** **Writing** **&** **Packaging**
**(Weeks** **13–14)**

> • Prepare artifacts: code repo, dataset (anonymized), trained model
> weights, evaluation scripts. • Write paper: intro, related work,
> methods (features + models), experiments, ethical discussion,
>
> conclusion.

**5.Data** **Collection** **&** **Labeling** **Protocol**

> • **Session** **metadata:** student_id (anonymized), device_type,
> browser, time, question_id, exam_id. • **Event** **types** **to**
> **record:** keydown, keyup, paste, focus/blur, visibilitychange, cut,
> copy, submit,
>
> selection changes.
>
> 3
>
> • **Privacy** **rules:** do not log full clipboard contents; only
> lengths and whether paste occurred. Hash student IDs. Keep raw text
> answers separately encrypted or store only embeddings for similarity
> analysis.

**Labeling** **guidelines:** - Honest (0): Participant answers without
external help. - Cheating (1): Participant uses
search/phone/collusion/AI assistance during the question. - Mixed:
Sessions may have partial cheating; annotate time ranges where cheating
occurred if possible.

**6.Feature** **Engineering** **(Detailed)** **Typing** **features**

> • Mean inter-key delay (ms) • Std of inter-key delay
>
> • Mean keypress duration
>
> • Typing speed (chars per second) • Backspace count per 100 chars
>
> • Burstiness (fraction of fast sequences)

**Hesitation** **features**

> • Time to first keypress after question load • Number of pauses \> 2s,
> \> 5s
>
> • Longest idle duration
>
> • Ratio of idle time to total time

**Editing** **&** **Navigation** **features**

> • Paste events count and paste size (chars) • Copy/cut events (count
> only)
>
> • Undo/redo counts
>
> • Focus loss count and total focus-loss duration • Tab switch rate
> (focus changes per minute)

**Answer-similarity** **features**

> • Sentence-BERT embedding for answers
>
> • Mean cosine similarity to all other students' answers for same
> question • Maximum pairwise similarity
>
> • Structural similarity: shared bigrams/trigrams ratio • Shared typo
> patterns (rare mistakes matching)

**Composite** **indicators**

> • Typing anomaly score (scaled 0–1) • Hesitation score (scaled 0–1)
>
> • Similarity score (scaled 0–1)
>
> 4

**7.Modeling** **Strategy**

> • **Baseline** **models:** IsolationForest (behavioral), Cosine
> thresholding (similarity), XGBoost (hesitation).
>
> • **Advanced** **models:** LSTM/Transformer autoencoders on raw
> sequences; Siamese networks for pairwise answer similarity.
>
> • **Fusion** **approaches:**
>
> • Weighted linear combination (interpretable) • Stacked model
> (meta-learner)
>
> • Graph-based clustering for collusion groups

**8.Real-time** **Inference** **&** **Integration**

> • Buffer events client-side; send micro-batches to backend every 3–5
> seconds.
>
> • Maintain per-session sliding-window features (e.g., last 30s) for
> near-real-time anomaly scoring. • Emit risk updates to dashboard with
> event timeline and contribution breakdown (e.g., "high
>
> similarity: 0.8; typing anomaly: 0.6").
>
> • Allow manual override and appeal workflow in admin UI.

**9.Evaluation,** **Ablation** **&** **Experiments**

> • **Ablation** **study:** measure performance drop when removing each
> modality. • **Robustness:** test on different devices, networks,
> browser extensions.
>
> • **Fairness:** evaluate false positive rates across user groups
> (native language, typing disability). • **User** **study:** measure
> the acceptability of camera-free proctoring and perceived privacy.

**10.Ethics,** **Privacy** **&** **Legal** **Considerations**

> • Minimize PII collection; hash/anonymize IDs.
>
> • Avoid storing clipboard contents or keystroke text in raw form;
> store aggregated features and embeddings.
>
> • Provide transparency to users about what is collected and how it is
> used. • Provide an appeals process and human review before punitive
> action.
>
> • Consult institutional IRB / ethics board before human-subject data
> collection.

**11.Deployment** **&** **Monitoring**

> • **Staging** **environment:** test capture under load (50–1000
> concurrent sessions).
>
> • **Monitoring:** track event ingest rate, feature extractor latency,
> model inference latency, and dashboard sync.
>
> • **Alerts:** high false-positive spikes, large drops in model
> accuracy, high latency. • **Model** **retraining:** scheduled
> weekly/biweekly depending on drift.

**12.Deliverables** **Checklist** • Working React exam client with
logging

> 5
>
> • FastAPI backend receiving & storing logs • Feature extractor +
> dataset (CSV/Parquet) • Trained models and inference API
>
> • Admin dashboard for flagged sessions • Evaluation scripts + ablation
> results
>
> • Paper draft & artifact bundle (code + data + weights)

**13.Suggested** **Paper** **Outline**

> 1\. Abstract
>
> 2\. Introduction & Motivation
>
> 3\. Related Work (keystroke dynamics, proctoring, similarity
> detection) 4. System Architecture
>
> 5\. Feature Engineering
>
> 6\. Models & Fusion Strategy 7. Experiments & Results
>
> 8\. Ethical Considerations
>
> 9\. Limitations & Future Work 10. Conclusion

**14.Appendix:** **Code** **Snippets** **&** **API** **Examples**
**Frontend:** **Minimal** **keystroke** **logger** **(concept)**

> // attach to a text-area for a question const buffer = \[\];
>
> textarea.addEventListener('keydown', e =\> buffer.push({t: Date.now(),
> type:'keydown', key:e.key}));
>
> textarea.addEventListener('keyup', e =\> buffer.push({t: Date.now(),
> type:'keyup', key:e.key}));
> window.addEventListener('visibilitychange', () =\> buffer.push({t:
> Date.now(), type: document.hidden ? 'blur' : 'focus'}));
>
> // flush every 3s setInterval(() =\> {
>
> if(buffer.length){
>
> fetch('/upload_events', {method:'POST', body:JSON.stringify({session,
> events:buffer})});
>
> buffer.length = 0; }
>
> }, 3000);

**Backend:** **Simple** **feature** **extractor** **(concept)**

> \# given events for a question, compute mean inter-key delay def
> mean_inter_key_delay(events):
>
> keydowns = \[e\['t'\] for e in events if e\['type'\]=='keydown'\]
>
> 6
>
> diffs = \[t2-t1 for t1,t2 in zip(keydowns, keydowns\[1:\])\] return
> sum(diffs)/len(diffs) if diffs else 0

**Example** **API** **endpoints**

> • POST /upload_events -\> receives {session_id, student_hash,
> question_id, events\[\]}
>
> • POST /extract_features -\> returns feature vector
>
> • POST /infer -\> returns {risk_score, reasons\[\]}
>
> 7
