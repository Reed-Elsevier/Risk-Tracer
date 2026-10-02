# RiskTracer

RiskTracer helps a human reviewer investigate supplier payment risk using invoice, supplier, relationship, and watchlist evidence.

## Language

**Investigation**:
A review centered on one invoice and the related supplier, payment, ownership, and watchlist evidence. A supplier profile can lead to an investigation of one of its invoices.
_Avoid_: Supplier investigation

**Review decision**:
A human reviewer's disposition of an investigation, such as escalating or clearing it, with a note and the evidence considered at that time. It does not represent a payment action.
_Avoid_: Payment approval, payment hold

**Evidence snapshot**:
The set of source facts and derived signals considered when a review decision was recorded.

**Ownership path**:
A sequence of ownership relationships connecting a supplier's business entity to another business entity. Each step represents a recorded entity-to-entity relationship.

**Indirect watchlist exposure**:
A recorded ownership path of one or two upstream links from a supplier's business entity to an entity with a watchlist entry. The path is a relationship signal, not proof of beneficial ownership or control.
_Avoid_: Beneficial owner match

**Indirect ownership link**:
A single reported entity-to-entity relationship labeled Indirect in the source data. Its intermediate relationships, if any, are not established by that record.

**Latest recorded exposure**:
A relationship to a listed entity found in the latest available dataset records. Its ownership and listing dates remain part of the evidence; the records do not by themselves verify that the relationship is still active.
_Avoid_: Verified current ownership

**Possible duplicate submission**:
Two invoice records with matching identifying details that warrant human comparison. This does not establish that either invoice was paid twice.
_Avoid_: Duplicate payment

**Invoice exception**:
A recorded issue or discrepancy associated with an invoice, whether or not the issue later received a recorded resolution. The invoice's status states its current workflow position.

**PO integrity signal**:
An invoice's purchase order reference is missing, or its referenced purchase order belongs to a different supplier or currency. The signal calls for review but does not establish fraud.

**Retrospective review**:
An investigation of an invoice whose payment has already been made. Its suggested next step concerns follow-up and verification, not holding the completed payment.

**Review priority**:
A workflow label that orders investigations for human attention using the signals found by RiskTracer. It is not a probability of fraud or a conclusion about the supplier.
_Avoid_: Fraud score
