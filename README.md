# PostgreSQL-S3 Pipeline

## Design Rationale & Implementation Notes

This solution intentionally prioritizes simplicity and speed of delivery. The architecture leverages AWS DMS, Kinesis, Lambda and RDS to create a straightforward pipeline for streaming database changes. The goal is to validate a working approach quickly, with the flexibility to evolve toward more complex solutions if requirements grow.

Some specific design choices and considerations:
- **Technology Selection**: DMS, Kinesis, Lambda and RDS are selected for their ease of integration and rapid setup. This enables fast prototyping and demonstration of end-to-end data flow.
- **Data Format**: JSON is used in S3, but for production, Parquet is recommended due to its efficiency for analytics and downstream processing.
- **Project Structure**: All code is kept at the project root for simplicity, but as the codebase grows, refactoring into logical directories is recommended for maintainability.
- **CloudFormation**: Because of the time constraints, CloudFormation is not used.

This approach demonstrates practical engineering tradeoffs, balancing delivery speed and clarity for the purposes of this assignment.

## Conclusion

The requirement was to achieve an end-to-end latency of **strictly less than 1 second**.

The current implementation **sometimes meets this target** (when Lambda is warm and DMS commits immediately), but **does not consistently stay under 1 second**.  
Typical latency ranges between **1 and 3 seconds**.

The main reasons are:
- **DMS replication buffering** causing unpredictable small delays,
- **Lambda cold starts** occasionally adding extra startup time,
- **Minor S3 network variability**.

### Summary
This solution demonstrates the correct real-time flow, but **does not fully satisfy the strict <1 second requirement under all conditions**.


## Architecture Diagram
```mermaid
flowchart LR
  A[RDS PostgreSQL] -->|WAL replication| B[DMS Replication]
  B -->|Stream WAL changes| C[Kinesis Data Stream]
  C -->|Trigger event| D[AWS Lambda Function]
  D -->|Processed features| E[S3 Processed Bucket]
```

## Scalability

**Horizontal scalability:**
- In this solution, Kinesis and Lambda can both scale out: if there are more events, AWS will run more Lambdas and Kinesis can add more shards.
- S3 can take as much data as you want.

**Vertical scalability:**
- You can make your RDS database bigger if you need to handle more traffic.

**Pros:**
- Easy to scale for more data/events (just add more Kinesis shards or let Lambda run more copies).
- S3 and Lambda scale almost automatically.

**Cons:**
- The database (RDS) is harder to scale for lots of writes; you can only make it so big.
- AWS has some limits (like how many Lambdas can run at once, or Kinesis shard limits).


## Quick Start
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in your AWS/Postgres info.
3. Test locally with `test-input/kinesis_test_input.json`:
   ```bash
   python lambda_function.py
   ```
   