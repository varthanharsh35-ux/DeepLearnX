"""
Specialized authentic question generator for Computer Science & Computer Systems Architecture.
Provides rigorous, concrete, university-grade assessments covering ISA, Pipelining, Caches, and Virtual Memory.
"""

from typing import Dict, Any, Optional

def generate_cs_architecture_question(
    c_name: str,
    tier: str,
    q_idx: int,
    has_probe: bool,
    pattern_idx: int = 0
) -> Dict[str, Any]:
    c_low = c_name.lower()

    # 1. Instruction Set Architecture & CPU Microarchitecture
    if "instruction set" in c_low or "microarchitecture" in c_low or "isa" in c_low:
        if tier == "basic":
            if pattern_idx % 2 == 0:
                text = "What is the primary role of the Instruction Set Architecture (ISA) in computer systems?"
                opts = {
                    "A": "It defines the functional interface between hardware and software, specifying instructions, registers, and addressing modes.",
                    "B": "It physically manufactures the semiconductor silicon dies and determines clock generator frequencies.",
                    "C": "It dynamically compiles high-level source code into bytecode during runtime execution.",
                    "D": "It allocates virtual IP addresses and manages local area network routing for processor sockets."
                }
                expl = "The ISA is the formal specification defining machine instructions, general-purpose registers, addressing modes, and data formats exposed to software."
            else:
                text = "During the instruction execution cycle of a CPU, what is the specific role of the Program Counter (PC)?"
                opts = {
                    "A": "It holds the memory address of the next instruction to be fetched from memory.",
                    "B": "It temporarily stores the arithmetic result produced by the Floating Point Unit.",
                    "C": "It counts the total number of physical transistors operating in the processor core.",
                    "D": "It records the clock cycles consumed by idle background operating system threads."
                }
                expl = "The Program Counter (PC) is a dedicated CPU register that holds the memory address of the next instruction to be fetched and executed."
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": None}

        elif tier == "conceptual":
            text = "How does a Reduced Instruction Set Computer (RISC) architecture differ fundamentally from a Complex Instruction Set Computer (CISC)?"
            opts = {
                "A": "RISC prioritizes simple, single-cycle fixed-length instructions with load-store memory access, whereas CISC provides variable-length instructions capable of direct memory operations.",
                "B": "RISC eliminates the use of general-purpose CPU registers, relying exclusively on stack-based operand evaluation.",
                "C": "CISC architectures cannot be pipelined or executed on superscalar microprocessor cores.",
                "D": "RISC processors execute high-level programming language statements directly in silicon without binary machine decoding."
            }
            expl = "RISC architectures use uniform instruction formats and load-store designs to facilitate streamlined pipelined execution."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Why does the fixed-length instruction format of RISC simplify high-performance pipelined execution?",
                    "options": {
                        "A": "Fixed-length instructions can be decoded and fetched in constant time, allowing predictable pipeline stage synchronization.",
                        "B": "Fixed-length instructions eliminate all memory hierarchy access overhead in cache architectures.",
                        "C": "Fixed-length instructions guarantee that branches never incur speculative misprediction penalties.",
                        "D": "Fixed-length instructions allow arithmetic logic units to operate without clock signal distribution."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

        else: # application
            text = "A computer program executes 10^9 instructions on a 2.5 GHz processor with an average Cycles Per Instruction (CPI) of 1.6. What is the total CPU execution time?"
            opts = {
                "A": "0.64 seconds, calculated as (10^9 * 1.6) / (2.5 * 10^9 s^-1).",
                "B": "1.56 seconds, calculated as (2.5 * 10^9) / (10^9 * 1.6).",
                "C": "4.00 seconds, calculated as (10^9 * 2.5) / 1.6.",
                "D": "0.25 seconds, calculated as 10^9 / (2.5 * 10^9 * 1.6)."
            }
            expl = "According to the CPU performance equation, CPU Time = (Instruction Count * CPI) / Clock Frequency = (10^9 * 1.6) / (2.5 * 10^9) = 0.64 seconds."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Why does increasing CPU clock frequency not guarantee a proportional decrease in execution time across all workloads?",
                    "options": {
                        "A": "Because memory access latency and cache misses do not scale with CPU clock speed, increasing the effective CPI.",
                        "B": "Because faster clock speeds decrease the total number of machine instructions in the program binary.",
                        "C": "Because the operating system scheduler disables superscalar execution when clock speeds exceed 2 GHz.",
                        "D": "Because arithmetic logic units can only process immediate integer constants at lower frequencies."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

    # 2. Instruction Pipelining & Pipeline Hazard Resolution
    elif "pipelining" in c_low or "hazard" in c_low or "pipeline" in c_low:
        if tier == "basic":
            if pattern_idx % 2 == 0:
                text = "In a classical 5-stage RISC instruction pipeline, which sequence represents the correct chronological order of stages?"
                opts = {
                    "A": "Instruction Fetch (IF) -> Instruction Decode (ID) -> Execute (EX) -> Memory Access (MEM) -> Write Back (WB).",
                    "B": "Instruction Decode (ID) -> Instruction Fetch (IF) -> Write Back (WB) -> Memory Access (MEM) -> Execute (EX).",
                    "C": "Instruction Fetch (IF) -> Memory Access (MEM) -> Instruction Decode (ID) -> Execute (EX) -> Write Back (WB).",
                    "D": "Execute (EX) -> Instruction Fetch (IF) -> Instruction Decode (ID) -> Memory Access (MEM) -> Write Back (WB)."
                }
                expl = "The classical 5-stage RISC pipeline executes in the strict sequence IF, ID, EX, MEM, and WB."
            else:
                text = "Which condition causes a Read-After-Write (RAW) data hazard in a pipelined processor?"
                opts = {
                    "A": "An instruction attempts to read a register operand before a preceding instruction has written its updated value to that register.",
                    "B": "Two instructions simultaneously attempt to access the same physical cache line in main memory.",
                    "C": "A branch instruction is executed before the instruction cache has loaded the subsequent instruction block.",
                    "D": "An instruction writes to a register before a previous instruction has finished reading from that same register."
                }
                expl = "A RAW hazard occurs when instruction j tries to read an operand before instruction i writes it, creating a true data dependency."
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": None}

        elif tier == "conceptual":
            text = "How does data forwarding (operand bypassing) resolve Read-After-Write (RAW) data hazards in an instruction pipeline without inserting stall bubbles?"
            opts = {
                "A": "It routes the computation result directly from the ALU or MEM output latches back to the ALU input latches of the dependent instruction.",
                "B": "It re-executes the dependent instruction from the beginning of the program using speculative execution.",
                "C": "It dynamically converts the dependent instruction into a non-blocking no-operation (NOP) directive.",
                "D": "It stalls the entire processor clock until all subsequent instructions have retired from the pipeline."
            }
            expl = "Data forwarding intercepts the computed result from inter-stage pipeline registers before it is written to the register file."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Under what specific circumstance can data forwarding NOT completely eliminate a pipeline stall cycle?",
                    "options": {
                        "A": "In a Load-Use hazard, where the required data is not available from memory until the end of the MEM stage.",
                        "B": "When two consecutive instructions both perform arithmetic additions on immediate integer values.",
                        "C": "When the processor executes a sequence of unconditional jump instructions with branch prediction.",
                        "D": "Whenever the instruction cache achieves a 100% hit rate during instruction fetch."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

        else: # application
            text = "A 5-stage pipeline encounters a conditional branch instruction resolved at the end of the EX stage (stage 3). If branch prediction is not used and the branch is taken, how many stall/flush cycles are incurred?"
            opts = {
                "A": "2 stall cycles, corresponding to the two instructions fetched into IF and ID before the branch resolution.",
                "B": "5 stall cycles, requiring the entire pipeline to completely empty and reboot.",
                "C": "0 stall cycles, because hardware pipelines evaluate branch targets in parallel with instruction fetch.",
                "D": "4 stall cycles, because all stages except Write Back must be re-initialized."
            }
            expl = "Because the branch target is determined in stage 3 (EX), the two instructions fetched in stages 1 (IF) and 2 (ID) must be flushed, creating a 2-cycle penalty."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Why does dynamic branch prediction with a Branch Target Buffer (BTB) improve pipeline throughput?",
                    "options": {
                        "A": "It predicts the branch direction and target in the IF stage, avoiding pipeline flush bubbles when the prediction is correct.",
                        "B": "It converts all conditional branch instructions into sequential ALU add operations.",
                        "C": "It prevents data cache misses by prefetching branch targets directly into CPU registers.",
                        "D": "It eliminates the need for execution units to evaluate comparison operands."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

    # 3. Memory Hierarchy, Cache Locality & Cache Organization
    elif "cache" in c_low or "memory hierarchy" in c_low or "locality" in c_low:
        if tier == "basic":
            if pattern_idx % 2 == 0:
                text = "What is the distinction between temporal locality and spatial locality in computer memory access patterns?"
                opts = {
                    "A": "Temporal locality refers to re-accessing the same memory address soon; spatial locality refers to accessing memory addresses physically proximate to recently accessed addresses.",
                    "B": "Temporal locality refers to accessing contiguous memory addresses; spatial locality refers to accessing cache blocks across different clock cycles.",
                    "C": "Temporal locality applies only to virtual disk swap files; spatial locality applies strictly to CPU register files.",
                    "D": "Temporal locality dictates instruction cache replacement; spatial locality dictates data bus arbitration protocols."
                }
                expl = "Temporal locality reflects reuse of specific items in a short time; spatial locality reflects access to adjacent items."
            else:
                text = "Which class of cache miss occurs upon the very first access to a memory block, regardless of cache size or associativity?"
                opts = {
                    "A": "Compulsory miss (cold miss).",
                    "B": "Conflict miss (collision miss).",
                    "C": "Capacity miss.",
                    "D": "Coherence miss."
                }
                expl = "Compulsory (cold) misses occur on the initial access to a block that has never been loaded into the cache."
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": None}

        elif tier == "conceptual":
            text = "How does increasing cache associativity (e.g. from direct-mapped to 4-way set-associative) affect cache performance and cycle time?"
            opts = {
                "A": "It significantly reduces conflict misses by providing multiple set slots, but may slightly increase hit latency due to multiplexer and tag comparison overhead.",
                "B": "It completely eliminates compulsory misses while reducing the hardware cost of tag comparator circuits.",
                "C": "It doubles memory bus bandwidth but eliminates the benefits of spatial locality across sequential reads.",
                "D": "It restricts the cache to storing only read-only instruction blocks rather than modifiable data blocks."
            }
            expl = "Higher associativity reduces conflict misses by allowing multiple locations per set, at the cost of additional comparison logic."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Why does a direct-mapped cache suffer from higher conflict misses when accessing memory addresses separated by the cache stride?",
                    "options": {
                        "A": "Because all addresses with the same index bits map to the exact same single cache line, causing repeated mutual evictions.",
                        "B": "Because direct-mapped caches lack write-back buffers and cannot communicate with main memory.",
                        "C": "Because direct-mapped caches require variable-length instruction decoders to resolve tag conflicts.",
                        "D": "Because direct-mapped caches execute replacement policies based on least frequently used algorithms."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

        else: # application
            text = "A processor has an L1 cache hit time of 1 ns, a cache miss rate of 4%, and a main memory miss penalty of 50 ns. What is the Average Memory Access Time (AMAT)?"
            opts = {
                "A": "3.0 ns, computed as AMAT = 1 ns + (0.04 * 50 ns) = 1 + 2.0 = 3.0 ns.",
                "B": "51.0 ns, computed as 1 ns + 50 ns.",
                "C": "2.0 ns, computed as 0.04 * 50 ns.",
                "D": "0.2 ns, computed as 1 ns * 0.04 * 50 ns."
            }
            expl = "AMAT = Hit Time + (Miss Rate * Miss Penalty) = 1 ns + (0.04 * 50 ns) = 1 ns + 2 ns = 3.0 ns."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Why is adding an L2 cache between L1 and main memory effective at reducing the overall memory stall penalty?",
                    "options": {
                        "A": "Because the L2 cache captures a substantial portion of L1 misses with a much lower access latency than main DRAM.",
                        "B": "Because an L2 cache eliminates the need for virtual memory address translation.",
                        "C": "Because an L2 cache forces all instruction and data references to use spatial locality exclusively.",
                        "D": "Because an L2 cache decreases the clock frequency of the processor core to match memory bus speed."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

    # 4. Virtual Memory, Page Tables & Translation Lookaside Buffers (TLB)
    else:
        if tier == "basic":
            if pattern_idx % 2 == 0:
                text = "What is the primary function of a Translation Lookaside Buffer (TLB) in virtual memory architectures?"
                opts = {
                    "A": "It is a fast hardware cache that stores recent virtual-to-physical address translations to accelerate memory access.",
                    "B": "It acts as a secondary hard drive partition used to hold dormant operating system kernel processes.",
                    "C": "It encrypts virtual memory pages before writing them to the dynamic random-access memory (DRAM) bus.",
                    "D": "It translates high-level assembly mnemonic instructions into microcode control signals."
                }
                expl = "The TLB caches recent page table translations, avoiding memory table walks on virtual address translation hits."
            else:
                text = "What hardware/software event occurs when a CPU attempts to access a valid virtual memory page that is not currently resident in physical RAM?"
                opts = {
                    "A": "A Page Fault exception is raised, transferring execution to the operating system kernel to load the page from secondary storage.",
                    "B": "The processor immediately halts execution and enters permanent hardware shutdown.",
                    "C": "The memory controller automatically overwrites the kernel page table with zeroed data.",
                    "D": "The TLB switches to direct-mapped mode and retries the instruction indefinitely."
                }
                expl = "A page fault triggers an OS trap, pausing the process while the requested page is retrieved from disk into physical memory."
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": None}

        elif tier == "conceptual":
            text = "Why do modern operating systems employ multi-level (hierarchical) page tables instead of a single large linear page table for 64-bit address spaces?"
            opts = {
                "A": "Multi-level page tables allow unallocated regions of the vast virtual address space to be omitted, dramatically saving physical memory.",
                "B": "Multi-level page tables eliminate the need for address translation hardware and Translation Lookaside Buffers.",
                "C": "Multi-level page tables reduce the number of memory accesses required to translate a virtual address from three to zero.",
                "D": "Multi-level page tables ensure that virtual page sizes match the size of CPU general-purpose registers."
            }
            expl = "Hierarchical page tables allocate table pages only for memory regions that are actively mapped, saving immense amounts of RAM."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Why does a TLB miss typically have a much lower performance penalty than a page fault?",
                    "options": {
                        "A": "A TLB miss only requires walking page table structures in physical RAM (hundreds of cycles), whereas a page fault requires disk/SSD I/O swapping (millions of cycles).",
                        "B": "A TLB miss is handled entirely inside the ALU, whereas a page fault requires flushing processor registers.",
                        "C": "A TLB miss does not pause instruction execution, whereas a page fault reboots the CPU microcode.",
                        "D": "A TLB miss uses hardware branch predictors to guess the physical address without memory lookup."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

        else: # application
            text = "A server running a memory-intensive data processing workload experiences near-100% disk I/O utilization and severe throughput collapse, with CPU utilization dropping below 10%. What architectural phenomenon is occurring?"
            opts = {
                "A": "Thrashing, caused by the active working set exceeding physical RAM capacity, leading to continuous page fault swapping.",
                "B": "A structural pipeline hazard in the floating-point multiplier causing instruction stalls.",
                "C": "A false sharing cache coherence storm between symmetric multiprocessing CPU cores.",
                "D": "A cold compulsory cache miss storm in the L1 instruction cache."
            }
            expl = "Thrashing occurs when memory demand exceeds physical RAM, forcing the operating system to continuously swap pages to and from disk."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "What is the most effective architectural remediation to resolve memory thrashing on a server?",
                    "options": {
                        "A": "Increase physical RAM capacity or reduce the active working set size of running processes.",
                        "B": "Increase the CPU clock frequency to process disk swapping interrupts faster.",
                        "C": "Disable data forwarding in the processor microarchitecture pipeline.",
                        "D": "Reduce L1 cache associativity from 8-way to direct-mapped."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}
