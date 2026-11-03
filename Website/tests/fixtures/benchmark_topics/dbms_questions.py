"""
Authentic Database Management Systems (DBMS) Question Generator
Provides university-grade, domain-specific assessments covering:
1. Relational Model, Functional Dependencies & Normalization (1NF to BCNF)
2. SQL Query Execution Plans, B+ Tree Indexing & Hash Join Operations
3. ACID Transaction Properties, Serializability & Two-Phase Locking (2PL)
4. Crash Recovery, Write-Ahead Logging (WAL) & ARIES Protocol
"""

from typing import Dict, Any, Optional

def generate_dbms_question(
    c_name: str,
    tier: str,
    q_idx: int,
    has_probe: bool,
    pattern_idx: int = 0
) -> Dict[str, Any]:
    c_low = c_name.lower()

    # 1. Relational Model, Functional Dependencies & Normalization
    if "relational" in c_low or "normal" in c_low or "depend" in c_low or "bcnf" in c_low or "schema" in c_low:
        if tier == "basic":
            if pattern_idx % 2 == 0:
                text = "In relational database theory, what formal condition is required for a relation to be in Boyce-Codd Normal Form (BCNF)?"
                opts = {
                    "A": "For every non-trivial functional dependency X -> Y, the determinant X must be a superkey of the relation.",
                    "B": "Every table must contain at least three foreign key relationships referencing external schemas.",
                    "C": "All character columns must be encoded exclusively in ASCII format without unicode characters.",
                    "D": "Primary keys must be stored in alphabetical order across secondary storage pages."
                }
                expl = "BCNF is a stricter version of 3NF. It eliminates all redundancy based on functional dependencies by mandating that for every non-trivial X -> Y, X must be a superkey."
            else:
                text = "What is the primary objective of decomposing an unnormalized relation into Third Normal Form (3NF)?"
                opts = {
                    "A": "To eliminate transitive dependencies, thereby preventing update, insertion, and deletion anomalies while preserving functional dependencies.",
                    "B": "To merge all separate tables into a single global table containing 500 columns.",
                    "C": "To convert relational tables into unstructured document JSON files.",
                    "D": "To force all database queries to execute using sequential table scans."
                }
                expl = "3NF eliminates transitive dependencies (non-prime attributes determining other non-prime attributes), stopping anomalies where changing an attribute requires updating thousands of duplicate rows."
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": None}

        elif tier == "conceptual":
            text = "Consider a relation R(A, B, C) with functional dependencies {AB -> C, C -> B}. What normal form does this relation satisfy, and why?"
            opts = {
                "A": "It is in 3NF but violates BCNF, because in C -> B, the attribute B is a prime attribute (part of candidate key AB), but determinant C is not a superkey.",
                "B": "It violates 1NF because the attributes contain repeating groups and non-atomic values.",
                "C": "It is in 4NF because multi-valued dependencies are completely absent.",
                "D": "It is not a valid mathematical relation because functional dependencies cannot have single-attribute determinants."
            }
            expl = "Candidate keys are AB and AC. For C -> B: C is not a superkey (violates BCNF), but B is part of candidate key AB, so 3NF's condition (either X is superkey or Y is prime) is satisfied."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Why can decomposing R(A, B, C) with dependencies {AB -> C, C -> B} into BCNF relations R1(C, B) and R2(A, C) cause dependency preservation issues?",
                    "options": {
                        "A": "The original dependency AB -> C cannot be verified by checking either R1 or R2 in isolation without performing an expensive relational join.",
                        "B": "BCNF decomposition deletes all primary key indexes from the storage engine.",
                        "C": "Decomposed relations cannot store numeric data types in database columns.",
                        "D": "Relational joins are prohibited in Boyce-Codd Normal Form schemas."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

        else: # application
            text = "A customer order table stores `(OrderID, CustomerID, CustomerAddress, ItemID, Quantity, ItemPrice)`. Updates to customer addresses frequently result in inconsistent data where past orders display stale addresses while recent orders show updated addresses. How should a database architect re-engineer this relation?"
            opts = {
                "A": "Decompose into separate 3NF relations: Customers(CustomerID, Address), Orders(OrderID, CustomerID, OrderDate), and OrderItems(OrderID, ItemID, Quantity, PriceAtPurchase).",
                "B": "Add a trigger that deletes all historical order records whenever a customer changes their shipping address.",
                "C": "Combine all orders into a single CSV flat file and disable database foreign key constraints.",
                "D": "Require customers to re-register with a brand-new CustomerID every time they move houses."
            }
            expl = "The original table suffers from transitive dependencies and mixed functional dependencies (`CustomerID -> Address`, `OrderID, ItemID -> Quantity`). Normalizing into distinct entities eliminates the update anomaly."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Why is `PriceAtPurchase` explicitly retained in OrderItems rather than relying solely on the current item price in an Items table?",
                    "options": {
                        "A": "Historical orders require an immutable snapshot of transaction price at time of sale, preventing historical accounting discrepancies when product prices fluctuate.",
                        "B": "Floating point price columns cannot be indexed in relational database tables.",
                        "C": "The SQL language prohibits referencing foreign key tables during invoice printing.",
                        "D": "Retaining purchase price converts the relational schema into a non-relational key-value store."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

    # 2. SQL Query Execution Plans, B+ Tree Indexing & Hash Join Operations
    elif "index" in c_low or "b+" in c_low or "query" in c_low or "join" in c_low or "plan" in c_low:
        if tier == "basic":
            if pattern_idx % 2 == 0:
                text = "Why do relational database storage engines use B+ Trees rather than standard Binary Search Trees (BST) for disk-based indexing?"
                opts = {
                    "A": "B+ Trees have high fan-out (wide branching factor) which minimizes tree height, drastically reducing the number of expensive disk page I/O reads required to locate a key.",
                    "B": "Binary Search Trees consume double the CPU instruction cycles during floating-point arithmetic.",
                    "C": "B+ Trees store all leaf nodes in volatile CPU register memory rather than physical disks.",
                    "D": "Binary Search Trees can only index single-digit integer columns in database tables."
                }
                expl = "Disk I/O is the primary bottleneck. A B+ Tree with 4KB pages and fan-out of 100+ can index millions of rows in 3 to 4 levels, requiring only 3-4 page reads, whereas a BST requires dozens of random disk seeks."
            else:
                text = "In relational databases, what defines a 'Clustered Index'?"
                opts = {
                    "A": "An index where the physical storage order of rows on disk matches the indexed key order; hence, a table can possess only one clustered index.",
                    "B": "An index distributed across ten distinct physical server hardware clusters.",
                    "C": "An index created strictly on non-numeric textual description columns.",
                    "D": "An index that executes queries strictly using random number generators."
                }
                expl = "A clustered index determines the actual physical sequence of data in the table. Because physical rows can only be sorted in one order on disk, each table has at most one clustered index."
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": None}

        elif tier == "conceptual":
            text = "Under what query condition will a database query optimizer intentionally choose a sequential Full Table Scan instead of using an existing B+ Tree index on the queried column?"
            opts = {
                "A": "When the query predicate has low selectivity (matches a large fraction of table rows, e.g., >15-20%), where sequential block reads are faster than thousands of scattered random page I/Os.",
                "B": "When the table contains more than five columns with integer data types.",
                "C": "When the database administrator has logged out of the management console.",
                "D": "When the B+ Tree index contains duplicate keys in its internal routing nodes."
            }
            expl = "Index scans incur random I/O: look up leaf pointer, then fetch corresponding data page. When retrieving >15-20% of rows, sequential table scan is much faster due to disk sequential prefetching."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Why does a 'Covering Index' maintain high performance even when a query retrieves a substantial volume of rows?",
                    "options": {
                        "A": "The index contains all columns requested by the SELECT and WHERE clauses, allowing the query engine to satisfy the request directly from the index leaves without touching table heap pages.",
                        "B": "Covering indexes disable all query logging in database transactions.",
                        "C": "Covering indexes double the physical network bandwidth of database servers.",
                        "D": "Covering indexes convert SQL queries into compiled C++ binary machine instructions."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

        else: # application
            text = "A query `SELECT * FROM Orders o JOIN Customers c ON o.CustomerID = c.CustomerID` joins a 50-million-row Orders table with a 50,000-row Customers table. How should the query optimizer execute this join for maximum throughput?"
            opts = {
                "A": "Build a Hash Join by hashing the smaller Customers table into memory, then stream the Orders table once through the hash table to match keys in O(N + M) time.",
                "B": "Execute an unindexed Nested Loop Join comparing all 50 million orders against all 50,000 customers in O(N * M) time.",
                "C": "Sort both tables in reverse alphabetical order and delete all rows where CustomerID is even.",
                "D": "Send all 50 million order rows across the client web browser to perform the join using JavaScript array filters."
            }
            expl = "Hash Join is optimal for joining a small relation with a large relation when no index exists on the join key. Building an in-memory hash table on the small build relation allows single-pass probe over the large stream."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "When would a Sort-Merge Join be chosen over a Hash Join for this query?",
                    "options": {
                        "A": "When both relations are already physically sorted on CustomerID (e.g., via clustered index), allowing linear two-pointer scanning without memory hash allocation.",
                        "B": "When the database server has less than 256 bytes of physical RAM.",
                        "C": "When the SQL statement contains a LIMIT 0 clause.",
                        "D": "When the Customers table contains zero rows."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

    # 3. ACID Transaction Properties, Serializability & Two-Phase Locking (2PL)
    elif "acid" in c_low or "transact" in c_low or "lock" in c_low or "2pl" in c_low or "serializ" in c_low:
        if tier == "basic":
            if pattern_idx % 2 == 0:
                text = "What is the specific guarantee provided by the 'Atomicity' property of ACID database transactions?"
                opts = {
                    "A": "All operations within the transaction execute successfully to completion, or none of them take effect (all-or-nothing execution).",
                    "B": "Every query executes in less than one atomic microsecond.",
                    "C": "Data is physically stored inside subatomic particle spins on quantum hardware.",
                    "D": "Transactions are restricted strictly to single-table arithmetic modifications."
                }
                expl = "Atomicity ensures that a transaction is treated as a single indivisible unit of work: if a failure occurs halfway through, the engine rolls back all intermediate changes."
            else:
                text = "What rule governs the Strict Two-Phase Locking (Strict 2PL) concurrency control protocol?"
                opts = {
                    "A": "A transaction acquires locks during its growing phase and must hold all exclusive locks until transaction commit or abort.",
                    "B": "Every table must be locked for exactly two seconds before allowing updates.",
                    "C": "Transactions must release locks immediately after reading a single database column.",
                    "D": "Only two users can connect to the database server at any given time."
                }
                expl = "Strict 2PL guarantees conflict serializability and prevents cascading aborts by holding all exclusive (write) locks until the transaction ends (commit/abort)."
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": None}

        elif tier == "conceptual":
            text = "In ANSI SQL isolation levels, what is a 'Phantom Read' and which isolation level is required to prevent it?"
            opts = {
                "A": "A transaction re-executes a range query and discovers new rows inserted by another committed concurrent transaction; prevented strictly by Serializable isolation (or range locks).",
                "B": "A query returns data that was corrupted by electromagnetic interference on the motherboard.",
                "C": "A database user reads uncommitted changes that are subsequently rolled back; prevented by Read Committed.",
                "D": "Two transactions update the same single row simultaneously without lock collision."
            }
            expl = "A phantom read occurs when a range query (`WHERE age > 30`) returns different row sets because another transaction inserted and committed a qualifying row. Only Serializable prevents phantoms using predicate or gap locks."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Why does standard row-level locking on existing records fail to prevent phantom reads?",
                    "options": {
                        "A": "Row locks can only be placed on records that already physically exist in the table; they cannot lock non-existent placeholder records being inserted by other transactions.",
                        "B": "Row locks are automatically disabled whenever a SQL query includes a WHERE clause.",
                        "C": "Row locks cause the database engine to revert to 16-bit transaction identifiers.",
                        "D": "Row locks only apply to read operations, never to write operations."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

        else: # application
            text = "Transaction T1 transfers $100 from Account A to B (`Lock A -> Lock B`), while concurrent Transaction T2 transfers $50 from B to A (`Lock B -> Lock A`). What concurrency failure occurs and how does the database engine automatically resolve it?"
            opts = {
                "A": "Deadlock (circular wait); resolved by the engine maintaining a Wait-For Graph, detecting the cycle, and aborting one transaction (the victim) to release its locks.",
                "B": "Data corruption; resolved by deleting both accounts and resetting the bank balance to zero.",
                "C": "Buffer overflow; resolved by switching database network ports from 5432 to 3306.",
                "D": "Phantom read; resolved by restarting the physical operating system server."
            }
            expl = "Opposing lock acquisition order causes a classic deadlock cycle. The DBMS background deadlock detector spots the cycle in the Wait-For graph, selects a victim transaction, rolls it back, and returns a retryable error to the client."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "How can application developers design transaction code to structurally eliminate this deadlock without relying on DBMS aborts?",
                    "options": {
                        "A": "Enforce a global ordering on resource acquisition (e.g., always acquire locks in ascending order of AccountID: `min(A, B)` then `max(A, B)`).",
                        "B": "Wrap all database queries in infinite while-true retry loops.",
                        "C": "Remove all primary keys from bank account database tables.",
                        "D": "Execute all bank transfers using raw unauthenticated UDP datagrams."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

    # 4. Crash Recovery, Write-Ahead Logging (WAL) & ARIES Protocol
    else:
        if tier == "basic":
            if pattern_idx % 2 == 0:
                text = "What is the foundational principle of Write-Ahead Logging (WAL) in database crash recovery systems?"
                opts = {
                    "A": "Log records describing a data modification must be flushed to non-volatile disk storage BEFORE the corresponding dirty data page is written to database storage.",
                    "B": "Data pages must be written to disk three times before writing any log entries.",
                    "C": "Log files must be completely wiped and deleted every time the database server boots up.",
                    "D": "All database queries must be logged to text files on client mobile devices."
                }
                expl = "WAL dictates: (1) Undo rule: log record flushed to disk before dirty page is written (ensures rollback capability); (2) Redo rule: all log records for a committed transaction flushed to disk before commit acknowledges."
            else:
                text = "In the ARIES recovery algorithm, what is the sequence and role of the three distinct recovery passes executed after a crash?"
                opts = {
                    "A": "Analysis (determines dirty pages and active transactions at crash), Redo (repeats history to restore crash state), and Undo (rolls back uncommitted loser transactions).",
                    "B": "Compilation, Assembly, and Execution passes.",
                    "C": "Defragmentation, Re-indexing, and File System Compression passes.",
                    "D": "Backup, Export, and Drop Database passes."
                }
                expl = "ARIES recovery executes: (1) Analysis pass (finds winners/losers and dirty pages from checkpoint); (2) Redo pass ('repeating history' to re-apply committed changes); (3) Undo pass (undoes effects of active loser transactions)."
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": None}

        elif tier == "conceptual":
            text = "Why does the ARIES recovery algorithm 'Repeat History' during its Redo phase, re-applying changes even for transactions that were uncommitted and will eventually be rolled back?"
            opts = {
                "A": "To return the database to the exact consistent physical state at the instant of failure, ensuring that subsequent Undo logging (Compensation Log Records) functions deterministically without ambiguity.",
                "B": "Because the database engine cannot determine which transactions committed until after the hard drive is reformatted.",
                "C": "To test whether the secondary storage disk drives can tolerate maximum write workloads.",
                "D": "Because uncommitted transactions are legally required to be saved in public archives."
            }
            expl = "Repeating history ensures that page LSNs (Log Sequence Numbers) match reality. Once the exact crash state is reconstructed, the Undo pass cleanly reverses loser transactions and writes Compensation Log Records (CLRs) to prevent crash loops during recovery."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "What purpose do Compensation Log Records (CLRs) serve if the database server crashes AGAIN during the Undo phase of recovery?",
                    "options": {
                        "A": "CLRs record undo actions; when re-recovering, the engine reads CLRs and avoids repeating work that was already undone, guaranteeing bounded recovery time without infinite rollback loops.",
                        "B": "CLRs delete the master encryption keys to protect database confidentiality during a second crash.",
                        "C": "CLRs convert the database server into an in-memory Redis cache.",
                        "D": "CLRs force all client applications to disconnect and terminate permanently."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

        else: # application
            text = "A sudden power outage halts a database server mid-transaction. Inspection of the WAL log shows: Transaction T1 committed before the crash, T2 was midway through inserting 5,000 rows without committing, and T3 committed just prior to loss. How does the recovery manager handle T1, T2, and T3?"
            opts = {
                "A": "Redo passes re-apply changes for T1, T2, and T3; the Undo pass then reverses all modifications made by T2 (the loser transaction) using log undo records.",
                "B": "Discard all modifications made by all three transactions and restore yesterday's cold tape backup.",
                "C": "Force T2 to commit automatically and award synthetic default values to missing fields.",
                "D": "Delete the entire transaction log file and restart the database in read-only maintenance mode."
            }
            expl = "T1 and T3 are committed winners: their changes are preserved by the Redo pass. T2 was active without a commit record (loser): its changes are undone during the Undo pass, leaving the database consistent and durable."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Why can the database system safely acknowledge a COMMIT to the client application BEFORE the modified table data pages are physically flushed from RAM buffer pools to disk?",
                    "options": {
                        "A": "Because WAL log records describing the commit are synchronously flushed to disk first; if power fails before dirty data pages are flushed, the Redo pass reconstructs the data from the log.",
                        "B": "Because modern RAM retains electrical memory states for twelve months without battery backup.",
                        "C": "Because client applications maintain an authoritative copy of the entire database in their browser memory.",
                        "D": "Because unwritten data pages are automatically written to optical disks by BIOS firmware."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}
