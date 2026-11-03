"""
Authentic Operating Systems Question Generator
Provides university-grade, domain-specific assessments covering:
1. Process Lifecycle, Context Switching & CPU Scheduling Algorithms
2. Concurrency Control, Semaphores & Deadlock Coffman Conditions
3. Memory Management, Paging & Virtual Memory Thrashing
4. File System Inodes, Journaling & I/O Disk Scheduling
"""

from typing import Dict, Any, Optional

def generate_os_question(
    c_name: str,
    tier: str,
    q_idx: int,
    has_probe: bool,
    pattern_idx: int = 0
) -> Dict[str, Any]:
    c_low = c_name.lower()

    # 1. Process Lifecycle, Context Switching & CPU Scheduling
    if "process" in c_low or "schedul" in c_low or "context" in c_low or "lifecycle" in c_low:
        if tier == "basic":
            if pattern_idx % 2 == 0:
                text = "During an operating system context switch between two processes, which primary data structure must the kernel save and restore?"
                opts = {
                    "A": "The Process Control Block (PCB), including CPU registers, program counter, and stack pointer.",
                    "B": "The physical sector layout of the hard drive platters in storage controllers.",
                    "C": "The external DNS cache records stored in the network gateway router.",
                    "D": "The compiler optimization symbol table located in the user's home directory."
                }
                expl = "A context switch requires saving the executing process's state (registers, PC, stack pointer, page table base) into its PCB and restoring the state of the next scheduled process."
            else:
                text = "How does Round Robin (RR) CPU scheduling prevent starvation compared to non-preemptive Shortest Job First (SJF)?"
                opts = {
                    "A": "RR allocates a fixed time quantum per process, preempting long-running jobs to give all ready processes fair CPU access.",
                    "B": "RR executes processes in order of their compiled executable file size on disk.",
                    "C": "RR permanently terminates any process that exceeds two seconds of total execution time.",
                    "D": "RR assigns CPU cores exclusively to background operating system daemon threads."
                }
                expl = "Round Robin is preemptive: after a time slice expires, the running process is moved to the tail of the ready queue, preventing long jobs from monopolizing the CPU."
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": None}

        elif tier == "conceptual":
            text = "What trade-off governs the selection of the time quantum length in Round Robin CPU scheduling?"
            opts = {
                "A": "A very short quantum increases context-switch overhead and wastes CPU cycles, while a very long quantum degrades interactive responsiveness and approaches FCFS behavior.",
                "B": "A short quantum corrupts virtual memory page tables, while a long quantum eliminates cache misses.",
                "C": "A short quantum doubles physical RAM capacity, while a long quantum reduces network bandwidth.",
                "D": "The quantum length has no impact on system throughput or responsiveness in modern multicore systems."
            }
            expl = "If the time quantum is too small (e.g., 1 microsecond), context-switch overhead dominates. If too large (e.g., 10 seconds), interactive response times deteriorate toward First-Come-First-Served."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Why does a CPU-bound process suffer less from a larger time quantum than an I/O-bound interactive process?",
                    "options": {
                        "A": "CPU-bound jobs maximize throughput when allowed to run uninterrupted without frequent register save/restore overhead.",
                        "B": "CPU-bound jobs do not utilize arithmetic logic units during execution.",
                        "C": "I/O-bound jobs require continuous floating-point coprocessor calibration.",
                        "D": "CPU-bound jobs bypass the kernel scheduler by executing directly in BIOS ROM."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

        else: # application
            text = "A server experiences a severe performance collapse where CPU utilization drops to 6% while average job turnaround times skyrocket. System metrics show context switch frequency exceeds 250,000 switches per second. How should the systems engineer diagnose and remedy this?"
            opts = {
                "A": "Increase the scheduler time quantum and evaluate whether excessive thread contention on synchronized spinlocks is forcing rapid preemptions.",
                "B": "Underclock the CPU frequency by 75% to reduce the total number of instructions executed per minute.",
                "C": "Delete all swap partitions and disable virtual memory across the entire operating system.",
                "D": "Replace all SATA disk cables with shielded audio cables to reduce electrical interference."
            }
            expl = "Excessive context switching indicates either a microscopic time quantum or heavy lock contention (threads repeatedly yielding upon failing to acquire mutexes). Lengthening quantum and mitigating lock contention restores throughput."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Why does high lock contention between thousands of threads cause context switch rates to explode?",
                    "options": {
                        "A": "Blocked threads immediately trigger kernel yield transitions to give CPU time to unblocked threads, incurring massive scheduling overhead.",
                        "B": "Lock contention causes the CPU instruction pipeline to reverse its clock direction.",
                        "C": "Mutex locks force the kernel to write the entire physical RAM contents to the hard drive on every lock attempt.",
                        "D": "Contended locks erase user process IDs and require rebooting the operating system."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

    # 2. Concurrency Control, Semaphores & Deadlock Coffman Conditions
    elif "concurr" in c_low or "deadlock" in c_low or "semaphor" in c_low or "mutex" in c_low:
        if tier == "basic":
            if pattern_idx % 2 == 0:
                text = "Which four Coffman conditions must ALL hold simultaneously for a system deadlock to occur?"
                opts = {
                    "A": "Mutual Exclusion, Hold and Wait, No Preemption, and Circular Wait.",
                    "B": "Virtual Paging, Cache Snooping, Direct Memory Access, and Branch Prediction.",
                    "C": "User Mode, Kernel Mode, Interrupt Vectoring, and DMA Channeling.",
                    "D": "Serial Execution, Compilation, Assembly, and Linking."
                }
                expl = "Deadlock requires all 4 Coffman conditions: non-shareable resources (mutual exclusion), holding resources while waiting for others, inability to forcibly seize resources (no preemption), and a circular chain of waiting processes."
            else:
                text = "What is the atomic operational behavior of the Semaphore `wait()` (or `P()`) primitive?"
                opts = {
                    "A": "It decrements the semaphore counter; if the resulting value is negative, the calling thread is blocked until a `signal()` occurs.",
                    "B": "It immediately terminates the calling process and sends an alert to the system administrator.",
                    "C": "It doubles the process priority and locks all other CPU cores until the process terminates.",
                    "D": "It reads the system clock and pauses thread execution for exactly ten milliseconds."
                }
                expl = "The `wait()` / `P()` operation decrements the internal counter atomically. If value < 0, the thread is queued on the semaphore's wait list."
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": None}

        elif tier == "conceptual":
            text = "How does Deadlock Prevention differ fundamentally from Deadlock Avoidance in operating systems?"
            opts = {
                "A": "Prevention structurally eliminates at least one Coffman condition at design time, whereas Avoidance tracks dynamic resource allocation states at runtime (e.g., Banker's Algorithm) to avoid unsafe transitions.",
                "B": "Prevention reboots the server every 24 hours, while Avoidance terminates processes at random.",
                "C": "Prevention requires dedicated hardware co-processors, while Avoidance operates strictly in BIOS firmware.",
                "D": "Prevention allows deadlocks to occur and cleans them up, while Avoidance prohibits multi-threaded programming."
            }
            expl = "Deadlock Prevention imposes structural constraints (like acquiring resources in strict global linear order to break Circular Wait). Deadlock Avoidance evaluates runtime requests dynamically to ensure the system never enters an unsafe state."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Why does imposing a strict global ordering on resource acquisition successfully eliminate deadlocks?",
                    "options": {
                        "A": "A cycle of dependencies cannot form if every process must acquire resources in strictly increasing numerical order.",
                        "B": "Global ordering converts all multicore processors into single-core sequential processors.",
                        "C": "Global ordering eliminates the need for mutual exclusion on physical printers and disk blocks.",
                        "D": "Global ordering forces all running threads to share a single unified execution stack."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

        else: # application
            text = "In an embedded flight controller, a low-priority thread holding a shared sensor mutex is preempted by a medium-priority background communication thread, preventing a critical high-priority navigation task from acquiring the mutex. What is this phenomenon and how is it resolved?"
            opts = {
                "A": "Priority Inversion; resolved using the Priority Inheritance Protocol, where the low-priority thread temporarily inherits the high-priority thread's priority until releasing the mutex.",
                "B": "Memory Fragmentation; resolved by executing a garbage collection pass across the flash memory.",
                "C": "Buffer Overflow; resolved by compiling the kernel in 16-bit real mode.",
                "D": "Thrashing; resolved by swapping the process out to a solid-state disk partition."
            }
            expl = "Priority Inversion famously affected the Mars Pathfinder mission. The Priority Inheritance Protocol ensures that whenever a high-priority task blocks on a mutex held by a lower task, the lower task temporarily inherits the high priority to finish and release the resource quickly."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Why does the medium-priority task indirectly starve the high-priority task in classic Priority Inversion?",
                    "options": {
                        "A": "The medium-priority task does not need the mutex, so it preempts the low-priority task indefinitely, preventing it from ever finishing and releasing the mutex needed by the high-priority task.",
                        "B": "The medium-priority task deletes the mutex handle from the operating system kernel table.",
                        "C": "The medium-priority task overwrites the high-priority task's program counter register.",
                        "D": "The medium-priority task shuts off power to the sensor hardware bus."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

    # 3. Memory Management, Paging & Virtual Memory Thrashing
    elif "memory" in c_low or "pag" in c_low or "virtual" in c_low or "thrash" in c_low:
        if tier == "basic":
            if pattern_idx % 2 == 0:
                text = "What is the primary architectural purpose of Paging in modern virtual memory systems?"
                opts = {
                    "A": "To allow process physical address spaces to be non-contiguous, eliminating external fragmentation and enabling memory protection.",
                    "B": "To compress executable files on disk so they occupy less permanent storage space.",
                    "C": "To encrypt network packets before transmitting them over Ethernet adapters.",
                    "D": "To automatically synchronize local user files with remote cloud storage accounts."
                }
                expl = "Paging breaks physical memory into fixed-size frames and virtual memory into pages, allowing physical allocation to be fragmented across RAM without affecting the contiguous virtual address space."
            else:
                text = "What event occurs when a CPU references a virtual memory page that is marked not present in physical RAM?"
                opts = {
                    "A": "A Page Fault exception is raised, triggering the kernel to fetch the missing page from secondary storage into an available RAM frame.",
                    "B": "The computer system immediately reboots to recover from corrupted firmware.",
                    "C": "The running process is converted into a zombie state and permanently deleted.",
                    "D": "The CPU halts instruction execution until a physical RAM stick is replaced."
                }
                expl = "A page fault is a hardware interrupt raised by the MMU when a valid page's present bit is 0 in the page table, causing the OS to load the page from disk swap."
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": None}

        elif tier == "conceptual":
            text = "What is 'Thrashing' in an operating system, and what is its direct operational cause?"
            opts = {
                "A": "A state where the system spends more time servicing page faults and swapping pages in and out of disk than executing instructions, caused when the sum of process working sets exceeds physical RAM.",
                "B": "A mechanical failure where hard drive read/write arms physically collide with rotating metal platters.",
                "C": "An algorithmic condition where the scheduler alternates between two threads on every CPU clock cycle.",
                "D": "A network congestion issue where duplicate TCP packets flood the local router buffer."
            }
            expl = "Thrashing occurs when available physical frames cannot hold the active working sets of running processes. Every process immediately faults, creating a queue of disk I/O requests that halts CPU progress."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "How does the 'Working Set Model' prevent thrashing in multiprogrammed operating systems?",
                    "options": {
                        "A": "By monitoring the pages referenced by each process over a time window and suspending/swapping out entire processes if total working set demand exceeds physical memory capacity.",
                        "B": "By allocating exactly one page frame to every active user thread regardless of program size.",
                        "C": "By converting all virtual addresses directly into hardcoded physical RAM pointers at compile time.",
                        "D": "By disabling the memory management unit whenever total RAM usage exceeds 80%."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

        else: # application
            text = "A virtualized database server shows 98% disk I/O utilization, 3% CPU utilization, and 12,000 page faults per second. Which corrective action directly resolves the underlying root cause?"
            opts = {
                "A": "Reduce the multiprogramming degree (suspend background batch jobs) or add physical RAM so that active processes' working sets fit entirely in physical memory.",
                "B": "Increase CPU clock speed by 15% using motherboard BIOS overclocking settings.",
                "C": "Change the CPU scheduling policy from Round Robin to First-Come-First-Served.",
                "D": "Replace all TCP networking sockets with unformatted raw UDP datagrams."
            }
            expl = "High paging I/O combined with near-zero CPU utilization is the classic hallmark of thrashing. Reducing multiprogramming frees frames for remaining jobs to satisfy their working sets, terminating the paging storm."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Why will overclocking the CPU fail to resolve thrashing under excessive memory demand?",
                    "options": {
                        "A": "The bottleneck is disk I/O latency for page swapping; executing CPU instructions faster only causes processes to reach their next page fault sooner.",
                        "B": "Overclocking automatically disables virtual memory in 64-bit operating systems.",
                        "C": "Overclocking clears the contents of secondary storage swap files.",
                        "D": "Disk read/write speeds are directly locked to CPU clock frequencies."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

    # 4. File System Inodes, Journaling & I/O Disk Scheduling
    else:
        if tier == "basic":
            if pattern_idx % 2 == 0:
                text = "In Unix-like file systems, what critical file metadata is stored in an Inode rather than inside directory entries?"
                opts = {
                    "A": "File permissions, owner UID, file size, timestamp metadata, and direct/indirect data block pointers.",
                    "B": "The actual human-readable filename and its full parent directory path string.",
                    "C": "The user's encrypted operating system login password and browser cookies.",
                    "D": "The compiler binary code used to build the operating system kernel."
                }
                expl = "In Unix filesystems, directory entries map filenames to inode numbers. The inode itself stores file type, access rights, ownership, size, timestamps, and pointers to the disk blocks storing content."
            else:
                text = "What is the primary function of Write-Ahead Journaling in modern file systems (e.g., ext4, NTFS)?"
                opts = {
                    "A": "To record intended metadata updates in a circular log before applying them to the file system, ensuring rapid consistency recovery after sudden power loss.",
                    "B": "To automatically duplicate all user files to a cloud server every thirty minutes.",
                    "C": "To compress audio and video files on disk to conserve storage volume space.",
                    "D": "To prevent unauthorized users from viewing the operating system boot log."
                }
                expl = "Journaling prevents filesystem corruption during crashes. By committing metadata changes to the journal first, a reboot after a power cut only requires replaying or rolling back the journal rather than running a full disk fsck scan."
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": None}

        elif tier == "conceptual":
            text = "How do Hard Links differ fundamentally from Symbolic (Soft) Links in file system architecture?"
            opts = {
                "A": "Hard links are additional directory entries that point directly to the same underlying inode number, whereas symbolic links are independent files containing a target file's path string.",
                "B": "Hard links require SSD drives, while symbolic links only function on magnetic rotating hard disks.",
                "C": "Hard links can cross external network mounts, while symbolic links cannot.",
                "D": "Deleting a hard link immediately deletes the original file content regardless of remaining references."
            }
            expl = "A hard link shares the target's inode (incrementing the inode reference count); deleting one link preserves data until the count reaches zero. A symbolic link is a distinct file holding a path; deleting the target creates a dangling symlink."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Why do traditional Unix file systems prohibit hard links between two different mounted file system partitions?",
                    "options": {
                        "A": "Inode numbers are unique only within a single filesystem partition; an inode number on disk A has no meaning or may point to an unrelated file on disk B.",
                        "B": "Hard links require identical disk spinning rotational speeds across both drives.",
                        "C": "Cross-filesystem links consume double the CPU cache lines in the kernel.",
                        "D": "Mounted partitions share a single unified read-only inode table."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

        else: # application
            text = "A storage server encounters severe disk head contention with random I/O requests scattered across all cylinders of a mechanical hard drive. How does the SCAN (Elevator) disk scheduling algorithm improve throughput over FCFS?"
            opts = {
                "A": "SCAN moves the disk arm in one direction servicing all pending requests across cylinders until reaching the end, then reverses direction, dramatically reducing total seek distance.",
                "B": "SCAN executes requests strictly in the exact order they arrive from client applications over the network.",
                "C": "SCAN deletes half of all pending disk write requests to reduce queue depth.",
                "D": "SCAN spins the disk platters in reverse direction to access blocks from the bottom side."
            }
            expl = "FCFS incurs massive random head travel back and forth across platters. The SCAN (elevator) algorithm sweeps across cylinders unidirectionally, minimizing mechanical seek time and maximizing contiguous throughput."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Why is mechanical disk seek time a far more significant performance bottleneck than rotational latency or transfer time?",
                    "options": {
                        "A": "Seek time involves physically accelerating and decelerating a mechanical actuator arm across millimeters of platter surface, which is orders of magnitude slower than electronic data transfer.",
                        "B": "Seek time requires the operating system kernel to switch into real mode.",
                        "C": "Actuator arm movements consume all available PCI Express bus bandwidth.",
                        "D": "Rotational latency only applies to solid-state drives without moving parts."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}
