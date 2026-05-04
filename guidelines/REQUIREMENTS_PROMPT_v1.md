Role: You are a Senior Software Requirements Engineer and Academic Technical Writer. Your task is to formalize, structure, and expand upon a set of raw project requirements for a university-level Generative Software Engineering project.

Context: The project requires building a configurable game engine for the board game Blokus. The implementation must follow strict academic and software engineering guidelines. The project is split into two milestones to explicitly simulate a requirements evolution case study, moving from a standard four-player baseline to a two-player configuration.

Task: Transform the raw input data below into a formal Software Requirements Specification document. You must categorize the requirements into Functional Requirements, Non-Functional Requirements, System Constraints, and clearly defined Milestones. Maintain a highly professional, rigorous, and academic tone throughout the document.

Specific Deliverables Required in the Output:

    Core Engine Specifications: Detail the functional requirements for a configurable engine supporting both Blokus Classic and Blokus Duo.

    Interface and State Management: Define the requirements for the minimal Command Line Interface, JSON state loading mechanisms, move validation logic, move application processes, and state serialization.

    Player Archetypes: Specify the implementation details for human players and simple automated computer players.

    Testing and Evaluation: Specify the automated test suite parameters, the evaluation harness, and any advanced evaluation techniques applicable to the system.

    Milestone 1 (Classic Baseline): Clearly outline the deliverables for the four-player classic mode. This includes legality checkers, move application, serialization, and core rule tests.

    Milestone 2 (Change Request): Formalize the transition to Blokus Duo as a configuration change. Note the two-player constraint, specific board dimensions, and unique starting corners. Detail how the tests and evaluation harness must be updated.

    Academic Reporting Constraints: Define the requirements for the final project report. Focus specifically on the evidence-based analysis of applied guidelines, the strict LLM usage disclosure (detailing tools used, application areas, and output validation), and the requirements evolution case study analyzing the friction of implementing Milestone 2.

    Infrastructure: Detail the repository requirements, including reproducible scripts for installation, testing, and execution via a build management tool like Maven or uv.

Exclusions: Explicitly document that heavy graphical user interfaces, strong AI opponents, and online multiplayer features are strictly out of scope and must not be implemented.

Raw Input Data to Formalize:
Requirements
Project
■ Engine library that implements Blokus Classic and Blokus
Duo →game is configurable
■ CLI/minimal application
■ load a state from JSON, validate a move, apply a move, list 
legal moves, print/serialize the resulting state etc.
■ human and computer (simple) players
■ play the game (i.e., implement the rule books)
■ Evaluation harness
■ automated test suite, and (optional) other means of 
checks/tests incl. advanced evaluation techniques (where 
applicable)
■ Final implementation + repository with reproducible scripts 
(install, test, run) → build management tool (e.g., Maven for 
Java, uv for Python…)
■ Project report: evidence-based analysis of applying guidelines, 
including counterexamples and refinements
■ AI usage disclosure: tools/models used, where used, and how 
outputs were validated
■ No formal requirements for a heavy graphical UI, strong AI 
player (optional extension only), or for online multiplayer
Milestones
■ Milestone 1 (Classic baseline)
■ Fully functioning Blokus Classic rules (4 players) 
including
■ legality checker,
■ move application,
■ serialization,
■ tests for key rules and transforms
■ Milestone 2 (“Change request”)
■ Extend the same engine to support Blokus Duo via 
configuration
■ 2 players,
■ Duo-specific board/start-corners
■ Update tests and evaluation harness to cover both modes
■ In your report, treat this as a requirements-evolution case 
study: what broke, what the LLM suggested, what actually 
worked